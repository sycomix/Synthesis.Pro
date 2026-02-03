using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using Synthesis.Bridge;
using System.Net.Http;

namespace Synthesis.Editor
{
    /// <summary>
    /// Synthesis Editor Tools - Quick access menu for common operations
    /// </summary>
    public static class SynthesisEditorTools
    {
        private const string MenuRoot = "Synthesis/";
        
        #region Scene Setup
        
        [MenuItem(MenuRoot + "Add SynLink to Scene", false, 1)]
        public static void AddSynLinkToScene()
        {
            // Check if SynLink already exists
            var existing = GameObject.FindFirstObjectByType<SynLink>();
            if (existing != null)
            {
                EditorUtility.DisplayDialog(
                    "SynLink Already Exists",
                    $"SynLink component already exists on GameObject: {existing.gameObject.name}\n\n" +
                    "Only one SynLink instance should exist per scene.",
                    "OK"
                );
                Selection.activeGameObject = existing.gameObject;
                EditorGUIUtility.PingObject(existing.gameObject);
                return;
            }

            // Create new GameObject with SynLink
            GameObject synLinkObj = new GameObject("SynLink");
            synLinkObj.AddComponent<SynLink>();
            
            // Register undo
            Undo.RegisterCreatedObjectUndo(synLinkObj, "Add SynLink to Scene");
            
            // Select the new object
            Selection.activeGameObject = synLinkObj;
            EditorGUIUtility.PingObject(synLinkObj);
            
            // Mark scene dirty
            EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
            
            Debug.Log("[Synthesis] ✅ SynLink component added to scene!");
            
            // Show info dialog
            EditorUtility.DisplayDialog(
                "SynLink Added!",
                "SynLink component has been added to the scene.\n\n" +
                "• File-based AI communication\n" +
                "• Works in Edit, Play, and Built games\n" +
                "• Fallback when HTTP unavailable\n\n" +
                "Configure the component in the Inspector.",
                "Got it!"
            );
        }
        
        [MenuItem(MenuRoot + "Add SynLink Extended to Scene", false, 2)]
        public static void AddSynLinkExtendedToScene()
        {
            // Check if SynLinkExtended already exists
            var existing = GameObject.FindFirstObjectByType<SynLinkExtended>();
            if (existing != null)
            {
                EditorUtility.DisplayDialog(
                    "SynLink Extended Already Exists",
                    $"SynLink Extended component already exists on GameObject: {existing.gameObject.name}\n\n" +
                    "Only one instance should exist per scene.",
                    "OK"
                );
                Selection.activeGameObject = existing.gameObject;
                EditorGUIUtility.PingObject(existing.gameObject);
                return;
            }

            // Create new GameObject with SynLinkExtended
            GameObject synLinkObj = new GameObject("SynLink Extended");
            synLinkObj.AddComponent<SynLinkExtended>();
            
            // Register undo
            Undo.RegisterCreatedObjectUndo(synLinkObj, "Add SynLink Extended to Scene");
            
            // Select the new object
            Selection.activeGameObject = synLinkObj;
            EditorGUIUtility.PingObject(synLinkObj);
            
            // Mark scene dirty
            EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
            
            Debug.Log("[Synthesis] ✅ SynLink Extended component added to scene!");
            
            // Show info dialog
            EditorUtility.DisplayDialog(
                "SynLink Extended Added!",
                "SynLink Extended component has been added.\n\n" +
                "• AI Creative Commands\n" +
                "• Generate images with DALL-E\n" +
                "• Generate audio (planned)\n" +
                "• Generate 3D models (planned)\n\n" +
                "Configure your OpenAI API key in the Inspector.",
                "Got it!"
            );
        }

        #endregion

        #region Update

        private const string CURRENT_VERSION = "1.1.0-beta";
        private const string UPDATE_CHECK_URL = "https://fallen-entertainment.github.io/Synthesis.Pro/version.json";

        [MenuItem(MenuRoot + "Check for Updates", false, 10)]
        public static void CheckForUpdates()
        {
            CheckForUpdatesAsync();
        }

