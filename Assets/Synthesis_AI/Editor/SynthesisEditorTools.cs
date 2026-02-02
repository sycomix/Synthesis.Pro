using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using Synthesis.Bridge;

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
            var existing = GameObject.FindObjectOfType<SynLink>();
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
            var existing = GameObject.FindObjectOfType<SynLinkExtended>();
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
        
        #region Communication
        
        [MenuItem(MenuRoot + "Open Chat Window", false, 20)]
        public static void OpenChatWindow()
        {
            // Ensure chat watcher is running
            SynthesisChatWatcher.EnsureWatcherRunning();

            // Open the IMGUI-based chat window
            SynthesisChatWindow.OpenChatWindow();
        }
        
        [MenuItem(MenuRoot + "Chat Watcher Status", false, 22)]
        public static void ChatWatcherStatus()
        {
            bool running = SynthesisChatWatcher.IsWatcherRunning();
            
            if (running)
            {
                EditorUtility.DisplayDialog(
                    "Chat Watcher Status",
                    "✅ Chat Watcher is RUNNING\n\n" +
                    "The AI will be automatically notified when you send chat messages.\n\n" +
                    "Status: Active and monitoring",
                    "OK"
                );
            }
            else
            {
                bool start = EditorUtility.DisplayDialog(
                    "Chat Watcher Status",
                    "❌ Chat Watcher is NOT RUNNING\n\n" +
                    "The AI won't see your chat messages automatically.\n\n" +
                    "Would you like to start it now?",
                    "Start Watcher",
                    "Cancel"
                );
                
                if (start)
                {
                    SynthesisChatWatcher.StartWatcher();
                }
            }
        }
        
        [MenuItem(MenuRoot + "Restart HTTP Server", false, 23)]
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
        
        [MenuItem(MenuRoot + "Test Connection", false, 24)]
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
            var runtimeBridge = GameObject.FindObjectOfType<SynLink>();
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
        
        #region Documentation
        
        [MenuItem(MenuRoot + "Documentation/Quick Start", false, 40)]
        public static void OpenQuickStart()
        {
            string path = "Assets/Synthesis_AI/Documentation/QUICK_START.md";
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
            string path = "Assets/Synthesis_AI/Documentation/COMMANDS_REFERENCE.md";
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
            string path = "Assets/Synthesis_AI/Documentation/SYNLINK_INTEGRATION_GUIDE.md";
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

        #region Detective Mode & Privacy (Phase 4)

        [MenuItem(MenuRoot + "Detective Mode/Privacy & Data Management", false, 50)]
        public static void OpenPrivacyManager()
        {
            string status =
                "╔════════════════════════════════════════╗\n" +
                "║   🔐 DETECTIVE MODE PRIVACY MANAGER   ║\n" +
                "╚════════════════════════════════════════╝\n\n" +

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
                "YOUR DATA, YOUR CHOICE:\n" +
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" +

                "🔒 LOCAL BY DEFAULT\n" +
                "   All debugging data stored on your machine\n" +
                "   knowledge_base.db contains your solutions\n\n" +

                "💾 BACKUP OPTIONS\n" +
                "   • Full Personal Backup (PRIVATE)\n" +
                "   • Anonymized Community Insights\n" +
                "   • Solutions Export (project details stripped)\n\n" +

                "🌐 COMMUNITY SHARING (Optional)\n" +
                "   Share anonymized debugging patterns\n" +
                "   Help other Unity devs WITHOUT exposing code\n\n" +

                "🤝 NDA/CORPORATE FRIENDLY\n" +
                "   Can't share due to NDA? That's fine!\n" +
                "   Detective Mode works 100% offline\n\n" +

                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" +

                "Use menu options to:\n" +
                "• Backup your personal data\n" +
                "• Export shareable insights\n" +
                "• View privacy guidelines\n" +
                "• Access documentation";

            EditorUtility.DisplayDialog("Privacy & Data Management", status, "Got it!");
        }

        [MenuItem(MenuRoot + "Detective Mode/Backup Personal Data", false, 51)]
        public static void BackupPersonalData()
        {
            string savePath = EditorUtility.SaveFilePanel(
                "Backup Personal Detective Mode Data",
                "",
                "detective_mode_backup.json",
                "json"
            );

            if (string.IsNullOrEmpty(savePath))
            {
                Debug.Log("[Detective Mode] Backup cancelled");
                return;
            }

            bool confirmed = EditorUtility.DisplayDialog(
                "Confirm Personal Backup",
                "⚠️  WARNING: This file will contain:\n\n" +
                "   • Your file paths\n" +
                "   • Your error messages\n" +
                "   • Your notes and observations\n" +
                "   • Project-specific data\n\n" +
                "🔒 FOR LOCAL BACKUP ONLY - DO NOT UPLOAD!\n\n" +
                "Continue with backup?",
                "Yes, Backup My Data",
                "Cancel"
            );

            if (!confirmed) return;

            try
            {
                // Run Python export command
                string pythonCmd = $"python Assets/Synthesis_AI/detective_mode.py --export-personal \"{savePath}\"";
                Debug.Log($"[Detective Mode] Running: {pythonCmd}");

                System.Diagnostics.Process process = new System.Diagnostics.Process();
                process.StartInfo.FileName = "python";
                process.StartInfo.Arguments = $"Assets/Synthesis_AI/detective_mode.py --export-personal \"{savePath}\"";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;
                process.Start();
                process.WaitForExit();

                if (process.ExitCode == 0)
                {
                    EditorUtility.DisplayDialog(
                        "Backup Complete!",
                        $"✅ Personal data backed up successfully!\n\n" +
                        $"📁 Location: {savePath}\n\n" +
                        $"🔒 Remember: This file is PRIVATE\n" +
                        $"   Keep it secure, local backups only!",
                        "Awesome!"
                    );
                }
                else
                {
                    string error = process.StandardError.ReadToEnd();
                    Debug.LogError($"[Detective Mode] Backup failed: {error}");
                    EditorUtility.DisplayDialog("Backup Failed", $"Error: {error}", "OK");
                }
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Detective Mode] Backup exception: {e.Message}");
                EditorUtility.DisplayDialog("Backup Error",
                    "Could not run Detective Mode export.\n\n" +
                    "Make sure Python is installed and detective_mode.py is accessible.",
                    "OK");
            }
        }

        [MenuItem(MenuRoot + "Detective Mode/Export Shareable Insights", false, 52)]
        public static void ExportShareableInsights()
        {
            bool confirmed = EditorUtility.DisplayDialog(
                "Export Shareable Community Insights?",
                "This will export ANONYMIZED data:\n\n" +
                "✅ Safe to share:\n" +
                "   • AI confidence scores (aggregate)\n" +
                "   • Hallucination patterns\n" +
                "   • Error type statistics\n" +
                "   • Provider performance (aggregate)\n\n" +
                "❌ NOT included:\n" +
                "   • Your file paths\n" +
                "   • Your notes\n" +
                "   • Project names\n" +
                "   • Specific error messages\n\n" +
                "Continue?",
                "Yes, Export Insights",
                "Cancel"
            );

            if (!confirmed) return;

            string savePath = EditorUtility.SaveFilePanel(
                "Export Community Insights",
                "",
                "community_insights.json",
                "json"
            );

            if (string.IsNullOrEmpty(savePath)) return;

            try
            {
                System.Diagnostics.Process process = new System.Diagnostics.Process();
                process.StartInfo.FileName = "python";
                process.StartInfo.Arguments = $"Assets/Synthesis_AI/detective_mode.py --export-shareable \"{savePath}\"";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.CreateNoWindow = true;
                process.Start();
                process.WaitForExit();

                if (process.ExitCode == 0)
                {
                    EditorUtility.DisplayDialog(
                        "Export Complete!",
                        $"✅ Community insights exported!\n\n" +
                        $"📁 Location: {savePath}\n\n" +
                        $"🌐 This file is SAFE to share with the community\n" +
                        $"   All project-specific data removed!",
                        "Awesome!"
                    );
                }
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Detective Mode] Export exception: {e.Message}");
            }
        }

        [MenuItem(MenuRoot + "Detective Mode/Export Anonymized Solutions", false, 53)]
        public static void ExportAnonymizedSolutions()
        {
            bool confirmed = EditorUtility.DisplayDialog(
                "Export Anonymized Solutions?",
                "This will export debugging solutions with:\n\n" +
                "✅ Kept:\n" +
                "   • General error patterns\n" +
                "   • Generic solutions\n" +
                "   • Debugging approaches\n\n" +
                "❌ Removed:\n" +
                "   • Your file paths\n" +
                "   • Your variable names → 'variableName'\n" +
                "   • Your class names → 'ClassName'\n" +
                "   • Project-specific code\n\n" +
                "Safe to share with the community!\n\n" +
                "Continue?",
                "Yes, Export Solutions",
                "Cancel"
            );

            if (!confirmed) return;

            string savePath = EditorUtility.SaveFilePanel(
                "Export Anonymized Solutions",
                "",
                "community_solutions.json",
                "json"
            );

            if (string.IsNullOrEmpty(savePath)) return;

            try
            {
                System.Diagnostics.Process process = new System.Diagnostics.Process();
                process.StartInfo.FileName = "python";
                process.StartInfo.Arguments = $"Assets/Synthesis_AI/detective_mode.py --export-solutions \"{savePath}\"";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.CreateNoWindow = true;
                process.Start();
                process.WaitForExit();

                if (process.ExitCode == 0)
                {
                    EditorUtility.DisplayDialog(
                        "Export Complete!",
                        $"✅ Anonymized solutions exported!\n\n" +
                        $"📁 Location: {savePath}\n\n" +
                        $"🌐 Safe to share - project details stripped!",
                        "Awesome!"
                    );
                }
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Detective Mode] Export exception: {e.Message}");
            }
        }

        [MenuItem(MenuRoot + "Detective Mode/Documentation/Privacy Guidelines", false, 54)]
        public static void OpenPrivacyGuidelines()
        {
            string path = "Assets/Synthesis_AI/DETECTIVE_MODE_AI_GUIDELINES.md";
            var doc = AssetDatabase.LoadAssetAtPath<TextAsset>(path);
            if (doc != null)
            {
                EditorGUIUtility.PingObject(doc);
                Selection.activeObject = doc;

                EditorUtility.DisplayDialog(
                    "AI Privacy Guidelines",
                    "📜 Opening AI Privacy Guidelines...\n\n" +
                    "This document explains:\n" +
                    "   • What data is private vs shareable\n" +
                    "   • How anonymization works\n" +
                    "   • Guidelines for AI developers\n" +
                    "   • Privacy-first architecture\n\n" +
                    "These guidelines respect both user privacy\n" +
                    "and AI developer autonomy.",
                    "Got it!"
                );
            }
            else
            {
                Debug.LogWarning($"[Detective Mode] Privacy guidelines not found: {path}");
                EditorUtility.DisplayDialog("File Not Found",
                    "Privacy guidelines document not found.\n\n" +
                    "Expected location:\n" + path,
                    "OK");
            }
        }

        [MenuItem(MenuRoot + "Detective Mode/Documentation/Feature Overview", false, 55)]
        public static void OpenDetectiveModeOverview()
        {
            string path = "Assets/Synthesis_AI/AI_CONFIDENCE_FEATURE.md";
            var doc = AssetDatabase.LoadAssetAtPath<TextAsset>(path);
            if (doc != null)
            {
                EditorGUIUtility.PingObject(doc);
                Selection.activeObject = doc;
            }
            else
            {
                Debug.LogWarning($"[Detective Mode] Feature docs not found: {path}");
            }
        }

        [MenuItem(MenuRoot + "Detective Mode/Documentation/Usage Guide", false, 56)]
        public static void OpenDetectiveModeUsage()
        {
            string path = "Assets/Synthesis_AI/DETECTIVE_MODE_USAGE.md";
            var doc = AssetDatabase.LoadAssetAtPath<TextAsset>(path);
            if (doc != null)
            {
                EditorGUIUtility.PingObject(doc);
                Selection.activeObject = doc;
            }
            else
            {
                Debug.LogWarning($"[Detective Mode] Usage docs not found: {path}");
            }
        }

        [MenuItem(MenuRoot + "Detective Mode/View Confidence Report", false, 57)]
        public static void ViewConfidenceReport()
        {
            EditorUtility.DisplayDialog(
                "View AI Confidence Report",
                "To view the AI confidence report, run:\n\n" +
                "python Assets/Synthesis_AI/detective_mode.py --confidence-report\n\n" +
                "This shows:\n" +
                "   • AI accuracy by error type\n" +
                "   • Hallucination patterns\n" +
                "   • Provider performance\n" +
                "   • Success rates\n\n" +
                "Open your terminal and run the command above.",
                "Got it!"
            );
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
