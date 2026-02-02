using UnityEngine;
using UnityEditor;
using System;
using System.Diagnostics;
using System.IO;

namespace Synthesis.Editor
{
    /// <summary>
    /// Manages the chat watcher process that monitors Unity for chat messages
    /// Starts automatically, runs in background, integrates cleanly
    /// </summary>
    [InitializeOnLoad]
    public static class SynthesisChatWatcher
    {
        private static Process watcherProcess;
        private static bool isWatcherRunning = false;
        private static readonly string pythonPath;
        private static readonly string watcherScriptPath;
        
        static SynthesisChatWatcher()
        {
            // Setup paths
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            pythonPath = Path.Combine(projectRoot, "KnowledgeBase", "python", "python.exe");
            watcherScriptPath = Path.Combine(Application.dataPath, "Synthesis_AI", "chat_watcher.py");
            
            // Start watcher automatically when Unity opens
            EditorApplication.delayCall += () =>
            {
                if (EditorPrefs.GetBool("Synthesis.AutoStartChatWatcher", true))
                {
                    StartWatcher();
                }
            };
            
            // Stop watcher when Unity closes
            EditorApplication.quitting += StopWatcher;
        }
        
        public static bool IsWatcherRunning()
        {
            if (watcherProcess == null) return false;
            
            try
            {
                // Check if process is still alive
                return !watcherProcess.HasExited;
            }
            catch
            {
                return false;
            }
        }
        
        public static void EnsureWatcherRunning()
        {
            if (!IsWatcherRunning())
            {
                StartWatcher();
            }
        }
        
        public static void StartWatcher()
        {
            // Stop existing watcher if running
            if (IsWatcherRunning())
            {
                UnityEngine.Debug.LogWarning("[Synthesis] Chat Watcher already running");
                return;
            }
            
            // Check if Python exists
            if (!File.Exists(pythonPath))
            {
                UnityEngine.Debug.LogError($"[Synthesis] Python not found at: {pythonPath}\n" +
                    "Please run KnowledgeBase/setup_kb.bat first");
                
                EditorUtility.DisplayDialog(
                    "Python Not Found",
                    "Chat Watcher requires Python from the Knowledge Base.\n\n" +
                    "Please run: KnowledgeBase/setup_kb.bat\n\n" +
                    "This will install embedded Python (no system install needed).",
                    "OK"
                );
                return;
            }
            
            // Check if watcher script exists
            if (!File.Exists(watcherScriptPath))
            {
                UnityEngine.Debug.LogError($"[Synthesis] Watcher script not found at: {watcherScriptPath}");
                return;
            }
            
            try
            {
                // Start the watcher process
                var startInfo = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = $"\"{watcherScriptPath}\"",
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    WorkingDirectory = Path.GetDirectoryName(watcherScriptPath)
                };
                
                watcherProcess = new Process { StartInfo = startInfo };
                
                // Log output for debugging
                watcherProcess.OutputDataReceived += (sender, e) =>
                {
                    if (!string.IsNullOrEmpty(e.Data))
                    {
                        UnityEngine.Debug.Log($"[Chat Watcher] {e.Data}");
                    }
                };
                
                watcherProcess.ErrorDataReceived += (sender, e) =>
                {
                    if (!string.IsNullOrEmpty(e.Data))
                    {
                        UnityEngine.Debug.LogWarning($"[Chat Watcher] {e.Data}");
                    }
                };
                
                watcherProcess.Start();
                watcherProcess.BeginOutputReadLine();
                watcherProcess.BeginErrorReadLine();
                
                isWatcherRunning = true;
                
                UnityEngine.Debug.Log("[Synthesis] ✅ Chat Watcher started automatically!");
                UnityEngine.Debug.Log("[Synthesis] AI will be notified when you send chat messages");
            }
            catch (Exception e)
            {
                UnityEngine.Debug.LogError($"[Synthesis] Failed to start Chat Watcher: {e.Message}");
            }
        }
        
        public static void StopWatcher()
        {
            if (watcherProcess == null) return;
            
            try
            {
                if (!watcherProcess.HasExited)
                {
                    watcherProcess.Kill();
                    watcherProcess.WaitForExit(2000);
                }
                
                watcherProcess.Dispose();
                watcherProcess = null;
                isWatcherRunning = false;
                
                UnityEngine.Debug.Log("[Synthesis] Chat Watcher stopped");
            }
            catch (Exception e)
            {
                UnityEngine.Debug.LogWarning($"[Synthesis] Error stopping watcher: {e.Message}");
            }
        }
        
        [MenuItem("Synthesis/Advanced/Toggle Auto-Start Chat Watcher")]
        public static void ToggleAutoStart()
        {
            bool current = EditorPrefs.GetBool("Synthesis.AutoStartChatWatcher", true);
            EditorPrefs.SetBool("Synthesis.AutoStartChatWatcher", !current);
            
            string status = !current ? "ENABLED" : "DISABLED";
            UnityEngine.Debug.Log($"[Synthesis] Auto-start Chat Watcher: {status}");
            
            EditorUtility.DisplayDialog(
                "Chat Watcher Auto-Start",
                $"Auto-start is now: {status}\n\n" +
                (current ? "Watcher will NOT start automatically when Unity opens." : "Watcher will start automatically when Unity opens."),
                "OK"
            );
        }
    }
}
