using UnityEngine;
using UnityEditor;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;

namespace Synthesis.Editor
{
    /// <summary>
    /// Runs automatic setup on first import
    /// Initializes databases, downloads embeds, and configures system
    /// </summary>
    [InitializeOnLoad]
    public static class FirstTimeSetup
    {
        private const string SETUP_COMPLETE_KEY = "Synthesis.SetupComplete";
        private const string PYTHON_DOWNLOAD_URL = "https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0-runtime-deps/python-embedded.zip";
        private const string NODE_DOWNLOAD_URL = "https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0-runtime-deps/node-embedded.zip";
        private const string MODELS_DOWNLOAD_URL = "https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0-runtime-deps/models.zip";
        private static readonly HttpClient httpClient = new HttpClient();

        static FirstTimeSetup()
        {
            // CRITICAL: Ensure Newtonsoft.Json is installed FIRST before anything else
            EditorApplication.delayCall += EnsureNewtonsoftJson;

            // Check if setup already completed
            if (EditorPrefs.GetBool(SETUP_COMPLETE_KEY, false))
            {
                return;
            }

            // Delay to let Unity finish initializing
            EditorApplication.delayCall += RunFirstTimeSetup;
        }

        private static void EnsureNewtonsoftJson()
        {
            try
            {
                string manifestPath = Path.Combine(Application.dataPath, "..", "Packages", "manifest.json");

                if (!File.Exists(manifestPath))
                {
                    Debug.LogWarning("[Synthesis] Package manifest not found");
                    return;
                }

                string manifestContent = File.ReadAllText(manifestPath);

                // Check if already installed
                if (manifestContent.Contains("\"com.unity.nuget.newtonsoft-json\""))
                {
                    return; // Already installed
                }

                Debug.Log("[Synthesis] Adding Newtonsoft.Json dependency...");

                // Find the dependencies section and add Newtonsoft.Json
                int depsIndex = manifestContent.IndexOf("\"dependencies\"");
                if (depsIndex == -1)
                {
                    Debug.LogError("[Synthesis] Could not find dependencies section in manifest.json");
                    return;
                }

                int braceIndex = manifestContent.IndexOf('{', depsIndex);
                if (braceIndex == -1)
                {
                    Debug.LogError("[Synthesis] Malformed manifest.json");
                    return;
                }

                // Insert Newtonsoft.Json as first dependency
                string newtonsoftEntry = "\n    \"com.unity.nuget.newtonsoft-json\": \"3.2.1\",";
                manifestContent = manifestContent.Insert(braceIndex + 1, newtonsoftEntry);

                // Write back to file
                File.WriteAllText(manifestPath, manifestContent);

                // Force Unity to reload packages
                AssetDatabase.Refresh();

                Debug.Log("[Synthesis] ✅ Newtonsoft.Json added to project");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Synthesis] Failed to add Newtonsoft.Json: {e.Message}");
            }
        }

        private static void RunFirstTimeSetup()
        {
            Debug.Log("[Synthesis] Running first-time setup...");

            bool shouldSetup = EditorUtility.DisplayDialog(
                "Welcome to Synthesis.Pro Beta!",
                "🚧 BETA - Early Access Release\n" +
                "We're actively seeking feedback!\n\n" +
                "First-time setup required:\n" +
                "• Initialize knowledge base databases\n" +
                "• Download Python runtime (~50MB)\n" +
                "• Download Node.js runtime (~20MB)\n" +
                "• Download AI models (~200MB)\n" +
                "• Configure system\n\n" +
                "This will take a few minutes.\n\n" +
                "Continue?",
                "Yes, Set Up",
                "Later"
            );

            if (!shouldSetup)
            {
                Debug.Log("[Synthesis] Setup postponed. Run 'Synthesis > Setup > First Time Setup' when ready.");
                return;
            }

            // Run setup steps
            _ = SetupAsync(); // Fire and forget with proper error handling inside
        }

        [MenuItem("Tools/Synthesis/Setup/First Time Setup", false, 100)]
        public static void ManualSetup()
        {
            _ = SetupAsync(); // Fire and forget with proper error handling inside
        }

