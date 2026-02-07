using UnityEngine;
using UnityEditor;
using System;
using System.Collections.Generic;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Text.RegularExpressions;
using Newtonsoft.Json;

namespace Synthesis.Editor
{
    /// <summary>
    /// Edit Mode console monitor - captures logs even when not playing.
    ///
    /// Philosophy: "Always present, naturally aware" - I'm here in Edit Mode,
    /// learning from compile errors, warnings, and your workflow patterns.
    ///
    /// Features:
    /// - Captures console output in Edit Mode (not just Play Mode)
    /// - Connects directly to Python WebSocket server
    /// - Automatic initialization on Unity load
    /// - Smart filtering (errors always, warnings filtered, important logs)
    /// - Works alongside runtime ConsoleWatcher for complete coverage
    /// </summary>
    [InitializeOnLoad]
    public static class ConsoleWatcherEditor
    {
        #region Settings

        private static bool captureErrors = true;
        private static bool captureWarnings = true;
        private static bool captureImportantLogs = false;

        private static string[] noisyWarnings = new string[]
        {
            "Mesh.colors",
            "obsolete",
            "deprecated",
            "URP",
            "Shader Graphs"
        };

        private static string[] importantKeywords = new string[]
        {
            "[synthesis",
            "[rag]",
            "initialized",
            "connected",
            "failed",
            "success"
        };

        #endregion

        #region State

        private static ClientWebSocket webSocket;
        private static CancellationTokenSource cancellationToken;
        private static bool isConnected = false;
        private static bool isConnecting = false;

        private static List<ConsoleEntry> pendingEntries = new List<ConsoleEntry>();
        private static HashSet<int> seenHashes = new HashSet<int>();

        private static float lastSendTime = 0f;
        private static float batchInterval = 2f;
        private static int batchSize = 10;

        private static int totalCaptured = 0;
        private static int totalSkipped = 0;

        private static string serverUrl = "ws://localhost:8765";

        #endregion

        #region Initialization

        static ConsoleWatcherEditor()
        {
            // Initialize on Unity load
            EditorApplication.update += Update;
            Application.logMessageReceived += HandleLogMessage;

            // Connect to WebSocket server
            ConnectAsync();

            Debug.Log("[ConsoleWatcher Editor] 👁️ Edit Mode monitoring active - I'm always here");
        }

        #endregion

        #region Update Loop

        private static void Update()
        {
            // Send batched entries periodically
            if (pendingEntries.Count > 0)
            {
                float currentTime = (float)EditorApplication.timeSinceStartup;
                if (currentTime - lastSendTime >= batchInterval)
                {
                    SendBatch();
                }
            }

            // Also send if batch is full
            if (pendingEntries.Count >= batchSize)
            {
                SendBatch();
            }
        }

        #endregion

        #region WebSocket Connection

        private static async void ConnectAsync()
        {
            if (isConnected || isConnecting)
                return;

            isConnecting = true;

            try
            {
                cancellationToken = new CancellationTokenSource();
                webSocket = new ClientWebSocket();

                await webSocket.ConnectAsync(new Uri(serverUrl), cancellationToken.Token);
                isConnected = true;
                isConnecting = false;

                Debug.Log("[ConsoleWatcher Editor] ✅ Connected to Python server");

                // Start receiving messages
                _ = ReceiveLoop();
            }
            catch (Exception e)
            {
                isConnecting = false;
                isConnected = false;

                // Only log if it's not a connection refused error (server might not be running)
                if (!(e is WebSocketException))
                {
                    Debug.LogWarning($"[ConsoleWatcher Editor] Connection failed: {e.Message}");
                }

                // Schedule reconnect attempt
                ScheduleReconnect();
            }
        }

        private static void ScheduleReconnect()
        {
            EditorApplication.delayCall += () =>
            {
                System.Threading.Thread.Sleep(5000); // Wait 5 seconds
                ConnectAsync();
            };
        }

        private static async Task ReceiveLoop()
        {
            var buffer = new byte[4096];

            try
            {
                while (isConnected && webSocket.State == WebSocketState.Open)
                {
                    var result = await webSocket.ReceiveAsync(
                        new ArraySegment<byte>(buffer),
                        cancellationToken.Token
                    );

                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        await webSocket.CloseAsync(
                            WebSocketCloseStatus.NormalClosure,
                            "Closing",
                            cancellationToken.Token
                        );
                        isConnected = false;
                        ScheduleReconnect();
                        break;
                    }
                }
            }
            catch (Exception e)
            {
                if (!(e is OperationCanceledException))
                {
                    Debug.LogWarning($"[ConsoleWatcher Editor] Receive error: {e.Message}");
                }
                isConnected = false;
                ScheduleReconnect();
            }
        }

        #endregion

        #region Console Capture

        private static void HandleLogMessage(string logString, string stackTrace, LogType type)
        {
            // Should we capture this?
            if (!ShouldCapture(logString, type))
            {
                totalSkipped++;
                return;
            }

            // Create entry
            var entry = new ConsoleEntry
            {
                type = type.ToString().ToLower(),
                message = logString,
                stackTrace = stackTrace,
                timestamp = DateTime.Now.ToString("o"),
                context = "editor" // Mark as Edit Mode
            };

            // Try to extract file and line from stack trace
            ExtractFileAndLine(stackTrace, out entry.file, out entry.line);

            // Deduplicate
            int hash = ComputeEntryHash(entry);
            if (seenHashes.Contains(hash))
            {
                totalSkipped++;
                return;
            }

            seenHashes.Add(hash);

            // Add to batch
            pendingEntries.Add(entry);
            totalCaptured++;
        }

