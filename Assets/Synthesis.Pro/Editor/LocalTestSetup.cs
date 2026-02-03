using UnityEngine;
using UnityEditor;
using System.IO;

namespace Synthesis.Editor
{
    /// <summary>
    /// LOCAL TESTING ONLY - Manually setup executables for testing
    /// This bypasses the download system for local development
    /// </summary>
    public static class LocalTestSetup
    {
        [MenuItem("Tools/Synthesis/Debug/Local Test Setup", false, 210)]
        public static void RunLocalSetup()
        {
            bool confirm = EditorUtility.DisplayDialog(
                "Local Test Setup",
                "This will help you manually setup executables for local testing.\n\n" +
                "You'll need to provide paths to:\n" +
                "• Python embedded runtime folder\n" +
                "• Node.js executable\n\n" +
                "This is for TESTING ONLY - production uses download-on-demand.\n\n" +
                "Continue?",
                "Yes",
                "Cancel"
            );

            if (!confirm) return;

            SetupPythonRuntime();
            SetupNodeRuntime();

            EditorUtility.DisplayDialog(
                "Setup Complete",
                "Local test setup complete!\n\n" +
                "Run 'Tools → Synthesis → Debug → Run System Test' to verify.",
                "OK"
            );
        }

        private static void SetupPythonRuntime()
        {
            string targetDir = Path.Combine(Application.dataPath, "Synthesis.Pro", "KnowledgeBase", "python");

            if (Directory.Exists(targetDir) && File.Exists(Path.Combine(targetDir, "python.exe")))
            {
                bool overwrite = EditorUtility.DisplayDialog(
                    "Python Runtime Exists",
                    $"Python runtime already exists at:\n{targetDir}\n\nOverwrite?",
                    "Yes",
                    "Skip"
                );

                if (!overwrite)
                {
                    Debug.Log("[LocalTestSetup] Skipping Python setup");
                    return;
                }
            }

            string sourceDir = EditorUtility.OpenFolderPanel(
                "Select Python Embedded Runtime Folder",
                "",
                ""
            );

            if (string.IsNullOrEmpty(sourceDir))
            {
                Debug.LogWarning("[LocalTestSetup] Python setup cancelled");
                return;
            }

            // Verify it's a valid Python runtime
            if (!File.Exists(Path.Combine(sourceDir, "python.exe")))
            {
                EditorUtility.DisplayDialog(
                    "Invalid Python Runtime",
                    "Selected folder doesn't contain python.exe\n\nPlease select a valid Python embedded runtime folder.",
                    "OK"
                );
                return;
            }

            try
            {
                // Create target directory
                Directory.CreateDirectory(targetDir);

                // Copy all files and folders
                CopyDirectory(sourceDir, targetDir, true);

                Debug.Log($"[LocalTestSetup] ✅ Python runtime copied to {targetDir}");
                EditorUtility.DisplayDialog(
                    "Python Setup Complete",
                    $"Python runtime copied successfully!\n\nLocation: {targetDir}",
                    "OK"
                );
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[LocalTestSetup] Python setup failed: {e.Message}");
                EditorUtility.DisplayDialog(
                    "Setup Failed",
                    $"Failed to copy Python runtime:\n\n{e.Message}",
                    "OK"
                );
            }
        }

        private static void SetupNodeRuntime()
        {
            string targetDir = Path.Combine(Application.dataPath, "Synthesis.Pro", "Server", "node");
            string targetFile = Path.Combine(targetDir, "node.exe");

            if (File.Exists(targetFile))
            {
                bool overwrite = EditorUtility.DisplayDialog(
                    "Node.js Exists",
                    $"Node.js already exists at:\n{targetFile}\n\nOverwrite?",
                    "Yes",
                    "Skip"
                );

                if (!overwrite)
                {
                    Debug.Log("[LocalTestSetup] Skipping Node.js setup");
                    return;
                }
            }

            string sourceFile = EditorUtility.OpenFilePanel(
                "Select node.exe",
                "",
                "exe"
            );

            if (string.IsNullOrEmpty(sourceFile))
            {
                Debug.LogWarning("[LocalTestSetup] Node.js setup cancelled");
                return;
            }

            // Verify it's node.exe
            if (!Path.GetFileName(sourceFile).Equals("node.exe", System.StringComparison.OrdinalIgnoreCase))
            {
                EditorUtility.DisplayDialog(
                    "Invalid File",
                    "Please select node.exe",
                    "OK"
                );
                return;
            }

            try
            {
                // Create target directory
                Directory.CreateDirectory(targetDir);

                // Copy node.exe
                File.Copy(sourceFile, targetFile, true);

                Debug.Log($"[LocalTestSetup] ✅ Node.js copied to {targetFile}");
                EditorUtility.DisplayDialog(
                    "Node.js Setup Complete",
                    $"Node.js copied successfully!\n\nLocation: {targetFile}",
                    "OK"
                );
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[LocalTestSetup] Node.js setup failed: {e.Message}");
                EditorUtility.DisplayDialog(
                    "Setup Failed",
                    $"Failed to copy Node.js:\n\n{e.Message}",
                    "OK"
                );
            }
        }

