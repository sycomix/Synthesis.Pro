using UnityEngine;
using System.IO;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace Synthesis.Bridge
{
    /// <summary>
    /// SynLink - File-based command system for AI-Unity communication
    /// 
    /// How it works:
    /// 1. External tool writes commands to a JSON file
    /// 2. Unity reads and executes commands
    /// 3. Unity writes results back to another JSON file
    /// 4. External tool reads results
    /// 
    /// THIS IS HOW AI GETS EYES AND HANDS IN UNITY! 🤖✨
    /// </summary>
    [DefaultExecutionOrder(-1000)]
    [AddComponentMenu("Synthesis/SynLink (File-based)")]
    public class SynLink : MonoBehaviour
    {
        #region Singleton
        
        private static SynLink instance;
        public static SynLink Instance => instance;
        
        #endregion
        
        #region Settings
        
        [Header("Bridge Settings")]
        [SerializeField] private bool enableBridge = true;
        [SerializeField] private float pollInterval = 0.5f;
        
        [Header("File Paths")]
        [SerializeField] private string commandsFileName = "unity_bridge_commands.json";
        [SerializeField] private string resultsFileName = "unity_bridge_results.json";
        [SerializeField] private string logsFileName = "unity_bridge_logs.txt";
        
        [Header("Persistence")]
        [SerializeField] private UIChangeLog changeLog; // Assign in Inspector for persistent changes
        
        // Knowledge Base removed - not needed for core functionality
        
        private string commandsFilePath;
        private string resultsFilePath;
        private string logsFilePath;
        
        
        #endregion
        
        #region State
        
        private float lastPollTime;
        private int commandsProcessed = 0;
        private Queue<BridgeCommand> commandQueue = new Queue<BridgeCommand>();
        
        #endregion
        
        #region Unity Lifecycle
        
        private void Awake()
        {
            // Singleton
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            instance = this;
            DontDestroyOnLoad(gameObject);
            
            // Setup file paths (in project root for easy access)
            commandsFilePath = Path.Combine(Application.dataPath, "..", commandsFileName);
            resultsFilePath = Path.Combine(Application.dataPath, "..", resultsFileName);
            logsFilePath = Path.Combine(Application.dataPath, "..", logsFileName);
            
            // Initialize files
            InitializeBridge();
            
            
            Log("🌉 Unity Bridge Initialized!");
            Log($"Commands: {commandsFilePath}");
            Log($"Results: {resultsFilePath}");
            Log($"Logs: {logsFilePath}");
        }
        
        private void Update()
        {
            if (!enableBridge)
                return;
            
            // Poll for commands
            if (Time.time - lastPollTime >= pollInterval)
            {
                lastPollTime = Time.time;
                PollForCommands();
            }
            
            // Process queued commands
            ProcessCommandQueue();
        }
        
        private void OnDestroy()
        {
            
            if (instance == this)
            {
                instance = null;
            }
        }
        
        #endregion
        
        #region Bridge Initialization
        
        private void InitializeBridge()
        {
            // Create empty results file
            WriteBridgeResult(new BridgeResult
            {
                success = true,
                message = "Bridge ready",
                timestamp = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
            });
            
            // Create log file
            File.WriteAllText(logsFilePath, $"=== Unity Bridge Logs ===\n{System.DateTime.Now}\n\n");
        }
        
        #endregion
        
        #region Command Processing
        
        private void PollForCommands()
        {
            if (!File.Exists(commandsFilePath))
                return;
            
            try
            {
                string json = File.ReadAllText(commandsFilePath);
                
                if (string.IsNullOrWhiteSpace(json))
                    return;
                
                var commands = JsonConvert.DeserializeObject<BridgeCommandBatch>(json);
                
                if (commands?.commands != null)
                {
                    foreach (var cmd in commands.commands)
                    {
                        commandQueue.Enqueue(cmd);
                    }
                    
                    // Clear the commands file
                    File.WriteAllText(commandsFilePath, "");
                }
            }
            catch (System.Exception ex)
            {
                Log($"❌ Error reading commands: {ex.Message}");
            }
        }
        
        private void ProcessCommandQueue()
        {
            // Process one command per frame to avoid hitches
            if (commandQueue.Count > 0)
            {
                var cmd = commandQueue.Dequeue();
                ExecuteCommand(cmd);
            }
        }
        
        private void ExecuteCommand(BridgeCommand cmd)
        {
            Log($"📥 Executing: {cmd.type} (ID: {cmd.id})");
            
            BridgeResult result = new BridgeResult
            {
                commandId = cmd.id,
                timestamp = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
            };
            
            try
            {
                // Check if this is an extended command (creative AI powers!)
                if (SynLinkExtended.Instance != null && IsExtendedCommand(cmd.type))
                {
                    SynLinkExtended.Instance.ProcessExtendedCommand(cmd);
                    return; // Extended handler processes its own result
                }
                
                switch (cmd.type)
                {
                    case "GetSceneInfo":
                        result = GetSceneInfo(cmd);
                        break;
                    
                    case "FindGameObject":
                        result = FindGameObjectCommand(cmd);
                        break;
                    
                    case "GetComponent":
                        result = GetComponentCommand(cmd);
                        break;
                    
                    case "SetComponentValue":
                        result = SetComponentValueCommand(cmd);
                        break;
                    
                    case "SetPosition":
                        result = SetPositionCommand(cmd);
                        break;
                    
                    case "SetActive":
                        result = SetActiveCommand(cmd);
                        break;
                    
                    case "MoveGameObject":
                        result = MoveGameObjectCommand(cmd);
                        break;
                    
                    case "RecordChange":
                        result = RecordChangeCommand(cmd);
                        break;
                    
                    case "Log":
                        result = LogCommand(cmd);
                        break;
                    
                    case "Ping":
                        result = new BridgeResult
                        {
                            commandId = cmd.id,
                            success = true,
                            message = "Pong! Bridge is alive!",
                            data = new Dictionary<string, object>
                            {
                                { "commandsProcessed", commandsProcessed },
                                { "queueLength", commandQueue.Count },
                                { "time", Time.time }
                            }
                        };
                        break;
                    
                    // Knowledge Base commands removed - not needed for core functionality
                    
                    default:
                        result.success = false;
                        result.message = $"Unknown command type: {cmd.type}";
                        break;
                }
                
                commandsProcessed++;
            }
            catch (System.Exception ex)
            {
                result.success = false;
                result.message = $"Error: {ex.Message}";
                result.error = ex.ToString();
                Log($"❌ Command failed: {ex.Message}");
            }
            
            // Write result
            WriteBridgeResult(result);
        }
        
        private bool IsExtendedCommand(string commandType)
        {
            return commandType == "GenerateImage" ||
                   commandType == "GenerateSound" ||
                   commandType == "Generate3DModel" ||
                   commandType == "GenerateShader" ||
                   commandType == "GenerateScript" ||
                   commandType == "GetCapabilities";
        }
        
        #endregion
        
        #region Command Implementations
        
        private BridgeResult GetSceneInfo(BridgeCommand cmd)
        {
            var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            var rootObjects = scene.GetRootGameObjects();
            
            var sceneInfo = new Dictionary<string, object>
            {
                { "sceneName", scene.name },
                { "scenePath", scene.path },
                { "rootObjectCount", rootObjects.Length },
                { "rootObjects", System.Array.ConvertAll(rootObjects, go => go.name) }
            };
            
            return new BridgeResult
            {
                commandId = cmd.id,
                success = true,
                message = $"Scene: {scene.name}",
                data = sceneInfo
            };
        }
        
        private BridgeResult FindGameObjectCommand(BridgeCommand cmd)
        {
            string name = cmd.parameters?.GetValueOrDefault("name")?.ToString();
            
            if (string.IsNullOrEmpty(name))
            {
                return new BridgeResult
                {
                    commandId = cmd.id,
                    success = false,
                    message = "Missing 'name' parameter"
                };
            }
            
            GameObject go = GameObject.Find(name);
            
            if (go == null)
            {
                return new BridgeResult
                {
                    commandId = cmd.id,
                    success = false,
                    message = $"GameObject '{name}' not found"
                };
            }
            
            var info = new Dictionary<string, object>
            {
                { "name", go.name },
                { "active", go.activeInHierarchy },
                { "position", go.transform.position.ToString() },
                { "components", System.Array.ConvertAll(go.GetComponents<Component>(), c => c.GetType().Name) }
            };
            
            return new BridgeResult
            {
                commandId = cmd.id,
                success = true,
                message = $"Found: {go.name}",
                data = info
            };
        }
        
        private BridgeResult GetComponentCommand(BridgeCommand cmd)
        {
            string objectName = cmd.parameters?.GetValueOrDefault("object")?.ToString();
            string componentType = cmd.parameters?.GetValueOrDefault("component")?.ToString();
            
            GameObject go = GameObject.Find(objectName);
            if (go == null)
            {
                return new BridgeResult
                {
                    commandId = cmd.id,
                    success = false,
                    message = $"GameObject '{objectName}' not found"
                };
            }
            
            Component comp = go.GetComponent(componentType);
            if (comp == null)
            {
                return new BridgeResult
                {
                    commandId = cmd.id,
                    success = false,
                    message = $"Component '{componentType}' not found on '{objectName}'"
                };
            }
            
            // Get component data using reflection
            var componentData = GetComponentData(comp);
            
            return new BridgeResult
            {
                commandId = cmd.id,
                success = true,
                message = $"Component data retrieved",
                data = componentData
            };
        }
        
        private BridgeResult SetComponentValueCommand(BridgeCommand cmd)
        {
            string objectName = cmd.parameters?.GetValueOrDefault("object")?.ToString();
            string componentType = cmd.parameters?.GetValueOrDefault("component")?.ToString();
            string fieldName = cmd.parameters?.GetValueOrDefault("field")?.ToString();
            object value = cmd.parameters?.GetValueOrDefault("value");
            
            GameObject go = GameObject.Find(objectName);
            if (go == null)
            {
                return new BridgeResult
                {
                    commandId = cmd.id,
                    success = false,
                    message = $"GameObject '{objectName}' not found"
                };
            }
            
            Component comp = go.GetComponent(componentType);
            if (comp == null)
            {
                return new BridgeResult
                {
                    commandId = cmd.id,
                    success = false,
                    message = $"Component '{componentType}' not found"
                };
            }
            
            // Use reflection to set value
            var field = comp.GetType().GetField(fieldName, 
                System.Reflection.BindingFlags.Public | 
                System.Reflection.BindingFlags.NonPublic | 
                System.Reflection.BindingFlags.Instance);
            
            if (field != null)
            {
                // Convert value to correct type
                object convertedValue = ConvertValueToType(value, field.FieldType);
                field.SetValue(comp, convertedValue);
                return new BridgeResult
                {
                    commandId = cmd.id,
                    success = true,
                    message = $"Set {fieldName} = {convertedValue}"
                };
            }
            
            // Try property
            var property = comp.GetType().GetProperty(fieldName);
            if (property != null && property.CanWrite)
            {
                // Convert value to correct type
                object convertedValue = ConvertValueToType(value, property.PropertyType);
                property.SetValue(comp, convertedValue);
                return new BridgeResult
                {
                    commandId = cmd.id,
                    success = true,
                    message = $"Set {fieldName} = {convertedValue}"
                };
            }
            
            return new BridgeResult
            {
                commandId = cmd.id,
                success = false,
                message = $"Field/Property '{fieldName}' not found or not writable"
            };
        }
        
        private BridgeResult LogCommand(BridgeCommand cmd)
        {
            string message = cmd.parameters?.GetValueOrDefault("message")?.ToString() ?? "No message";
            Log($"🔔 External: {message}");
            
            return new BridgeResult
            {
                commandId = cmd.id,
                success = true,
                message = "Logged"
            };
        }
        
        private BridgeResult SetPositionCommand(BridgeCommand cmd)
        {
            string objectName = cmd.parameters?.GetValueOrDefault("object")?.ToString();
            object positionValue = cmd.parameters?.GetValueOrDefault("position");
            
            GameObject go = GameObject.Find(objectName);
            if (go == null)
            {
                return new BridgeResult
                {
                    commandId = cmd.id,
                    success = false,
                    message = $"GameObject '{objectName}' not found"
                };
            }
            
            Vector3 position = (Vector3)ConvertValueToType(positionValue, typeof(Vector3));
            go.transform.position = position;
            
            return new BridgeResult
            {
                commandId = cmd.id,
                success = true,
                message = $"Moved '{objectName}' to {position}",
                data = new Dictionary<string, object>
                {
                    { "newPosition", position.ToString() }
                }
            };
        }
        
        private BridgeResult SetActiveCommand(BridgeCommand cmd)
        {
            string objectName = cmd.parameters?.GetValueOrDefault("object")?.ToString();
            bool active = cmd.parameters?.GetValueOrDefault("active")?.ToString() == "true";
            
            GameObject go = GameObject.Find(objectName);
            if (go == null)
            {
                return new BridgeResult
                {
                    commandId = cmd.id,
                    success = false,
                    message = $"GameObject '{objectName}' not found"
                };
            }
            
            go.SetActive(active);
            
            return new BridgeResult
            {
                commandId = cmd.id,
                success = true,
                message = $"Set '{objectName}' active = {active}"
            };
        }
        
        private BridgeResult MoveGameObjectCommand(BridgeCommand cmd)
        {
            string objectName = cmd.parameters?.GetValueOrDefault("object")?.ToString();
            float x = System.Convert.ToSingle(cmd.parameters?.GetValueOrDefault("x") ?? 0);
            float y = System.Convert.ToSingle(cmd.parameters?.GetValueOrDefault("y") ?? 0);
            float z = System.Convert.ToSingle(cmd.parameters?.GetValueOrDefault("z") ?? 0);
            bool recordChange = cmd.parameters?.GetValueOrDefault("record")?.ToString() == "true";
            
            GameObject go = GameObject.Find(objectName);
            if (go == null)
            {
                return new BridgeResult
                {
                    commandId = cmd.id,
                    success = false,
                    message = $"GameObject '{objectName}' not found"
                };
            }
            
            Vector3 oldPos = go.transform.position;
            Vector3 newPos = new Vector3(x, y, z);
            go.transform.position = newPos;
            
            // Optionally record the change for persistence
            if (recordChange && changeLog != null)
            {
                changeLog.RecordPositionChange(GetGameObjectPath(go), newPos);
            }
            
            return new BridgeResult
            {
                commandId = cmd.id,
                success = true,
                message = $"Moved '{objectName}' from {oldPos} to {newPos}",
                data = new Dictionary<string, object>
                {
                    { "oldPosition", oldPos.ToString() },
                    { "newPosition", newPos.ToString() },
                    { "recorded", recordChange }
                }
            };
        }
        
        private BridgeResult RecordChangeCommand(BridgeCommand cmd)
        {
            if (changeLog == null)
            {
                return new BridgeResult
                {
                    commandId = cmd.id,
                    success = false,
                    message = "UIChangeLog not assigned to SynLink"
                };
            }

            string objectName = cmd.parameters?.GetValueOrDefault("object")?.ToString();
            string componentType = cmd.parameters?.GetValueOrDefault("component")?.ToString();
            string fieldName = cmd.parameters?.GetValueOrDefault("field")?.ToString();
            object value = cmd.parameters?.GetValueOrDefault("value");

            GameObject go = GameObject.Find(objectName);
            if (go == null)
            {
                return new BridgeResult
                {
                    commandId = cmd.id,
                    success = false,
                    message = $"GameObject '{objectName}' not found"
                };
            }

            string objectPath = GetGameObjectPath(go);

            if (string.IsNullOrEmpty(componentType))
            {
                // Record transform change
                if (fieldName == "position")
                {
                    changeLog.RecordPositionChange(objectPath, go.transform.position);
                }
                // Add more transform properties as needed
            }
            else
            {
                // Record component field change
                changeLog.RecordComponentChange(objectPath, componentType, fieldName, value);
            }

            return new BridgeResult
            {
                commandId = cmd.id,
                success = true,
                message = $"Recorded change for '{objectName}'"
            };
        }
        
        #endregion
        
        #region Helpers
        
        private object ConvertValueToType(object value, System.Type targetType)
        {
            if (value == null)
                return null;
            
            // Already correct type
            if (targetType.IsInstanceOfType(value))
                return value;
            
            // Handle Unity types that come as JSON objects (Newtonsoft.Json.Linq.JObject)
            if (value is Newtonsoft.Json.Linq.JObject jobj)
            {
                // Vector3
                if (targetType == typeof(Vector3))
                {
                    return new Vector3(
                        jobj["x"]?.ToObject<float>() ?? 0f,
                        jobj["y"]?.ToObject<float>() ?? 0f,
                        jobj["z"]?.ToObject<float>() ?? 0f
                    );
                }
                
                // Vector2
                if (targetType == typeof(Vector2))
                {
                    return new Vector2(
                        jobj["x"]?.ToObject<float>() ?? 0f,
                        jobj["y"]?.ToObject<float>() ?? 0f
                    );
                }
                
                // Color
                if (targetType == typeof(Color))
                {
                    return new Color(
                        jobj["r"]?.ToObject<float>() ?? 0f,
                        jobj["g"]?.ToObject<float>() ?? 0f,
                        jobj["b"]?.ToObject<float>() ?? 0f,
                        jobj["a"]?.ToObject<float>() ?? 1f
                    );
                }
                
                // Quaternion
                if (targetType == typeof(Quaternion))
                {
                    return new Quaternion(
                        jobj["x"]?.ToObject<float>() ?? 0f,
                        jobj["y"]?.ToObject<float>() ?? 0f,
                        jobj["z"]?.ToObject<float>() ?? 0f,
                        jobj["w"]?.ToObject<float>() ?? 1f
                    );
                }
                
                // Rect
                if (targetType == typeof(Rect))
                {
                    return new Rect(
                        jobj["x"]?.ToObject<float>() ?? 0f,
                        jobj["y"]?.ToObject<float>() ?? 0f,
                        jobj["width"]?.ToObject<float>() ?? 0f,
                        jobj["height"]?.ToObject<float>() ?? 0f
                    );
                }
            }
            
            // Handle numeric conversions
            try
            {
                if (targetType == typeof(float))
                    return System.Convert.ToSingle(value);
                if (targetType == typeof(int))
                    return System.Convert.ToInt32(value);
                if (targetType == typeof(bool))
                    return System.Convert.ToBoolean(value);
                if (targetType == typeof(string))
                    return value.ToString();
            }
            catch (System.Exception ex)
            {
                Log($"⚠️ Failed to convert {value} to {targetType.Name}: {ex.Message}");
            }
            
            // Default: try to cast
            return System.Convert.ChangeType(value, targetType);
        }
        
        private string GetGameObjectPath(GameObject obj)
        {
            string path = obj.name;
            Transform current = obj.transform.parent;
            while (current != null)
            {
                path = current.name + "/" + path;
                current = current.parent;
            }
            return path;
        }
        
        private Dictionary<string, object> GetComponentData(Component comp)
        {
            var data = new Dictionary<string, object>();
            
            // Get all public fields
            var fields = comp.GetType().GetFields(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
            foreach (var field in fields)
            {
                try
                {
                    var value = field.GetValue(comp);
                    data[field.Name] = value?.ToString() ?? "null";
                }
                catch { }
            }
            
            // Get all public properties
            var properties = comp.GetType().GetProperties(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
            foreach (var property in properties)
            {
                if (property.CanRead)
                {
                    try
                    {
                        var value = property.GetValue(comp);
                        data[property.Name] = value?.ToString() ?? "null";
                    }
                    catch { }
                }
            }
            
            return data;
        }
        
        #endregion
        
        #region Helpers
        
        private void WriteBridgeResult(BridgeResult result)
        {
            try
            {
                string json = JsonConvert.SerializeObject(result, Formatting.Indented);
                File.WriteAllText(resultsFilePath, json);
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"[SynLink] Failed to write result: {ex.Message}");
            }
        }
        
        private void Log(string message)
        {
            string logEntry = $"[{System.DateTime.Now:HH:mm:ss}] {message}\n";
            Debug.Log($"[SynLink] {message}");
            
            try
            {
                File.AppendAllText(logsFilePath, logEntry);
            }
            catch { }
        }
        
        #endregion
    }
    
    #region Data Structures
    
    [System.Serializable]
    public class BridgeCommandBatch
    {
        public List<BridgeCommand> commands;
    }
    
    [System.Serializable]
    public class BridgeCommand
    {
        public string id;
        public string type;
        public Dictionary<string, object> parameters;
    }
    
    [System.Serializable]
    public class BridgeResult
    {
        public string commandId;
        public bool success;
        public string message;
        public string timestamp;
        public Dictionary<string, object> data;
        public string error;
    }
    
    #endregion
}