        private static async Task SetupAsync()
        {
            EditorUtility.DisplayProgressBar("Synthesis Setup", "Initializing...", 0.0f);

            try
            {
                // Step 1: Download Python runtime FIRST
                EditorUtility.DisplayProgressBar("Synthesis Setup", "Downloading Python runtime...", 0.2f);
                await DownloadPythonRuntime();

                // Step 2: Download Node.js runtime
                EditorUtility.DisplayProgressBar("Synthesis Setup", "Downloading Node.js runtime...", 0.3f);
                await DownloadNodeRuntime();

                // Step 3: Download models
                EditorUtility.DisplayProgressBar("Synthesis Setup", "Downloading AI models...", 0.5f);
                await DownloadModels();

                // Step 4: Initialize Python environment
                EditorUtility.DisplayProgressBar("Synthesis Setup", "Setting up Python environment...", 0.6f);
                InitializePythonEnvironment();

                // Step 5: Initialize databases (requires Python)
                EditorUtility.DisplayProgressBar("Synthesis Setup", "Creating databases...", 0.8f);
                if (!InitializeDatabases())
                {
                    throw new System.Exception("Failed to initialize databases");
                }

                // Step 6: Create initial public DB content
                EditorUtility.DisplayProgressBar("Synthesis Setup", "Creating initial content...", 0.9f);
                CreateInitialPublicContent();

                // Mark setup as complete
                EditorPrefs.SetBool(SETUP_COMPLETE_KEY, true);

                EditorUtility.ClearProgressBar();

                EditorUtility.DisplayDialog(
                    "Setup Complete!",
                    "Synthesis.Pro Beta is ready to use!\n\n" +
                    "Next steps:\n" +
                    "• Check 'Synthesis > Test Connection'\n" +
                    "• Add SynLink to your scene\n" +
                    "• Start building with AI!\n\n" +
                    "📢 Beta Feedback:\n" +
                    "github.com/Fallen-Entertainment/Synthesis.Pro/issues\n\n" +
                    "Documentation: fallen-entertainment.github.io/Synthesis.Pro",
                    "Get Started!"
                );

                Debug.Log("[Synthesis] ✅ First-time setup complete!");
            }
            catch (System.Exception e)
            {
                EditorUtility.ClearProgressBar();
                Debug.LogError($"[Synthesis] Setup failed: {e.Message}");

                EditorUtility.DisplayDialog(
                    "Setup Failed",
                    $"Setup encountered an error:\n\n{e.Message}\n\n" +
                    "You can retry via: Synthesis > Setup > First Time Setup",
                    "OK"
                );
            }
        }

