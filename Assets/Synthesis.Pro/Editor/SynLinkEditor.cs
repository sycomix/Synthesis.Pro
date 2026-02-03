using UnityEngine;
using UnityEditor;
using System;
using System.Net;
using System.Text;
using System.Threading;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;

namespace Synthesis.Editor
{
    /// <summary>
    /// SynLink Editor - HTTP Server for MCP-Unity Communication
    /// Starts automatically when Unity Editor loads - NO GameObject needed!
    /// </summary>
    [InitializeOnLoad]
    public static class SynLinkEditor
    {
        private static HttpListener httpListener;
        private static Thread listenerThread;
        private static Queue<Action> mainThreadQueue = new Queue<Action>();
        private static bool isRunning = false;
        private static int httpPort = 9765;
        private static bool logRequests = true;
        
        // Public API for checking connection status
        public static bool IsConnected() => isRunning && httpListener != null && httpListener.IsListening;

        // Static constructor - called when Unity Editor loads (and after each recompile)
        static SynLinkEditor()
        {
            Debug.Log("[SynLink] 🚀 Editor HTTP Server initializing...");
            
            // Force cleanup of any lingering instances from previous domain reload
            StopHTTPServer();
            
            EditorApplication.update += Update;
            
            // Delay startup slightly to allow port release
            EditorApplication.delayCall += () =>
            {
                System.Threading.Thread.Sleep(500); // Give OS time to release the port
                StartHTTPServer();
            };
        }

        private static void Update()
        {
            // Process main thread queue
            lock (mainThreadQueue)
            {
                while (mainThreadQueue.Count > 0)
                {
                    try
                    {
                        mainThreadQueue.Dequeue()?.Invoke();
                    }
                    catch (Exception e)
                    {
                        Debug.LogError($"[SynLink] Error in main thread action: {e.Message}");
                    }
                }
            }
        }

        private static int startupRetries = 0;
        private const int MAX_RETRIES = 5; // Increased for TIME_WAIT clearance
        
        /// <summary>
        /// Check if a port is available for binding
        /// </summary>
        private static bool IsPortAvailable(int port)
        {
            System.Net.Sockets.TcpListener listener = null;
            try
            {
                listener = new System.Net.Sockets.TcpListener(IPAddress.Loopback, port);
                listener.Start();
                listener.Stop();
                return true;
            }
            catch
            {
                return false;
            }
            finally
            {
                if (listener != null)
                {
                    try { listener.Stop(); } catch { }
                }
            }
        }
        
        /// <summary>
        /// Try to find what process is using a port (Windows only)
        /// </summary>
        private static string GetPortOwner(int port)
        {
            try
            {
                var startInfo = new System.Diagnostics.ProcessStartInfo
                {
                    FileName = "netstat",
                    Arguments = "-ano",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    CreateNoWindow = true
                };
                
                using (var process = System.Diagnostics.Process.Start(startInfo))
                {
                    string output = process.StandardOutput.ReadToEnd();
                    foreach (string line in output.Split('\n'))
                    {
                        if (line.Contains($":{port} ") || line.Contains($":{port}\t"))
                        {
                            // Extract PID from the last column
                            string[] parts = line.Split(new char[] { ' ', '\t' }, StringSplitOptions.RemoveEmptyEntries);
                            if (parts.Length > 0 && int.TryParse(parts[parts.Length - 1], out int pid))
                            {
                                try
                                {
                                    var ownerProcess = System.Diagnostics.Process.GetProcessById(pid);
                                    return $"{ownerProcess.ProcessName} (PID {pid})";
                                }
                                catch
                                {
                                    return $"PID {pid}";
                                }
                            }
                        }
                    }
                }
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[SynLink] Could not determine process using port {httpPort}: {e.Message}");
            }
            return "unknown process";
        }
        