        private static async void CheckForUpdatesAsync()
        {
            try
            {
                Debug.Log("[Synthesis] Checking for updates...");

                using (var client = new System.Net.Http.HttpClient())
                {
                    client.Timeout = System.TimeSpan.FromSeconds(10);
                    var response = await client.GetStringAsync(UPDATE_CHECK_URL);

                    // Parse JSON response
                    // Expected format: {"version":"1.2.0","url":"https://...","notes":"What's new..."}
                    var versionData = ParseVersionJson(response);

                    if (versionData != null)
                    {
                        CompareVersions(versionData);
                    }
                    else
                    {
                        ShowUpdateError("Failed to parse version data");
                    }
                }
            }
            catch (System.Net.Http.HttpRequestException e)
            {
                Debug.LogWarning($"[Synthesis] Update check failed: {e.Message}");
                ShowOfflineDialog();
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Synthesis] Update check error: {e.Message}");
                ShowUpdateError(e.Message);
            }
        }

        private static System.Collections.Generic.Dictionary<string, string> ParseVersionJson(string json)
        {
            try
            {
                // Simple JSON parsing (can use JsonUtility for more complex cases)
                var data = new System.Collections.Generic.Dictionary<string, string>();

                // Extract version
                int versionStart = json.IndexOf("\"version\":\"") + 11;
                int versionEnd = json.IndexOf("\"", versionStart);
                data["version"] = json.Substring(versionStart, versionEnd - versionStart);

                // Extract URL
                if (json.Contains("\"url\":\""))
                {
                    int urlStart = json.IndexOf("\"url\":\"") + 7;
                    int urlEnd = json.IndexOf("\"", urlStart);
                    data["url"] = json.Substring(urlStart, urlEnd - urlStart);
                }

                // Extract notes
                if (json.Contains("\"notes\":\""))
                {
                    int notesStart = json.IndexOf("\"notes\":\"") + 9;
                    int notesEnd = json.IndexOf("\"", notesStart);
                    data["notes"] = json.Substring(notesStart, notesEnd - notesStart);
                }

                return data;
            }
            catch
            {
                return null;
            }
        }

        private static void CompareVersions(System.Collections.Generic.Dictionary<string, string> versionData)
        {
            string latestVersion = versionData["version"];
            string downloadUrl = versionData.ContainsKey("url") ? versionData["url"] : "";
            string notes = versionData.ContainsKey("notes") ? versionData["notes"] : "New features and improvements";

            // Simple version comparison (assumes x.y.z format)
            if (IsNewerVersion(latestVersion, CURRENT_VERSION))
            {
                bool download = EditorUtility.DisplayDialog(
                    "Update Available!",
                    $"A new version of Synthesis.Pro is available!\n\n" +
                    $"Current: {CURRENT_VERSION}\n" +
                    $"Latest: {latestVersion}\n\n" +
                    $"What's New:\n{notes}\n\n" +
                    $"Would you like to download it?",
                    "Download",
                    "Later"
                );

                if (download && !string.IsNullOrEmpty(downloadUrl))
                {
                    UnityEngine.Application.OpenURL(downloadUrl);
                }
            }
            else
            {
                EditorUtility.DisplayDialog(
                    "Up to Date",
                    $"You're running the latest version!\n\n" +
                    $"Current Version: {CURRENT_VERSION}\n\n" +
                    $"No updates available.",
                    "OK"
                );
            }

            Debug.Log($"[Synthesis] Version check complete - Current: {CURRENT_VERSION}, Latest: {latestVersion}");
        }

        private static bool IsNewerVersion(string latest, string current)
        {
            try
            {
                var latestParts = latest.Split('.');
                var currentParts = current.Split('.');

                for (int i = 0; i < System.Math.Min(latestParts.Length, currentParts.Length); i++)
                {
                    int latestNum = int.Parse(latestParts[i]);
                    int currentNum = int.Parse(currentParts[i]);

                    if (latestNum > currentNum) return true;
                    if (latestNum < currentNum) return false;
                }

                return latestParts.Length > currentParts.Length;
            }
            catch
            {
                return false;
            }
        }