        private static void CopyDirectory(string sourceDir, string targetDir, bool recursive)
        {
            var dir = new DirectoryInfo(sourceDir);

            if (!dir.Exists)
                throw new DirectoryNotFoundException($"Source directory not found: {sourceDir}");

            DirectoryInfo[] dirs = dir.GetDirectories();

            // Create the destination directory
            Directory.CreateDirectory(targetDir);

            // Copy files
            foreach (FileInfo file in dir.GetFiles())
            {
                string targetFilePath = Path.Combine(targetDir, file.Name);
                file.CopyTo(targetFilePath, true);
            }

            // Copy subdirectories
            if (recursive)
            {
                foreach (DirectoryInfo subDir in dirs)
                {
                    string newTargetDir = Path.Combine(targetDir, subDir.Name);
                    CopyDirectory(subDir.FullName, newTargetDir, true);
                }
            }
        }

        [MenuItem("Tools/Synthesis/Debug/Show Runtime Paths", false, 211)]
        public static void ShowRuntimePaths()
        {
            string pythonPath = Path.Combine(Application.dataPath, "Synthesis.Pro", "KnowledgeBase", "python", "python.exe");
            string nodePath = Path.Combine(Application.dataPath, "Synthesis.Pro", "Server", "node", "node.exe");

            bool pythonExists = File.Exists(pythonPath);
            bool nodeExists = File.Exists(nodePath);

            string message = "Runtime Paths:\n\n";
            message += $"Python: {(pythonExists ? "✅" : "❌")}\n{pythonPath}\n\n";
            message += $"Node.js: {(nodeExists ? "✅" : "❌")}\n{nodePath}";

            Debug.Log($"[LocalTestSetup]\n{message}");
            EditorUtility.DisplayDialog("Runtime Paths", message, "OK");
        }

        [MenuItem("Tools/Synthesis/Debug/Clean Runtime Files", false, 212)]
        public static void CleanRuntimeFiles()
        {
            bool confirm = EditorUtility.DisplayDialog(
                "Clean Runtime Files?",
                "This will DELETE all runtime files:\n" +
                "• Python runtime\n" +
                "• Node.js runtime\n\n" +
                "This is useful for testing fresh setup.\n\n" +
                "Continue?",
                "Yes, Delete",
                "Cancel"
            );

            if (!confirm) return;

            try
            {
                string pythonDir = Path.Combine(Application.dataPath, "Synthesis.Pro", "KnowledgeBase", "python");
                string nodeDir = Path.Combine(Application.dataPath, "Synthesis.Pro", "Server", "node");

                int filesDeleted = 0;

                if (Directory.Exists(pythonDir))
                {
                    Directory.Delete(pythonDir, true);
                    filesDeleted++;
                    Debug.Log($"[LocalTestSetup] Deleted Python runtime from {pythonDir}");
                }

                if (Directory.Exists(nodeDir))
                {
                    Directory.Delete(nodeDir, true);
                    filesDeleted++;
                    Debug.Log($"[LocalTestSetup] Deleted Node.js runtime from {nodeDir}");
                }

                if (filesDeleted == 0)
                {
                    EditorUtility.DisplayDialog(
                        "Nothing to Clean",
                        "No runtime files found to delete.",
                        "OK"
                    );
                }
                else
                {
                    EditorUtility.DisplayDialog(
                        "Clean Complete",
                        $"Deleted {filesDeleted} runtime folder(s).\n\n" +
                        "Run Local Test Setup to restore them.",
                        "OK"
                    );
                }
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[LocalTestSetup] Clean failed: {e.Message}");
                EditorUtility.DisplayDialog(
                    "Clean Failed",
                    $"Error cleaning runtime files:\n\n{e.Message}",
                    "OK"
                );
            }
        }
    }
}