        public static void StartHTTPServer()
        {
            if (isRunning)
            {
                Debug.LogWarning("[SynLink] HTTP Server already running!");
                return;
            }

            // Pre-check if port is available
            if (!IsPortAvailable(httpPort))
            {
                string portOwner = GetPortOwner(httpPort);
                
                if (startupRetries < MAX_RETRIES)
                {
                    Debug.LogWarning($"[SynLink] Port {httpPort} is busy (used by {portOwner}), will retry in 5 seconds... (Attempt {startupRetries + 1}/{MAX_RETRIES})");
                    startupRetries++;
                    
                    EditorApplication.delayCall += () =>
                    {
                        System.Threading.Thread.Sleep(5000);
                        StartHTTPServer();
                    };
                    return;
                }
                else
                {
                    Debug.LogError($"[SynLink] Port {httpPort} is not available after {MAX_RETRIES} attempts. Used by: {portOwner}");
                    Debug.LogError($"[SynLink] Try closing the other process or restart Unity completely.");
                    startupRetries = 0;
                    return;
                }
            }

            try
            {
                httpListener = new HttpListener();
                httpListener.Prefixes.Add($"http://localhost:{httpPort}/");
                httpListener.Start();
                isRunning = true;

                listenerThread = new Thread(ListenForRequests);
                listenerThread.IsBackground = true;
                listenerThread.Start();

                Debug.Log($"[SynLink] 🔗 HTTP Server started on port {httpPort}");
                Debug.Log("[SynLink] ✨ Ready for MCP commands! (No GameObject needed!)");
                
                // Reset retry counter on success
                startupRetries = 0;
            }
            catch (Exception e)
            {
                // Suppress errors if server is already running (common during domain reloads)
                if (e is System.Net.HttpListenerException || e.Message.Contains("normally permitted"))
                {
                    // Silently ignore - server likely already running from previous session
                }
                else
                {
                    // Log unexpected errors as warnings instead of errors
                    Debug.LogWarning($"[SynLink] Could not start HTTP server: {e.GetType().Name} - {e.Message}");
                }
                isRunning = false;
                startupRetries = 0;
            }
        }

        public static void StopHTTPServer()
        {
            if (!isRunning) return;

            try
            {
                isRunning = false;
                
                if (httpListener != null)
                {
                    try
                    {
                        httpListener.Stop();
                        httpListener.Close();
                        ((IDisposable)httpListener).Dispose();
                    }
                    catch { /* Ignore errors during shutdown */ }
                    finally
                    {
                        httpListener = null;
                    }
                }
                
                if (listenerThread != null && listenerThread.IsAlive)
                {
                    // Wait for thread to exit gracefully (increased timeout for safety)
                    if (!listenerThread.Join(3000))
                    {
                        Debug.LogWarning("[SynLink] Listener thread did not exit within timeout - will exit on next iteration");
                    }
                    listenerThread = null;
                }
                
                Debug.Log("[SynLink] ✓ HTTP Server stopped");
            }
            catch (Exception e)
            {
                Debug.LogError($"[SynLink] Error stopping HTTP server: {e.Message}");
            }
        }

        private static void ListenForRequests()
        {
            while (isRunning && httpListener != null && httpListener.IsListening)
            {
                try
                {
                    var context = httpListener.GetContext();
                    ThreadPool.QueueUserWorkItem(_ => ProcessRequest(context));
                }
                catch (ThreadAbortException)
                {
                    // Unity is recompiling - exit gracefully
                    Debug.Log("[SynLink] Thread aborted (domain reload)");
                    break;
                }
                catch (Exception e)
                {
                    if (isRunning)
                    {
                        Debug.LogError($"[SynLink] Listener error: {e.Message}");
                    }
                }
            }
        }