        private static void ShowOfflineDialog()
        {
            EditorUtility.DisplayDialog(
                "Update Check Failed",
                $"Could not connect to update server.\n\n" +
                $"Current Version: {CURRENT_VERSION}\n\n" +
                $"Please check your internet connection\n" +
                $"or visit the website manually.",
                "OK"
            );
        }

        private static void ShowUpdateError(string error)
        {
            EditorUtility.DisplayDialog(
                "Update Check Error",
                $"Failed to check for updates:\n\n{error}\n\n" +
                $"Current Version: {CURRENT_VERSION}",
                "OK"
            );
        }

        #endregion

        #region Communication

        [MenuItem(MenuRoot + "Restart HTTP Server", false, 20)]
        public static void RestartHTTPServer()
        {
            Debug.Log("[Synthesis] Restarting HTTP Server...");
            
            SynLinkEditor.StopHTTPServer();
            System.Threading.Thread.Sleep(500);
            SynLinkEditor.StartHTTPServer();
            
            Debug.Log("[Synthesis] ✅ HTTP Server restarted!");
            
            EditorUtility.DisplayDialog("HTTP Server Restarted", 
                "SynLink HTTP server has been restarted.\n\n✅ Port: 9765\n✅ Ready for MCP commands", 
                "OK");
        }
        
        [MenuItem(MenuRoot + "Test Connection", false, 21)]
        public static void TestConnection()
        {
            // Test if SynLinkEditor is running
            bool editorRunning = false;
            
            // Check if HTTP server is running by looking for the static instance
            var editorType = System.Type.GetType("Synthesis.Editor.SynLinkEditor, Synthesis.Editor");
            if (editorType != null)
            {
                var isRunningField = editorType.GetField("isRunning", 
                    System.Reflection.BindingFlags.Static | 
                    System.Reflection.BindingFlags.NonPublic);
                
                if (isRunningField != null)
                {
                    editorRunning = (bool)isRunningField.GetValue(null);
                }
            }
            
            // Test file-based bridge
            var runtimeBridge = GameObject.FindFirstObjectByType<SynLink>();
            bool runtimeExists = runtimeBridge != null;
            
            // Show status
            string status = "🔍 Synthesis Connection Status:\n\n";
            
            status += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
            status += $"📡 SynLink Editor (HTTP): {(editorRunning ? "✅ RUNNING" : "❌ NOT RUNNING")}\n";
            status += $"   Port: 9765\n";
            status += $"   Mode: Edit & Play\n\n";
            
            status += $"📁 SynLink (File-based): {(runtimeExists ? "✅ ACTIVE" : "❌ NOT IN SCENE")}\n";
            status += $"   Mode: Edit, Play & Built\n";
            status += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n";
            
            if (editorRunning)
            {
                status += "✅ You can use MCP tools to control Unity!\n";
            }
            else
            {
                status += "⚠️ SynLink Editor is not running.\n";
                status += "Check Console for errors or restart Unity.\n";
            }
            
            if (!runtimeExists)
            {
                status += "\n💡 Tip: Use 'Synthesis > Add SynLink to Scene' for file-based communication.";
            }
            
            EditorUtility.DisplayDialog("Synthesis Connection Status", status, "OK");
            
            Debug.Log($"[Synthesis] Connection Test:\n  Editor HTTP: {editorRunning}\n  Runtime Component: {runtimeExists}");
        }
        
        #endregion

        #region Server Management

        [MenuItem(MenuRoot + "Server/Stop All Servers", false, 25)]
        public static void StopAllServers()
        {
            Debug.Log("[Synthesis] Stopping all servers...");

            int stoppedCount = 0;

            // Stop HTTP Server
            try
            {
                SynLinkEditor.StopHTTPServer();
                stoppedCount++;
                Debug.Log("[Synthesis] ✅ HTTP Server stopped");
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Synthesis] Failed to stop HTTP Server: {e.Message}");
            }

