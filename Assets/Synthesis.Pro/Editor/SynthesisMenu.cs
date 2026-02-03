using UnityEngine;
using UnityEditor;
using System.IO;

namespace Synthesis.Editor
{
    /// <summary>
    /// Synthesis menu items for quick access to features and documentation
    /// </summary>
    public static class SynthesisMenu
    {
        [MenuItem("Tools/Synthesis/Restart MCP Servers", false, 150)]
        public static void RestartMCPServers()
        {
            Debug.Log("[Synthesis] Restarting MCP servers...");
            
            // Stop servers
            SynLinkEditor.StopHTTPServer();
            SynLinkWebSocket.StopWebSocketServer();
            
            // Wait a moment for ports to be released
            System.Threading.Thread.Sleep(500);
            
            // Restart servers
            SynLinkEditor.StartHTTPServer();
            SynLinkWebSocket.StartWebSocketServer();
            
            int wsPort = SynLinkWebSocket.GetActualPort();
            EditorUtility.DisplayDialog("MCP Servers Restarted",
                "SynLink HTTP and WebSocket servers have been restarted.\n\n" +
                "Servers should now be available on:\n" +
                "• HTTP: localhost:9765\n" +
                $"• WebSocket: localhost:{wsPort}",
                "OK");
        }
        
        [MenuItem("Tools/Synthesis/Check MCP Server Status", false, 151)]
        public static void CheckMCPServerStatus()
        {
            bool httpRunning = SynLinkEditor.IsConnected();
            bool wsRunning = SynLinkWebSocket.IsRunning();
            int wsPort = SynLinkWebSocket.GetActualPort();

            string message = "MCP Server Status:\n\n";
            message += (httpRunning ? "✅" : "❌") + " HTTP Server (port 9765)\n";
            message += (wsRunning ? "✅" : "❌") + $" WebSocket Server (port {wsPort})\n\n";
            
            if (httpRunning && wsRunning)
            {
                message += "All systems operational! ✅\n\n" +
                          "You can now use MCP commands from Cursor.";
            }
            else
            {
                message += "One or more servers not running! ❌\n\n" +
                          "Try: Synthesis → Restart MCP Servers";
            }
            
            EditorUtility.DisplayDialog("MCP Server Status", message, "OK");
        }
        
        private static void OpenMarkdownFile(string relativePath)
        {
            if (File.Exists(relativePath))
            {
                // Try to open with default markdown editor
                try
                {
                    System.Diagnostics.Process.Start(relativePath);
                }
                catch
                {
                    // Fallback: reveal in file explorer
                    EditorUtility.RevealInFinder(relativePath);
                }
            }
            else
            {
                EditorUtility.DisplayDialog("File Not Found",
                    $"Documentation file not found:\n\n{relativePath}",
                    "OK");
            }
        }
    }
}