        private static bool InitializeDatabases()
        {
            try
            {
                // Use Assets/Synthesis.Pro path for consistency
                string packageRoot = Path.Combine(Application.dataPath, "Synthesis.Pro");
                string serverDir = Path.Combine(packageRoot, "Server");
                string privateDbPath = Path.Combine(serverDir, "synthesis_private.db");
                string publicDbPath = Path.Combine(serverDir, "synthesis_public.db");

                // Ensure directory exists
                Directory.CreateDirectory(serverDir);

                // Run Python database initialization script
                string ragDir = Path.Combine(packageRoot, "RAG");
                string initScript = Path.Combine(ragDir, "init_databases.py");

                if (!File.Exists(initScript))
                {
                    Debug.LogWarning("[Synthesis] init_databases.py not found, creating minimal DBs");
                    CreateMinimalDatabases(privateDbPath, publicDbPath);
                    return true;
                }

                // Run init script with embedded Python
                string pythonExe = Path.Combine(Application.dataPath, "Synthesis.Pro", "KnowledgeBase", "python", "python.exe");

                var process = new System.Diagnostics.Process();
                // Use embedded Python if available, otherwise fallback to system Python
                process.StartInfo.FileName = File.Exists(pythonExe) ? pythonExe : "python";
                process.StartInfo.Arguments = $"\"{initScript}\"";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;
                process.Start();

                // Wait with timeout (30 seconds for DB init)
                if (!process.WaitForExit(30000))
                {
                    process.Kill();
                    Debug.LogError("[Synthesis] Database init timed out");
                    return false;
                }

                if (process.ExitCode != 0)
                {
                    string error = process.StandardError.ReadToEnd();
                    Debug.LogError($"[Synthesis] Database init error: {error}");
                    return false;
                }

                Debug.Log("[Synthesis] Databases initialized");
                return true;
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Synthesis] Database initialization failed: {e.Message}");
                return false;
            }
        }

        private static void CreateMinimalDatabases(string privateDbPath, string publicDbPath)
        {
            // Create minimal SQLite database files with proper format
            // This is a fallback if Python init script isn't available

            Debug.Log("[Synthesis] Creating minimal SQLite database structures");

            // SQLite database file header (first 16 bytes)
            // "SQLite format 3\0" followed by page size and other metadata
            byte[] sqliteHeader = new byte[]
            {
                0x53, 0x51, 0x4C, 0x69, 0x74, 0x65, 0x20, 0x66,  // "SQLite f"
                0x6F, 0x72, 0x6D, 0x61, 0x74, 0x20, 0x33, 0x00,  // "ormat 3\0"
                0x10, 0x00, // Page size = 4096 (0x1000)
                0x01, // File format write version
                0x01, // File format read version
                0x00, // Reserved space at end of each page
                0x40, // Maximum embedded payload fraction (64)
                0x20, // Minimum embedded payload fraction (32)
                0x20, // Leaf payload fraction (32)
                0x00, 0x00, 0x00, 0x00, // File change counter
                0x00, 0x00, 0x00, 0x00, // Size of database in pages
                0x00, 0x00, 0x00, 0x00, // First freelist trunk page
                0x00, 0x00, 0x00, 0x00, // Total number of freelist pages
                0x00, 0x00, 0x00, 0x00, // Schema cookie
                0x00, 0x00, 0x00, 0x04, // Schema format number (4)
                0x00, 0x00, 0x10, 0x00, // Default page cache size
                0x00, 0x00, 0x00, 0x00, // Largest root btree page
                0x00, 0x00, 0x00, 0x01, // Text encoding (1 = UTF-8)
                0x00, 0x00, 0x00, 0x00, // User version
                0x00, 0x00, 0x00, 0x00, // Incremental vacuum mode
                0x00, 0x00, 0x00, 0x00, // Application ID
                // Reserved space (20 bytes of zeros)
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, // Version-valid-for number
                0x00, 0x2E, 0x33, 0x38  // SQLite version number (encoded)
            };

            // Create a minimal valid SQLite file (4096 bytes - one page)
            byte[] minimalDb = new byte[4096];
            System.Array.Copy(sqliteHeader, minimalDb, sqliteHeader.Length);

            // Write the minimal databases ONLY if they don't exist
            // CRITICAL: Never overwrite existing private database - it's sacred!
            if (!File.Exists(privateDbPath))
            {
                File.WriteAllBytes(privateDbPath, minimalDb);
                Debug.Log("[Synthesis] Created minimal private database");
            }
            else
            {
                Debug.Log("[Synthesis] Private database already exists - preserving it");
            }

            if (!File.Exists(publicDbPath))
            {
                File.WriteAllBytes(publicDbPath, minimalDb);
                Debug.Log("[Synthesis] Created minimal public database");
            }
            else
            {
                Debug.Log("[Synthesis] Public database already exists - preserving it");
            }
        }

        private static async Task DownloadPythonRuntime()
        {
            string targetDir = Path.Combine(Application.dataPath, "Synthesis.Pro", "KnowledgeBase", "python");

            if (Directory.Exists(targetDir) && Directory.GetFiles(targetDir, "python.exe").Length > 0)
            {
                Debug.Log("[Synthesis] Python runtime already exists");
                return;
            }

            try
            {
                // Clean up partial installation if it exists
                if (Directory.Exists(targetDir))
                {
                    Debug.Log("[Synthesis] Cleaning up partial Python installation...");
                    Directory.Delete(targetDir, true);
                }

                httpClient.Timeout = System.TimeSpan.FromMinutes(5);

                Debug.Log("[Synthesis] Downloading Python runtime...");
                var response = await httpClient.GetAsync(PYTHON_DOWNLOAD_URL);
                if (!response.IsSuccessStatusCode)
                {
                    throw new System.Exception($"Download failed: {response.StatusCode}");
                }

                string tempDir = Path.Combine(Path.GetTempPath(), "synthesis_python_download");
                Directory.CreateDirectory(tempDir);
                var zipPath = Path.Combine(tempDir, "python-embedded.zip");

                using (var fs = new FileStream(zipPath, FileMode.Create))
                {
                    await response.Content.CopyToAsync(fs);
                }

                // Extract zip
                Directory.CreateDirectory(targetDir);
                System.IO.Compression.ZipFile.ExtractToDirectory(zipPath, targetDir);

                // Cleanup
                Directory.Delete(tempDir, true);

                Debug.Log($"[Synthesis] Python runtime downloaded to {targetDir}");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Synthesis] Python download failed: {e.Message}");
                throw;
            }
        }

        private static async Task DownloadNodeRuntime()
        {
            string targetDir = Path.Combine(Application.dataPath, "Synthesis.Pro", "Server", "node");

            if (Directory.Exists(targetDir) && Directory.GetFiles(targetDir, "node.exe").Length > 0)
            {
                Debug.Log("[Synthesis] Node.js runtime already exists");
                return;
            }

            try
            {
                httpClient.Timeout = System.TimeSpan.FromMinutes(5);

                Debug.Log("[Synthesis] Downloading Node.js runtime...");
                var response = await httpClient.GetAsync(NODE_DOWNLOAD_URL);
                if (!response.IsSuccessStatusCode)
                {
                    throw new System.Exception($"Download failed: {response.StatusCode}");
                }

                string tempDir = Path.Combine(Path.GetTempPath(), "synthesis_node_download");
                Directory.CreateDirectory(tempDir);
                var zipPath = Path.Combine(tempDir, "node-embedded.zip");

                using (var fs = new FileStream(zipPath, FileMode.Create))
                {
                    await response.Content.CopyToAsync(fs);
                }

                // Extract zip
                Directory.CreateDirectory(targetDir);
                System.IO.Compression.ZipFile.ExtractToDirectory(zipPath, targetDir);

                // Cleanup
                Directory.Delete(tempDir, true);

                Debug.Log($"[Synthesis] Node.js runtime downloaded to {targetDir}");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Synthesis] Node.js download failed: {e.Message}");
                throw;
            }
        }

        private static async Task DownloadModels()
        {
            string packageRoot = Path.Combine(Application.dataPath, "Synthesis.Pro");
            string targetDir = Path.Combine(packageRoot, "Server", "models");

            // Check for specific model file to verify complete installation
            string modelFile = Path.Combine(targetDir, "unsloth", "embeddinggemma-300m-GGUF", "embeddinggemma-300M-Q8_0.gguf");
            if (File.Exists(modelFile))
            {
                Debug.Log("[Synthesis] Models already exist");
                return;
            }

            try
            {
                // Clean up partial installation
                if (Directory.Exists(targetDir))
                {
                    Debug.Log("[Synthesis] Cleaning up partial models installation...");
                    Directory.Delete(targetDir, true);
                }

                httpClient.Timeout = System.TimeSpan.FromMinutes(10);

                var response = await httpClient.GetAsync(MODELS_DOWNLOAD_URL);
                if (!response.IsSuccessStatusCode)
                {
                    throw new System.Exception($"Download failed: {response.StatusCode}");
                }

                var zipPath = "models.zip";
                using (var fs = new FileStream(zipPath, FileMode.Create))
                {
                    await response.Content.CopyToAsync(fs);
                }

                // Extract zip
                Directory.CreateDirectory(targetDir);
                System.IO.Compression.ZipFile.ExtractToDirectory(zipPath, targetDir);
                File.Delete(zipPath);

                Debug.Log("[Synthesis] Models downloaded");
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Synthesis] Models download failed: {e.Message}. RAG features may be limited.");
            }
        }

        private static void InitializePythonEnvironment()
        {
            string pythonPath = Path.Combine(Application.dataPath, "Synthesis.Pro", "KnowledgeBase", "python", "python.exe");

            if (!File.Exists(pythonPath))
            {
                Debug.LogWarning("[Synthesis] Python runtime not found - skipping package installation");
                return;
            }

            try
            {
                // Bootstrap pip for embedded Python using get-pip.py
                Debug.Log("[Synthesis] Bootstrapping pip...");

                // Download get-pip.py
                string getPipPath = Path.Combine(Application.temporaryCachePath, "get-pip.py");
                using (var client = new System.Net.WebClient())
                {
                    client.DownloadFile("https://bootstrap.pypa.io/get-pip.py", getPipPath);
                }

                Debug.Log("[Synthesis] Downloaded get-pip.py, installing pip...");

                var getPipProcess = new System.Diagnostics.Process();
                getPipProcess.StartInfo.FileName = pythonPath;
                getPipProcess.StartInfo.Arguments = $"\"{getPipPath}\"";
                getPipProcess.StartInfo.UseShellExecute = false;
                getPipProcess.StartInfo.RedirectStandardOutput = true;
                getPipProcess.StartInfo.RedirectStandardError = true;
                getPipProcess.StartInfo.CreateNoWindow = true;
                getPipProcess.Start();
                getPipProcess.WaitForExit(120000); // 2 minute timeout

                if (getPipProcess.ExitCode != 0)
                {
                    string pipError = getPipProcess.StandardError.ReadToEnd();
                    Debug.LogWarning($"[Synthesis] Could not bootstrap pip: {pipError}. Skipping package installation.");
                    return;
                }

                Debug.Log("[Synthesis] Pip bootstrapped successfully");

                // Install required packages
                Debug.Log("[Synthesis] Installing Python packages...");
                var process = new System.Diagnostics.Process();
                process.StartInfo.FileName = pythonPath;
                process.StartInfo.Arguments = "-m pip install sqlite-rag chromadb sentence-transformers";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;
                process.Start();

                // Wait with timeout (5 minutes for package installation)
                if (!process.WaitForExit(300000))
                {
                    process.Kill();
                    Debug.LogWarning("[Synthesis] Python package installation timed out");
                    return;
                }

                string output = process.StandardOutput.ReadToEnd();
                string error = process.StandardError.ReadToEnd();

                if (process.ExitCode == 0)
                {
                    Debug.Log("[Synthesis] Python packages installed successfully");
                }
                else
                {
                    Debug.LogWarning($"[Synthesis] Python package installation warnings: {error}");
                }
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Synthesis] Python setup warning: {e.Message}");
            }
        }

        private static void CreateInitialPublicContent()
        {
            // Create some initial entries in public DB
            string packageRoot = Path.Combine(Application.dataPath, "Synthesis.Pro");
            string publicDbPath = Path.Combine(packageRoot, "Server", "synthesis_public.db");

            if (!File.Exists(publicDbPath))
            {
                return;
            }

            Debug.Log("[Synthesis] Creating initial public KB content");

            // Add welcome entry, documentation links, etc.
            // This will be expanded with actual initial content
        }

        [MenuItem("Tools/Synthesis/Setup/Reset Setup", false, 101)]
        public static void ResetSetup()
        {
            bool confirm = EditorUtility.DisplayDialog(
                "Reset Setup?",
                "This will mark Synthesis as not set up.\n\n" +
                "First-time setup will run again on next restart.\n\n" +
                "Continue?",
                "Yes, Reset",
                "Cancel"
            );

            if (confirm)
            {
                EditorPrefs.DeleteKey(SETUP_COMPLETE_KEY);
                Debug.Log("[Synthesis] Setup reset. Restart Unity to run setup again.");

                EditorUtility.DisplayDialog(
                    "Reset Complete",
                    "Setup has been reset.\n\n" +
                    "Restart Unity to run first-time setup again.",
                    "OK"
                );
            }
        }
    }
}
