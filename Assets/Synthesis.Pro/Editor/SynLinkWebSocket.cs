using UnityEngine;
using UnityEditor;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Generic;

namespace Synthesis.Editor
{
    /// <summary>
    /// WebSocket server for real-time chat communication
    /// Runs alongside HTTP server for instant message delivery
    /// </summary>
    [InitializeOnLoad]
    public static class SynLinkWebSocket
    {
        private static TcpListener listener;
        private static Thread listenerThread;
        private static List<TcpClient> connectedClients = new List<TcpClient>();
        private static bool isRunning = false;
        private static int wsPort = 9766; // Default port, will auto-select if blocked
        private static int actualPort = 9766; // The port actually being used

        /// <summary>
        /// Get the actual port the WebSocket server is running on
        /// </summary>
        public static int GetActualPort()
        {
            return actualPort;
        }

        /// <summary>
        /// Check if the WebSocket server is currently running
        /// </summary>
        public static bool IsRunning()
        {
            return isRunning;
        }
        
        // Static constructor - starts when Unity Editor loads
        static SynLinkWebSocket()
        {
            Debug.Log("[SynLink WS] 🌐 WebSocket server initializing...");
            
            // Force cleanup of any lingering instances from previous domain reload
            StopWebSocketServer();
            
            EditorApplication.update += Update;
            
            // Delay startup slightly to allow port release
            EditorApplication.delayCall += () =>
            {
                System.Threading.Thread.Sleep(500); // Give OS time to release the port
                StartWebSocketServer();
            };
        }
        
        private static void Update()
        {
            // Process any queued operations if needed
        }
        
        private static int startupRetries = 0;
        private const int MAX_RETRIES = 5; // Increased for TIME_WAIT clearance
        