        private static bool ShouldCapture(string message, LogType type)
        {
            // Always capture errors and exceptions
            if ((type == LogType.Error || type == LogType.Exception || type == LogType.Assert) && captureErrors)
            {
                return true;
            }

            // Capture warnings (with filtering)
            if (type == LogType.Warning && captureWarnings)
            {
                // Skip noisy warnings
                foreach (string noise in noisyWarnings)
                {
                    if (message.IndexOf(noise, StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        return false;
                    }
                }
                return true;
            }

            // Only capture important logs
            if (type == LogType.Log && captureImportantLogs)
            {
                foreach (string keyword in importantKeywords)
                {
                    if (message.IndexOf(keyword, StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        return true;
                    }
                }
            }

            return false;
        }

        private static void ExtractFileAndLine(string stackTrace, out string file, out int line)
        {
            file = "";
            line = 0;

            if (string.IsNullOrEmpty(stackTrace))
                return;

            // Look for pattern: (at Assets/Path/File.cs:42)
            var match = Regex.Match(stackTrace, @"\(at (.+?):(\d+)\)");
            if (match.Success)
            {
                file = match.Groups[1].Value;
                int.TryParse(match.Groups[2].Value, out line);
            }
        }

        private static int ComputeEntryHash(ConsoleEntry entry)
        {
            // Hash based on type + message + file + line
            unchecked
            {
                int hash = 17;
                hash = hash * 31 + (entry.type?.GetHashCode() ?? 0);
                hash = hash * 31 + (entry.message?.GetHashCode() ?? 0);
                hash = hash * 31 + (entry.file?.GetHashCode() ?? 0);
                hash = hash * 31 + entry.line.GetHashCode();
                return hash;
            }
        }

        #endregion

        #region Sending

        private static async void SendBatch()
        {
            if (pendingEntries.Count == 0 || !isConnected)
                return;

            try
            {
                // Create command
                var command = new
                {
                    id = $"console_editor_{DateTime.Now.Ticks}",
                    type = "console_log",
                    parameters = new
                    {
                        entries = ConvertEntriesToObjects(pendingEntries)
                    }
                };

                string json = JsonConvert.SerializeObject(command);
                byte[] bytes = Encoding.UTF8.GetBytes(json);

                await webSocket.SendAsync(
                    new ArraySegment<byte>(bytes),
                    WebSocketMessageType.Text,
                    true,
                    cancellationToken.Token
                );

                // Clear batch
                pendingEntries.Clear();
                lastSendTime = (float)EditorApplication.timeSinceStartup;
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[ConsoleWatcher Editor] Send error: {e.Message}");
                isConnected = false;
                ScheduleReconnect();
            }
        }

        private static List<Dictionary<string, object>> ConvertEntriesToObjects(List<ConsoleEntry> entries)
        {
            var result = new List<Dictionary<string, object>>();

            foreach (var entry in entries)
            {
                var dict = new Dictionary<string, object>
                {
                    { "type", entry.type },
                    { "message", entry.message },
                    { "file", entry.file ?? "" },
                    { "line", entry.line },
                    { "stackTrace", entry.stackTrace ?? "" },
                    { "timestamp", entry.timestamp },
                    { "context", entry.context }
                };
                result.Add(dict);
            }

            return result;
        }

        #endregion

        #region Data Structures

        private class ConsoleEntry
        {
            public string type;
            public string message;
            public string file;
            public int line;
            public string stackTrace;
            public string timestamp;
            public string context; // "editor" or "runtime"
        }

        #endregion

        #region Public API

        /// <summary>
        /// Get capture statistics
        /// </summary>
        [MenuItem("Synthesis/Console Watcher/Show Edit Mode Stats")]
        public static void ShowStats()
        {
            string stats = $"Edit Mode Console Watcher:\n" +
                          $"  Connected: {isConnected}\n" +
                          $"  Captured: {totalCaptured}\n" +
                          $"  Skipped: {totalSkipped}\n" +
                          $"  Pending: {pendingEntries.Count}";

            Debug.Log(stats);
            EditorUtility.DisplayDialog("Console Watcher Stats", stats, "OK");
        }

        /// <summary>
        /// Reset deduplication cache
        /// </summary>
        [MenuItem("Synthesis/Console Watcher/Reset Deduplication")]
        public static void ResetDeduplication()
        {
            seenHashes.Clear();
            Debug.Log("[ConsoleWatcher Editor] Deduplication cache cleared");
        }

        /// <summary>
        /// Manual reconnect
        /// </summary>
        [MenuItem("Synthesis/Console Watcher/Reconnect")]
        public static void ManualReconnect()
        {
            if (isConnected)
            {
                Debug.Log("[ConsoleWatcher Editor] Already connected");
                return;
            }

            ConnectAsync();
        }

        #endregion
    }
}
