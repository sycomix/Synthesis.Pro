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
        [MenuItem("Synthesis/Restart WebSocket Server", false, 150)]
        public static void RestartWebSocketServer()
        {
            Debug.Log("[Synthesis] Restarting WebSocket server...");

            // Stop server
            SynLinkWebSocket.StopWebSocketServer();

            // Wait a moment for port to be released
            System.Threading.Thread.Sleep(500);

            // Restart server
            SynLinkWebSocket.StartWebSocketServer();

            int wsPort = SynLinkWebSocket.GetActualPort();
            EditorUtility.DisplayDialog("WebSocket Server Restarted",
                "Synthesis.Pro WebSocket server has been restarted.\n\n" +
                $"Server available on: localhost:{wsPort}",
                "OK");
        }

        [MenuItem("Synthesis/Check Server Status", false, 151)]
        public static void CheckServerStatus()
        {
            bool wsRunning = SynLinkWebSocket.IsRunning();
            int wsPort = SynLinkWebSocket.GetActualPort();

            string message = "Synthesis.Pro Server Status:\n\n";
            message += (wsRunning ? "[OK]" : "[ERROR]") + $" WebSocket Server (port {wsPort})\n\n";
            
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