        /// <summary>
        /// Check if a port is available for binding
        /// </summary>
        private static bool IsPortAvailable(int port)
        {
            TcpListener testListener = null;
            try
            {
                testListener = new TcpListener(IPAddress.Loopback, port);
                testListener.Start();
                testListener.Stop();
                return true;
            }
            catch
            {
                return false;
            }
            finally
            {
                if (testListener != null)
                {
                    try { testListener.Stop(); } catch { }
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
            catch { }
            return "unknown process";
        }
        
        public static void StartWebSocketServer()
        {
            if (isRunning)
            {
                Debug.LogWarning("[SynLink WS] WebSocket server already running!");
                return;
            }
            
            // Smart port selection: try default port first, then alternatives
            int selectedPort = -1;
            const int PORT_RANGE_SIZE = 10;

            // Try default port and alternatives (9766-9776)
            for (int portOffset = 0; portOffset < PORT_RANGE_SIZE; portOffset++)
            {
                int tryPort = wsPort + portOffset;
                if (IsPortAvailable(tryPort))
                {
                    selectedPort = tryPort;
                    if (portOffset > 0)
                    {
                        Debug.Log($"[SynLink WS] Default port {wsPort} was busy, using alternative port {selectedPort}");
                    }
                    break;
                }
            }

            // If no ports available in range, retry with delay (might be temporary TIME_WAIT state)
            if (selectedPort == -1)
            {
                string portOwner = GetPortOwner(wsPort);

                if (startupRetries < MAX_RETRIES)
                {
                    Debug.LogWarning($"[SynLink WS] All ports ({wsPort}-{wsPort + PORT_RANGE_SIZE - 1}) busy. Primary port used by {portOwner}. Retrying in 5 seconds... (Attempt {startupRetries + 1}/{MAX_RETRIES})");
                    startupRetries++;

                    EditorApplication.delayCall += () =>
                    {
                        System.Threading.Thread.Sleep(5000);
                        StartWebSocketServer();
                    };
                    return;
                }
                else
                {
                    Debug.LogError($"[SynLink WS] No available ports after {MAX_RETRIES} attempts. Port {wsPort} used by: {portOwner}");
                    Debug.LogError($"[SynLink WS] Try closing other processes or restart Unity completely.");
                    startupRetries = 0;
                    return;
                }
            }

            // Update to use the selected port
            actualPort = selectedPort;
            
            try
            {
                listener = new TcpListener(IPAddress.Loopback, actualPort);
                listener.Server.SetSocketOption(System.Net.Sockets.SocketOptionLevel.Socket,
                                                System.Net.Sockets.SocketOptionName.ReuseAddress, true);
                listener.Start();
                isRunning = true;

                listenerThread = new Thread(ListenForClients);
                listenerThread.IsBackground = true;
                listenerThread.Start();

                Debug.Log($"[SynLink WS] ✅ WebSocket server started on port {actualPort}");
                
                // Reset retry counter on success
                startupRetries = 0;
            }
            catch (Exception e)
            {
                // Suppress errors if server is already running (common during domain reloads)
                if (e is SocketException || e.Message.Contains("normally permitted") || e.Message.Contains("already in use"))
                {
                    // Silently ignore - server likely already running from previous session
                }
                else
                {
                    // Log unexpected errors as warnings instead of errors
                    Debug.LogWarning($"[SynLink WS] Could not start WebSocket server: {e.GetType().Name} - {e.Message}");
                }
                isRunning = false;
                startupRetries = 0;
            }
        }
        
        public static void StopWebSocketServer()
        {
            if (!isRunning) return;
            
            try
            {
                isRunning = false;
                
                // Close all client connections
                lock (connectedClients)
                {
                    foreach (var client in connectedClients)
                    {
                        try 
                        { 
                            client.Close(); 
                            client.Dispose();
                        } 
                        catch { }
                    }
                    connectedClients.Clear();
                }
                
                // Stop listener
                if (listener != null)
                {
                    try
                    {
                        listener.Stop();
                    }
                    catch { }
                    finally
                    {
                        listener = null;
                    }
                }
                
                // Stop thread
                if (listenerThread != null && listenerThread.IsAlive)
                {
                    if (!listenerThread.Join(1000))
                    {
                        try { listenerThread.Abort(); } catch { }
                    }
                    listenerThread = null;
                }
                
                Debug.Log("[SynLink WS] ✓ WebSocket server stopped");
            }
            catch (Exception e)
            {
                Debug.LogError($"[SynLink WS] Error stopping: {e.Message}");
            }
        }
        
        private static void ListenForClients()
        {
            while (isRunning)
            {
                try
                {
                    var client = listener.AcceptTcpClient();
                    Thread clientThread = new Thread(() => HandleClient(client));
                    clientThread.IsBackground = true;
                    clientThread.Start();
                }
                catch (ThreadAbortException)
                {
                    // Thread is being aborted during domain reload - this is expected, don't log
                    break;
                }
                catch (Exception e)
                {
                    // Only log if we're still supposed to be running (ignore shutdown errors)
                    if (isRunning && !(e is SocketException))
                    {
                        Debug.LogWarning($"[SynLink WS] Accept error: {e.Message}");
                    }
                }
            }
        }
        
        private static void HandleClient(TcpClient client)
        {
            try
            {
                NetworkStream stream = client.GetStream();
                
                // Read the WebSocket handshake
                byte[] bytes = new byte[4096];
                int length = stream.Read(bytes, 0, bytes.Length);
                string data = Encoding.UTF8.GetString(bytes, 0, length);
                
                // Check if it's a WebSocket upgrade request
                if (data.Contains("Upgrade: websocket"))
                {
                    // Complete the handshake
                    string response = BuildHandshakeResponse(data);
                    byte[] responseBytes = Encoding.UTF8.GetBytes(response);
                    stream.Write(responseBytes, 0, responseBytes.Length);
                    
                    // Add to connected clients
                    lock (connectedClients)
                    {
                        connectedClients.Add(client);
                    }
                    
                    Debug.Log("[SynLink WS] 🔗 Client connected");
                    
                    // Keep connection alive and listen for messages
                    ListenForMessages(client, stream);
                }
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[SynLink WS] Client error: {e.Message}");
            }
            finally
            {
                lock (connectedClients)
                {
                    connectedClients.Remove(client);
                }
                client.Close();
            }
        }
        
        private static string BuildHandshakeResponse(string request)
        {
            // Extract the WebSocket key
            string key = "";
            var lines = request.Split(new[] { "\r\n" }, StringSplitOptions.None);
            foreach (var line in lines)
            {
                if (line.StartsWith("Sec-WebSocket-Key:"))
                {
                    key = line.Substring("Sec-WebSocket-Key:".Length).Trim();
                    break;
                }
            }
            
            // Compute accept key
            string acceptKey = Convert.ToBase64String(
                System.Security.Cryptography.SHA1.Create().ComputeHash(
                    Encoding.UTF8.GetBytes(key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11")
                )
            );
            
            return "HTTP/1.1 101 Switching Protocols\r\n" +
                   "Upgrade: websocket\r\n" +
                   "Connection: Upgrade\r\n" +
                   $"Sec-WebSocket-Accept: {acceptKey}\r\n\r\n";
        }
        
        private static void ListenForMessages(TcpClient client, NetworkStream stream)
        {
            byte[] buffer = new byte[4096];
            
            while (isRunning && client.Connected)
            {
                try
                {
                    int bytesRead = stream.Read(buffer, 0, buffer.Length);
                    if (bytesRead == 0) break; // Client disconnected
                    
                    // Decode WebSocket frame
                    string message = DecodeWebSocketFrame(buffer, bytesRead);
                    
                    if (!string.IsNullOrEmpty(message))
                    {
                        Debug.Log($"[SynLink WS] 📨 Received: {message}");
                        
                        // Handle the message
                        HandleWebSocketMessage(message);
                    }
                }
                catch (Exception e)
                {
                    Debug.LogWarning($"[SynLink WS] Read error: {e.Message}");
                    break;
                }
            }
        }
        
        private static string DecodeWebSocketFrame(byte[] buffer, int length)
        {
            try
            {
                // Simple WebSocket frame decoding (text frames only)
                if (length < 2) return null;
                
                bool masked = (buffer[1] & 0x80) != 0;
                int payloadLength = buffer[1] & 0x7F;
                int offset = 2;
                
                if (payloadLength == 126)
                {
                    payloadLength = (buffer[2] << 8) | buffer[3];
                    offset = 4;
                }
                else if (payloadLength == 127)
                {
                    // We don't support large frames
                    return null;
                }
                
                byte[] mask = null;
                if (masked)
                {
                    mask = new byte[4];
                    Array.Copy(buffer, offset, mask, 0, 4);
                    offset += 4;
                }
                
                byte[] payload = new byte[payloadLength];
                Array.Copy(buffer, offset, payload, 0, payloadLength);
                
                if (masked)
                {
                    for (int i = 0; i < payloadLength; i++)
                    {
                        payload[i] ^= mask[i % 4];
                    }
                }
                
                return Encoding.UTF8.GetString(payload);
            }
            catch (Exception e)
            {
                Debug.LogError($"[SynLink WS] Decode error: {e.Message}");
                return null;
            }
        }
        
        private static void HandleWebSocketMessage(string message)
        {
            // Message format: JSON with sender and message
            try
            {
                // For now, assume format: {"type":"chat","message":"text"}
                if (message.Contains("\"type\":\"chat\""))
                {
                    // Extract message content (simple parsing)
                    int msgStart = message.IndexOf("\"message\":\"") + 11;
                    int msgEnd = message.IndexOf("\"", msgStart);
                    string chatMessage = message.Substring(msgStart, msgEnd - msgStart);
                    
                    Debug.Log($"[💬 USER] {chatMessage}");

                    // Old in-editor chat window removed - message logged only
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"[SynLink WS] Message handling error: {e.Message}");
            }
        }
        
        public static void BroadcastMessage(string message)
        {
            byte[] frame = EncodeWebSocketFrame(message);
            
            lock (connectedClients)
            {
                foreach (var client in connectedClients)
                {
                    try
                    {
                        if (client.Connected)
                        {
                            NetworkStream stream = client.GetStream();
                            stream.Write(frame, 0, frame.Length);
                        }
                    }
                    catch (Exception e)
                    {
                        Debug.LogWarning($"[SynLink WS] Broadcast error: {e.Message}");
                    }
                }
            }
        }
        
        private static byte[] EncodeWebSocketFrame(string message)
        {
            byte[] payload = Encoding.UTF8.GetBytes(message);
            byte[] frame;
            
            if (payload.Length < 126)
            {
                frame = new byte[2 + payload.Length];
                frame[0] = 0x81; // Text frame
                frame[1] = (byte)payload.Length;
                Array.Copy(payload, 0, frame, 2, payload.Length);
            }
            else if (payload.Length < 65536)
            {
                frame = new byte[4 + payload.Length];
                frame[0] = 0x81;
                frame[1] = 126;
                frame[2] = (byte)(payload.Length >> 8);
                frame[3] = (byte)(payload.Length & 0xFF);
                Array.Copy(payload, 0, frame, 4, payload.Length);
            }
            else
            {
                throw new Exception("Message too large");
            }
            
            return frame;
        }
    }
}
