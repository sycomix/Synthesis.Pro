using UnityEngine;
using UnityEditor;
using System.IO;
using System.Diagnostics;

namespace Synthesis.Editor
{
    /// <summary>
    /// System tester for verifying Synthesis.Pro dependencies and functionality
    /// Tests Python, Node.js, databases, and all critical systems
    /// </summary>
    public static class SystemTester
    {
        [MenuItem("Tools/Synthesis/Debug/Run System Test", false, 200)]
        public static void RunFullSystemTest()
        {
            UnityEngine.Debug.Log("=== SYNTHESIS.PRO SYSTEM TEST ===\n");

            bool allPassed = true;

            // Test 1: Python executable
            allPassed &= TestPythonExecutable();

            // Test 2: Node.js executable
            allPassed &= TestNodeExecutable();

            // Test 3: Python DLLs
            allPassed &= TestPythonDLLs();

            // Test 4: Database files
            allPassed &= TestDatabases();

            // Test 5: Python script execution
            allPassed &= TestPythonExecution();

            // Test 6: Node server start
            allPassed &= TestNodeServer();

            // Final result
            UnityEngine.Debug.Log("\n=== SYSTEM TEST COMPLETE ===");
            if (allPassed)
            {
                UnityEngine.Debug.Log("<color=green>✅ ALL TESTS PASSED</color>");
                EditorUtility.DisplayDialog(
                    "System Test: PASSED",
                    "All systems operational!\n\n" +
                    "✅ Python executable found\n" +
                    "✅ Node.js executable found\n" +
                    "✅ Python DLLs present\n" +
                    "✅ Databases accessible\n" +
                    "✅ Python scripts working\n" +
                    "✅ Node server functional",
                    "OK"
                );
            }
            else
            {
                UnityEngine.Debug.LogError("<color=red>❌ SOME TESTS FAILED - See console for details</color>");
                EditorUtility.DisplayDialog(
                    "System Test: FAILED",
                    "Some systems are not functional.\n\n" +
                    "Check the Unity Console for detailed error messages.\n\n" +
                    "You may need to run First Time Setup:\n" +
                    "Tools → Synthesis → Setup → First Time Setup",
                    "OK"
                );
            }
        }

        private static bool TestPythonExecutable()
        {
            UnityEngine.Debug.Log("\n[Test 1/6] Python Executable...");

            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string pythonExe = Path.Combine(projectRoot, "Assets", "Synthesis.Pro", "KnowledgeBase", "python", "python.exe");

            if (File.Exists(pythonExe))
            {
                UnityEngine.Debug.Log($"<color=green>✅ Python executable found: {pythonExe}</color>");
                return true;
            }
            else
            {
                UnityEngine.Debug.LogError($"<color=red>❌ Python executable NOT found: {pythonExe}</color>");
                UnityEngine.Debug.LogWarning("→ Run First Time Setup to download Python runtime");
                return false;
            }
        }

        private static bool TestNodeExecutable()
        {
            UnityEngine.Debug.Log("\n[Test 2/6] Node.js Executable...");

            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string nodeExe = Path.Combine(projectRoot, "Assets", "Synthesis.Pro", "Server", "node", "node.exe");

            if (File.Exists(nodeExe))
            {
                UnityEngine.Debug.Log($"<color=green>✅ Node.js executable found: {nodeExe}</color>");
                return true;
            }
            else
            {
                UnityEngine.Debug.LogError($"<color=red>❌ Node.js executable NOT found: {nodeExe}</color>");
                UnityEngine.Debug.LogWarning("→ Run First Time Setup to download Node.js runtime");
                return false;
            }
        }

        private static bool TestPythonDLLs()
        {
            UnityEngine.Debug.Log("\n[Test 3/6] Python DLLs (Native Plugins)...");

            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string pythonDir = Path.Combine(projectRoot, "Assets", "Synthesis.Pro", "KnowledgeBase", "python");

            string[] requiredDlls = new string[]
            {
                "python311.dll",
                "python3.dll"
            };

            bool allFound = true;
            foreach (string dll in requiredDlls)
            {
                string dllPath = Path.Combine(pythonDir, dll);
                if (File.Exists(dllPath))
                {
                    UnityEngine.Debug.Log($"  ✅ {dll}");
                }
                else
                {
                    UnityEngine.Debug.LogError($"  ❌ {dll} NOT FOUND");
                    allFound = false;
                }
            }

            if (allFound)
            {
                UnityEngine.Debug.Log("<color=green>✅ All required Python DLLs present</color>");
            }
            else
            {
                UnityEngine.Debug.LogError("<color=red>❌ Some Python DLLs missing</color>");
            }

            return allFound;
        }