        private static void ProcessRequest(HttpListenerContext context)
        {
            try
            {
                // Handle CORS preflight (OPTIONS)
                if (context.Request.HttpMethod == "OPTIONS")
                {
                    context.Response.StatusCode = 200;
                    context.Response.Headers.Add("Access-Control-Allow-Origin", "*");
                    context.Response.Headers.Add("Access-Control-Allow-Methods", "POST, OPTIONS");
                    context.Response.Headers.Add("Access-Control-Allow-Headers", "Content-Type");
                    context.Response.Close();
                    return;
                }
                
                if (context.Request.HttpMethod != "POST")
                {
                    SendResponse(context, 405, new { error = "Only POST requests are supported" });
                    return;
                }

                string requestBody;
                using (var reader = new System.IO.StreamReader(context.Request.InputStream, context.Request.ContentEncoding))
                {
                    requestBody = reader.ReadToEnd();
                }

                if (logRequests)
                {
                    Debug.Log($"[SynLink] 📨 Request: {requestBody}");
                }

                var command = JsonConvert.DeserializeObject<SynCommand>(requestBody);

                // Queue command for main thread execution
                object result = null;
                Exception error = null;
                var resetEvent = new System.Threading.ManualResetEvent(false);

                lock (mainThreadQueue)
                {
                    mainThreadQueue.Enqueue(() =>
                    {
                        try
                        {
                            result = ExecuteCommand(command);
                        }
                        catch (Exception e)
                        {
                            error = e;
                        }
                        finally
                        {
                            resetEvent.Set();
                        }
                    });
                }

                // Wait for main thread to execute
                resetEvent.WaitOne(5000);

                if (error != null)
                {
                    SendResponse(context, 500, new { error = error.Message });
                }
                else
                {
                    SendResponse(context, 200, result);
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[SynLink] Request processing error: {e.Message}");
                SendResponse(context, 500, new { error = e.Message });
            }
        }

        private static object ExecuteCommand(SynCommand cmd)
        {
            var commandName = cmd.GetCommand();
            var parameters = cmd.GetParameters();
            
            if (logRequests)
            {
                Debug.Log($"[SynLink] ⚡ Executing: {commandName}");
            }

            try
            {
                object resultData = null;
                string resultMessage = "";
                
                // Normalize command name (case-insensitive)
                var normalizedCommand = commandName.ToLower();
                
                switch (normalizedCommand)
                {
                    case "ping":
                        resultMessage = "Pong! 🔗";
                        break;

                    case "getsceneinfo":
                        resultData = GetSceneInfo();
                        resultMessage = "Scene info retrieved";
                        break;

                    case "findgameobject":
                        var objName = parameters.ContainsKey("name") ? parameters["name"]?.ToString() : cmd.objectName;
                        resultData = FindGameObject(objName);
                        resultMessage = $"Found GameObject: {objName}";
                        break;

                    case "getcomponent":
                        var obj1 = parameters.ContainsKey("object") ? parameters["object"]?.ToString() : cmd.objectName;
                        var comp1 = parameters.ContainsKey("component") ? parameters["component"]?.ToString() : cmd.component;
                        resultData = GetComponent(obj1, comp1);
                        resultMessage = $"Component {comp1} retrieved from {obj1}";
                        break;

                    case "getcomponentvalue":
                        var obj2 = parameters.ContainsKey("object") ? parameters["object"]?.ToString() : cmd.objectName;
                        var comp2 = parameters.ContainsKey("component") ? parameters["component"]?.ToString() : cmd.component;
                        var field2 = parameters.ContainsKey("field") ? parameters["field"]?.ToString() : cmd.field;
                        resultData = GetComponentValue(obj2, comp2, field2);
                        resultMessage = $"Value of {field2} retrieved";
                        break;

                    case "setcomponentvalue":
                        var obj3 = parameters.ContainsKey("object") ? parameters["object"]?.ToString() : cmd.objectName;
                        var comp3 = parameters.ContainsKey("component") ? parameters["component"]?.ToString() : cmd.component;
                        var field3 = parameters.ContainsKey("field") ? parameters["field"]?.ToString() : cmd.field;
                        var value3 = parameters.ContainsKey("value") ? parameters["value"] : cmd.value;
                        resultData = SetComponentValue(obj3, comp3, field3, value3);
                        resultMessage = $"Set {obj3}.{comp3}.{field3} = {value3}";
                        break;

                    case "gethierarchy":
                        resultData = GetHierarchy();
                        resultMessage = "Hierarchy retrieved";
                        break;
                    
                    case "getchildren":
                        var parentName = parameters.ContainsKey("object") ? parameters["object"]?.ToString() : cmd.objectName;
                        resultData = GetChildren(parentName);
                        resultMessage = $"Children of {parentName} retrieved";
                        break;

                    case "log":
                        var message = parameters.ContainsKey("message") ? parameters["message"]?.ToString() :
                                     cmd.args?["message"]?.ToString() ?? "";
                        Debug.Log($"[MCP] {message}");
                        resultMessage = "Message logged";
                        break;

                    default:
                        return new { success = false, message = $"Unknown command: {commandName}", error = $"Unknown command: {commandName}" };
                }
                
                return new { success = true, message = resultMessage, data = resultData };
            }
            catch (Exception e)
            {
                Debug.LogError($"[SynLink] Command execution error: {e.Message}");
                return new { success = false, message = "Command failed", error = e.Message };
            }
        }

        private static object GetSceneInfo()
        {
            var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            var rootObjects = scene.GetRootGameObjects();
            
            return new
            {
                sceneName = scene.name,
                scenePath = scene.path,
                rootObjectCount = rootObjects.Length,
                rootObjects = rootObjects.Select(go => go.name).ToArray()
            };
        }

        private static object FindGameObject(string name)
        {
            var go = GameObject.Find(name);
            if (go == null)
            {
                throw new Exception($"GameObject '{name}' not found");
            }

            var components = go.GetComponents<Component>();
            return new
            {
                name = go.name,
                active = go.activeInHierarchy,
                tag = go.tag,
                layer = go.layer,
                components = components.Select(c => c.GetType().Name).ToArray()
            };
        }

        private static object GetComponent(string objectName, string componentName)
        {
            var go = GameObject.Find(objectName);
            if (go == null)
            {
                throw new Exception($"GameObject '{objectName}' not found");
            }

            var component = go.GetComponent(componentName);
            if (component == null)
            {
                throw new Exception($"Component '{componentName}' not found on '{objectName}'");
            }

            return new
            {
                componentType = component.GetType().Name,
                fields = GetComponentFields(component)
            };
        }

        private static object GetComponentValue(string objectName, string componentName, string fieldName)
        {
            var go = GameObject.Find(objectName);
            if (go == null)
            {
                throw new Exception($"GameObject '{objectName}' not found");
            }

            var component = go.GetComponent(componentName);
            if (component == null)
            {
                throw new Exception($"Component '{componentName}' not found");
            }

            var field = component.GetType().GetField(fieldName, 
                System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            
            var property = component.GetType().GetProperty(fieldName,
                System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

            object value = null;
            if (field != null)
            {
                value = field.GetValue(component);
            }
            else if (property != null)
            {
                value = property.GetValue(component);
            }
            else
            {
                throw new Exception($"Field/Property '{fieldName}' not found");
            }

            return new
            {
                value = value,
                type = value?.GetType().Name ?? "null"
            };
        }

        private static object SetComponentValue(string objectName, string componentName, string fieldName, object value)
        {
            var go = GameObject.Find(objectName);
            if (go == null)
            {
                throw new Exception($"GameObject '{objectName}' not found");
            }

            var component = go.GetComponent(componentName);
            if (component == null)
            {
                throw new Exception($"Component '{componentName}' not found");
            }

            var field = component.GetType().GetField(fieldName,
                System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

            var property = component.GetType().GetProperty(fieldName,
                System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);

            if (field != null)
            {
                var convertedValue = ConvertValue(value, field.FieldType);
                field.SetValue(component, convertedValue);
                EditorUtility.SetDirty(component);
            }
            else if (property != null && property.CanWrite)
            {
                var convertedValue = ConvertValue(value, property.PropertyType);
                property.SetValue(component, convertedValue);
                EditorUtility.SetDirty(component);
            }
            else
            {
                throw new Exception($"Field/Property '{fieldName}' not found or not writable");
            }

            return new { oldValue = value, newValue = value, fieldName = fieldName };
        }

        private static object GetHierarchy()
        {
            var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            var rootObjects = scene.GetRootGameObjects();
            
            var hierarchy = new List<object>();
            foreach (var root in rootObjects)
            {
                hierarchy.Add(BuildHierarchyNode(root.transform));
            }

            return new
            {
                sceneName = scene.name,
                hierarchy = hierarchy
            };
        }

        private static object GetChildren(string objectName)
        {
            var go = GameObject.Find(objectName);
            if (go == null)
            {
                throw new Exception($"GameObject '{objectName}' not found");
            }

            var children = new List<object>();
            for (int i = 0; i < go.transform.childCount; i++)
            {
                var child = go.transform.GetChild(i);
                children.Add(new
                {
                    name = child.name,
                    active = child.gameObject.activeInHierarchy,
                    childCount = child.childCount
                });
            }

            return new
            {
                parentName = objectName,
                childCount = children.Count,
                children = children
            };
        }

        private static object BuildHierarchyNode(Transform transform)
        {
            var children = new List<object>();
            for (int i = 0; i < transform.childCount; i++)
            {
                children.Add(BuildHierarchyNode(transform.GetChild(i)));
            }

            var components = transform.GetComponents<Component>();
            return new
            {
                name = transform.name,
                active = transform.gameObject.activeInHierarchy,
                components = components.Select(c => c.GetType().Name).ToArray(),
                childCount = children.Count,
                children = children
            };
        }

        private static Dictionary<string, object> GetComponentFields(Component component)
        {
            var fields = new Dictionary<string, object>();
            var type = component.GetType();

            foreach (var field in type.GetFields(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance))
            {
                try
                {
                    fields[field.Name] = field.GetValue(component);
                }
                catch (System.Exception e)
                {
                    // Some fields may not be accessible - log and skip
                    Debug.LogWarning($"[SynLink] Could not read field '{field.Name}' on {type.Name}: {e.Message}");
                    fields[field.Name] = "<error>";
                }
            }

            foreach (var prop in type.GetProperties(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance))
            {
                try
                {
                    if (prop.CanRead)
                    {
                        fields[prop.Name] = prop.GetValue(component);
                    }
                }
                catch (System.Exception e)
                {
                    // Some properties may throw exceptions when accessed - log and skip
                    Debug.LogWarning($"[SynLink] Could not read property '{prop.Name}' on {type.Name}: {e.Message}");
                    fields[prop.Name] = "<error>";
                }
            }

            return fields;
        }

        private static object ConvertValue(object value, Type targetType)
        {
            if (value == null) return null;
            if (targetType.IsAssignableFrom(value.GetType())) return value;

            // Handle Vector2, Vector3, etc.
            if (targetType == typeof(Vector2) && value is Newtonsoft.Json.Linq.JObject)
            {
                var jobj = (Newtonsoft.Json.Linq.JObject)value;
                return new Vector2(
                    jobj["x"]?.ToObject<float>() ?? 0,
                    jobj["y"]?.ToObject<float>() ?? 0
                );
            }

            if (targetType == typeof(Vector3) && value is Newtonsoft.Json.Linq.JObject)
            {
                var jobj = (Newtonsoft.Json.Linq.JObject)value;
                return new Vector3(
                    jobj["x"]?.ToObject<float>() ?? 0,
                    jobj["y"]?.ToObject<float>() ?? 0,
                    jobj["z"]?.ToObject<float>() ?? 0
                );
            }

            if (targetType == typeof(Color) && value is Newtonsoft.Json.Linq.JObject)
            {
                var jobj = (Newtonsoft.Json.Linq.JObject)value;
                return new Color(
                    jobj["r"]?.ToObject<float>() ?? 0,
                    jobj["g"]?.ToObject<float>() ?? 0,
                    jobj["b"]?.ToObject<float>() ?? 0,
                    jobj["a"]?.ToObject<float>() ?? 1
                );
            }

            // Default conversion
            return Convert.ChangeType(value, targetType);
        }

        private static void SendResponse(HttpListenerContext context, int statusCode, object data)
        {
            try
            {
                context.Response.StatusCode = statusCode;
                context.Response.ContentType = "application/json";
                context.Response.Headers.Add("Access-Control-Allow-Origin", "*");

                var json = JsonConvert.SerializeObject(data);
                var buffer = Encoding.UTF8.GetBytes(json);

                context.Response.ContentLength64 = buffer.Length;
                context.Response.OutputStream.Write(buffer, 0, buffer.Length);
                context.Response.OutputStream.Close();

                if (logRequests)
                {
                    Debug.Log($"[SynLink] 📤 Response ({statusCode}): {json}");
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[SynLink] Error sending response: {e.Message}");
            }
        }

        [Serializable]
        private class SynCommand
        {
            public string type;  // MCP server format
            public Dictionary<string, object> parameters;  // MCP server format
            
            // Legacy fields for backwards compatibility
            public string command;
            public string objectName;
            public string component;
            public string field;
            public object value;
            public Dictionary<string, object> args;
            
            // Helper to get command name from either format
            public string GetCommand() => !string.IsNullOrEmpty(type) ? type : command;
            
            // Helper to get parameters from either format
            public Dictionary<string, object> GetParameters() => parameters ?? args ?? new Dictionary<string, object>();
        }
    }
}