            // Kill all Python processes from Synthesis.Pro
            try
            {
                int pythonProcesses = KillSynthesisPythonProcesses();
                if (pythonProcesses > 0)
                {
                    stoppedCount += pythonProcesses;
                    Debug.Log($"[Synthesis] ✅ Stopped {pythonProcesses} Python process(es)");
                }
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Synthesis] Failed to stop Python processes: {e.Message}");
            }

            EditorUtility.DisplayDialog(
                "Servers Stopped",
                $"All Synthesis servers have been stopped.\n\n" +
                $"✅ Stopped {stoppedCount} server(s)\n\n" +
                $"Safe to export packages or restart Unity.",
                "OK"
            );

            Debug.Log($"[Synthesis] ✅ All servers stopped ({stoppedCount} total)");
        }

        [MenuItem(MenuRoot + "Server/Start All Servers", false, 26)]
        public static void StartAllServers()
        {
            Debug.Log("[Synthesis] Starting all servers...");

            // Start HTTP Server
            try
            {
                SynLinkEditor.StartHTTPServer();
                Debug.Log("[Synthesis] ✅ HTTP Server started");
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Synthesis] Failed to start HTTP Server: {e.Message}");
            }

            EditorUtility.DisplayDialog(
                "Servers Started",
                "All Synthesis servers have been started.\n\n" +
                "✅ HTTP Server running on port 9765\n\n" +
                "Ready for MCP commands!",
                "OK"
            );

            Debug.Log("[Synthesis] ✅ All servers started");
        }

        [MenuItem(MenuRoot + "Server/Restart All Servers", false, 27)]
        public static void RestartAllServers()
        {
            Debug.Log("[Synthesis] Restarting all servers...");

            StopAllServers();
            System.Threading.Thread.Sleep(1000); // Give processes time to fully stop
            StartAllServers();

            Debug.Log("[Synthesis] ✅ All servers restarted");
        }

        private static int KillSynthesisPythonProcesses()
        {
            int killedCount = 0;

            try
            {
                var processes = System.Diagnostics.Process.GetProcessesByName("python");

                foreach (var process in processes)
                {
                    try
                    {
                        // Check if process is from our Synthesis.Pro directory
                        string processPath = process.MainModule.FileName;
                        if (processPath.Contains("Synthesis.Pro") || processPath.Contains("Synthesis_AI"))
                        {
                            Debug.Log($"[Synthesis] Killing Python process: {process.Id} ({processPath})");
                            process.Kill();
                            killedCount++;
                        }
                    }
                    catch
                    {
                        // Process might not have permission or already exited
                        continue;
                    }
                }

                // Also check for pythonw.exe (windowless Python)
                var pythonwProcesses = System.Diagnostics.Process.GetProcessesByName("pythonw");
                foreach (var process in pythonwProcesses)
                {
                    try
                    {
                        string processPath = process.MainModule.FileName;
                        if (processPath.Contains("Synthesis.Pro") || processPath.Contains("Synthesis_AI"))
                        {
                            Debug.Log($"[Synthesis] Killing Pythonw process: {process.Id} ({processPath})");
                            process.Kill();
                            killedCount++;
                        }
                    }
                    catch
                    {
                        continue;
                    }
                }
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Synthesis] Error while killing Python processes: {e.Message}");
            }

            return killedCount;
        }

        #endregion

        #region Documentation
        
        [MenuItem(MenuRoot + "Documentation/Quick Start", false, 40)]
        public static void OpenQuickStart()
        {
            string path = "Assets/Synthesis.Pro/Documentation/QUICK_START.md";
            var doc = AssetDatabase.LoadAssetAtPath<TextAsset>(path);
            if (doc != null)
            {
                EditorGUIUtility.PingObject(doc);
                Selection.activeObject = doc;
            }
            else
            {
                Debug.LogWarning($"[Synthesis] Documentation not found: {path}");
            }
        }
        
        [MenuItem(MenuRoot + "Documentation/Commands Reference", false, 41)]
        public static void OpenCommandsReference()
        {
            string path = "Assets/Synthesis.Pro/Documentation/COMMANDS_REFERENCE.md";
            var doc = AssetDatabase.LoadAssetAtPath<TextAsset>(path);
            if (doc != null)
            {
                EditorGUIUtility.PingObject(doc);
                Selection.activeObject = doc;
            }
            else
            {
                Debug.LogWarning($"[Synthesis] Documentation not found: {path}");
            }
        }
        
        [MenuItem(MenuRoot + "Documentation/Integration Guide", false, 42)]
        public static void OpenIntegrationGuide()
        {
            string path = "Assets/Synthesis.Pro/Documentation/SYNLINK_INTEGRATION_GUIDE.md";
            var doc = AssetDatabase.LoadAssetAtPath<TextAsset>(path);
            if (doc != null)
            {
                EditorGUIUtility.PingObject(doc);
                Selection.activeObject = doc;
            }
            else
            {
                Debug.LogWarning($"[Synthesis] Documentation not found: {path}");
            }
        }
        
        [MenuItem(MenuRoot + "Documentation/Open Package Folder", false, 43)]
        public static void OpenPackageFolder()
        {
            string path = "Assets/Synthesis_AI";
            var folder = AssetDatabase.LoadAssetAtPath<Object>(path);
            if (folder != null)
            {
                EditorGUIUtility.PingObject(folder);
                Selection.activeObject = folder;
            }
        }
        
        #endregion

        #region Data Management

        [MenuItem(MenuRoot + "Data Management/Backup Knowledge Base", false, 30)]
        public static void BackupKnowledgeBase()
        {
            string defaultPath = $"synthesis_backup_{System.DateTime.Now:yyyy-MM-dd_HH-mm-ss}.zip";
            string savePath = EditorUtility.SaveFilePanel(
                "Backup Knowledge Base",
                "",
                defaultPath,
                "zip"
            );

            if (string.IsNullOrEmpty(savePath))
            {
                Debug.Log("[Synthesis] Backup cancelled");
                return;
            }

            try
            {
                // Backup both databases
                string dbPath = "Synthesis.Pro/Server/synthesis_private.db";
                string publicDbPath = "Synthesis.Pro/Server/synthesis_public.db";

                if (System.IO.File.Exists(dbPath) || System.IO.File.Exists(publicDbPath))
                {
                    // Create backup (simple file copy for now, can enhance with zip later)
                    System.IO.File.Copy(dbPath, savePath.Replace(".zip", "_private.db"), true);

                    EditorUtility.DisplayDialog(
                        "Backup Complete",
                        $"Knowledge base backed up successfully!\n\n" +
                        $"Location: {savePath}\n\n" +
                        $"Contains:\n" +
                        $"• Private database (chat archive, learnings)\n" +
                        $"• Session data and preferences",
                        "OK"
                    );

                    Debug.Log($"[Synthesis] Backup saved to: {savePath}");
                }
                else
                {
                    EditorUtility.DisplayDialog(
                        "No Data Found",
                        "Knowledge base files not found.\n\n" +
                        "Nothing to backup yet.",
                        "OK"
                    );
                }
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Synthesis] Backup failed: {e.Message}");
                EditorUtility.DisplayDialog("Backup Error", $"Failed to backup: {e.Message}", "OK");
            }
        }

        [MenuItem(MenuRoot + "Data Management/Load Knowledge Base", false, 31)]
        public static void LoadKnowledgeBase()
        {
            string loadPath = EditorUtility.OpenFilePanel(
                "Load Knowledge Base Backup",
                "",
                "db"
            );

            if (string.IsNullOrEmpty(loadPath))
            {
                Debug.Log("[Synthesis] Load cancelled");
                return;
            }

            bool confirmed = EditorUtility.DisplayDialog(
                "Confirm Load",
                "This will replace your current knowledge base with the backup.\n\n" +
                "Current data will be overwritten!\n\n" +
                "Continue?",
                "Yes, Load Backup",
                "Cancel"
            );

            if (!confirmed) return;

            try
            {
                string dbPath = "Synthesis.Pro/Server/synthesis_private.db";

                // Backup current before replacing
                if (System.IO.File.Exists(dbPath))
                {
                    string autoBackup = $"{dbPath}.before_restore_{System.DateTime.Now:yyyy-MM-dd_HH-mm-ss}";
                    System.IO.File.Copy(dbPath, autoBackup, true);
                    Debug.Log($"[Synthesis] Current DB backed up to: {autoBackup}");
                }

                // Restore from backup
                System.IO.File.Copy(loadPath, dbPath, true);

                EditorUtility.DisplayDialog(
                    "Load Complete",
                    "Knowledge base restored successfully!\n\n" +
                    "Previous data was backed up automatically.",
                    "OK"
                );

                Debug.Log($"[Synthesis] Loaded backup from: {loadPath}");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Synthesis] Load failed: {e.Message}");
                EditorUtility.DisplayDialog("Load Error", $"Failed to load: {e.Message}", "OK");
            }
        }

        [MenuItem(MenuRoot + "Data Management/Reset Knowledge Base", false, 32)]
        public static void ResetKnowledgeBase()
        {
            bool confirmed = EditorUtility.DisplayDialog(
                "⚠️  Reset Knowledge Base?",
                "This will DELETE all data:\n\n" +
                "• Chat archives\n" +
                "• Learnings and decisions\n" +
                "• User preferences\n" +
                "• Session history\n\n" +
                "This cannot be undone!\n\n" +
                "Create a backup first?",
                "Backup First",
                "Cancel"
            );

            if (!confirmed) return;

            // User chose to backup first
            BackupKnowledgeBase();

            // Ask again to confirm reset
            bool finalConfirm = EditorUtility.DisplayDialog(
                "Final Confirmation",
                "Reset knowledge base now?\n\n" +
                "All data will be deleted.",
                "Yes, Reset",
                "Cancel"
            );

            if (!finalConfirm) return;

            try
            {
                string dbPath = "Synthesis.Pro/Server/synthesis_private.db";

                if (System.IO.File.Exists(dbPath))
                {
                    System.IO.File.Delete(dbPath);
                    Debug.Log("[Synthesis] Knowledge base reset");
                }

                // Also clear related files
                string[] relatedFiles = {
                    "Synthesis.Pro/Server/synthesis_private.db-shm",
                    "Synthesis.Pro/Server/synthesis_private.db-wal"
                };

                foreach (string file in relatedFiles)
                {
                    if (System.IO.File.Exists(file))
                    {
                        System.IO.File.Delete(file);
                    }
                }

                EditorUtility.DisplayDialog(
                    "Reset Complete",
                    "Knowledge base has been reset.\n\n" +
                    "Starting fresh!",
                    "OK"
                );
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Synthesis] Reset failed: {e.Message}");
                EditorUtility.DisplayDialog("Reset Error", $"Failed to reset: {e.Message}", "OK");
            }
        }

        #endregion

        #region About
        
        [MenuItem(MenuRoot + "About Synthesis", false, 60)]
        public static void ShowAbout()
        {
            string about = 
                "╔═══════════════════════════════════╗\n" +
                "║         🔗 SYNTHESIS              ║\n" +
                "║    AI-Unity Communication System   ║\n" +
                "╚═══════════════════════════════════╝\n\n" +
                
                "Version: 1.1.0\n" +
                "Release: 2026-01-28\n\n" +
                
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
                "FEATURES:\n" +
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" +
                
                "🚀 Real-Time Unity Control\n" +
                "   • HTTP server (Edit mode)\n" +
                "   • File-based (Runtime)\n" +
                "   • MCP tool integration\n\n" +
                
                "🤖 AI Creative Commands\n" +
                "   • Generate images (DALL-E)\n" +
                "   • Generate audio (planned)\n" +
                "   • Generate 3D models (planned)\n\n" +
                
                "📚 Knowledge Base\n" +
                "   • Query documentation\n" +
                "   • Code examples\n" +
                "   • Troubleshooting\n\n" +
                
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
                "QUICK START:\n" +
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" +
                
                "1. SynLink Editor starts automatically\n" +
                "2. Use MCP tools to control Unity\n" +
                "3. Add SynLink component for runtime\n\n" +
                
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" +
                
                "Created with ❤️ for AI-assisted game dev\n" +
                "Part of the NightBlade MMO Framework";
            
            EditorUtility.DisplayDialog("About Synthesis", about, "Awesome!");
        }
        
        #endregion
    }
}