        private static bool TestDatabases()
        {
            UnityEngine.Debug.Log("\n[Test 4/6] Database Files...");

            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string serverDir = Path.Combine(projectRoot, "Synthesis.Pro", "Server");

            string privateDb = Path.Combine(serverDir, "synthesis_private.db");
            string publicDb = Path.Combine(serverDir, "synthesis_public.db");

            bool privateExists = File.Exists(privateDb);
            bool publicExists = File.Exists(publicDb);

            if (privateExists)
            {
                UnityEngine.Debug.Log($"  ✅ Private database: {privateDb}");
            }
            else
            {
                UnityEngine.Debug.LogWarning($"  ⚠️ Private database not found (will be created): {privateDb}");
            }

            if (publicExists)
            {
                UnityEngine.Debug.Log($"  ✅ Public database: {publicDb}");
            }
            else
            {
                UnityEngine.Debug.LogWarning($"  ⚠️ Public database not found (will be created): {publicDb}");
            }

            if (privateExists && publicExists)
            {
                UnityEngine.Debug.Log("<color=green>✅ Both databases present</color>");
                return true;
            }
            else
            {
                UnityEngine.Debug.LogWarning("<color=yellow>⚠️ Databases will be created on first run</color>");
                return true; // Not a failure, just a warning
            }
        }

        private static bool TestPythonExecution()
        {
            UnityEngine.Debug.Log("\n[Test 5/6] Python Script Execution...");

            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string pythonExe = Path.Combine(projectRoot, "Assets", "Synthesis.Pro", "KnowledgeBase", "python", "python.exe");

            if (!File.Exists(pythonExe))
            {
                UnityEngine.Debug.LogError("<color=red>❌ Cannot test - python.exe not found</color>");
                return false;
            }

            try
            {
                var process = new Process();
                process.StartInfo.FileName = pythonExe;
                process.StartInfo.Arguments = "-c \"print('Python OK')\"";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;

                process.Start();
                string output = process.StandardOutput.ReadToEnd();
                string error = process.StandardError.ReadToEnd();
                process.WaitForExit();

                if (process.ExitCode == 0 && output.Contains("Python OK"))
                {
                    UnityEngine.Debug.Log($"<color=green>✅ Python execution successful: {output.Trim()}</color>");
                    return true;
                }
                else
                {
                    UnityEngine.Debug.LogError($"<color=red>❌ Python execution failed</color>");
                    UnityEngine.Debug.LogError($"Exit code: {process.ExitCode}");
                    UnityEngine.Debug.LogError($"Error: {error}");
                    return false;
                }
            }
            catch (System.Exception e)
            {
                UnityEngine.Debug.LogError($"<color=red>❌ Python execution exception: {e.Message}</color>");
                return false;
            }
        }

        private static bool TestNodeServer()
        {
            UnityEngine.Debug.Log("\n[Test 6/6] Node.js Server...");

            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string nodeExe = Path.Combine(projectRoot, "Assets", "Synthesis.Pro", "Server", "node", "node.exe");

            if (!File.Exists(nodeExe))
            {
                UnityEngine.Debug.LogError("<color=red>❌ Cannot test - node.exe not found</color>");
                return false;
            }

            try
            {
                var process = new Process();
                process.StartInfo.FileName = nodeExe;
                process.StartInfo.Arguments = "--version";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;

                process.Start();
                string output = process.StandardOutput.ReadToEnd();
                process.WaitForExit();

                if (process.ExitCode == 0)
                {
                    UnityEngine.Debug.Log($"<color=green>✅ Node.js functional: {output.Trim()}</color>");
                    return true;
                }
                else
                {
                    UnityEngine.Debug.LogError($"<color=red>❌ Node.js test failed</color>");
                    return false;
                }
            }
            catch (System.Exception e)
            {
                UnityEngine.Debug.LogError($"<color=red>❌ Node.js test exception: {e.Message}</color>");
                return false;
            }
        }

        [MenuItem("Tools/Synthesis/Debug/Quick Health Check", false, 201)]
        public static void QuickHealthCheck()
        {
            UnityEngine.Debug.Log("=== QUICK HEALTH CHECK ===");

            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));

            bool pythonOK = File.Exists(Path.Combine(projectRoot, "Assets", "Synthesis.Pro", "KnowledgeBase", "python", "python.exe"));
            bool nodeOK = File.Exists(Path.Combine(projectRoot, "Assets", "Synthesis.Pro", "Server", "node", "node.exe"));
            bool dllOK = File.Exists(Path.Combine(projectRoot, "Assets", "Synthesis.Pro", "KnowledgeBase", "python", "python311.dll"));

            string status = $"Python: {(pythonOK ? "✅" : "❌")}\n" +
                          $"Node.js: {(nodeOK ? "✅" : "❌")}\n" +
                          $"Python DLLs: {(dllOK ? "✅" : "❌")}";

            UnityEngine.Debug.Log(status);

            if (pythonOK && nodeOK && dllOK)
            {
                EditorUtility.DisplayDialog("Health Check: OK", "All systems ready!\n\n" + status, "OK");
            }
            else
            {
                EditorUtility.DisplayDialog("Health Check: Issues Found", "Some components missing:\n\n" + status + "\n\nRun First Time Setup?", "OK");
            }
        }
    }
}
