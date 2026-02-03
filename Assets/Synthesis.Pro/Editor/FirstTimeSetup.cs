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
        private const string PYTHON_DOWNLOAD_URL = "https://fallen-entertainment.github.io/Synthesis.Pro/downloads/python-embedded.zip";
        private const string MODELS_DOWNLOAD_URL = "https://fallen-entertainment.github.io/Synthesis.Pro/downloads/models.zip";

        static FirstTimeSetup()
        {
            // Check if setup already completed
            if (EditorPrefs.GetBool(SETUP_COMPLETE_KEY, false))
            {
                return;
            }

            // Delay to let Unity finish initializing
            EditorApplication.delayCall += RunFirstTimeSetup;
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
            SetupAsync();
        }

        [MenuItem("Synthesis/Setup/First Time Setup", false, 100)]
        public static void ManualSetup()
        {
            SetupAsync();
        }

        private static async void SetupAsync()
        {
            EditorUtility.DisplayProgressBar("Synthesis Setup", "Initializing...", 0.0f);

            try
            {
                // Step 1: Initialize databases
                EditorUtility.DisplayProgressBar("Synthesis Setup", "Creating databases...", 0.2f);
                if (!InitializeDatabases())
                {
                    throw new System.Exception("Failed to initialize databases");
                }

                // Step 2: Download Python runtime
                EditorUtility.DisplayProgressBar("Synthesis Setup", "Downloading Python runtime...", 0.4f);
                await DownloadPythonRuntime();

                // Step 3: Download models
                EditorUtility.DisplayProgressBar("Synthesis Setup", "Downloading AI models...", 0.6f);
                await DownloadModels();

                // Step 4: Initialize Python environment
                EditorUtility.DisplayProgressBar("Synthesis Setup", "Setting up Python environment...", 0.8f);
                InitializePythonEnvironment();

                // Step 5: Create initial public DB content
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
                // Get project root directory (parent of Assets folder)
                string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
                string serverDir = Path.Combine(projectRoot, "Synthesis.Pro", "Server");
                string privateDbPath = Path.Combine(serverDir, "synthesis_private.db");
                string publicDbPath = Path.Combine(serverDir, "synthesis_public.db");

                // Ensure directory exists
                Directory.CreateDirectory(serverDir);

                // Run Python database initialization script
                string initScript = Path.Combine(serverDir, "init_databases.py");

                if (!File.Exists(initScript))
                {
                    Debug.LogWarning("[Synthesis] init_databases.py not found, creating minimal DBs");
                    CreateMinimalDatabases(privateDbPath, publicDbPath);
                    return true;
                }

                // Run init script
                var process = new System.Diagnostics.Process();
                process.StartInfo.FileName = "python";
                process.StartInfo.Arguments = $"\"{initScript}\"";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;
                process.Start();
                process.WaitForExit();

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
            // Create empty SQLite databases with basic tables
            // This is a fallback if Python isn't available yet

            Debug.Log("[Synthesis] Creating minimal database structures");

            // For now, just create empty files
            // The Python scripts will create proper schema on first use
            File.WriteAllText(privateDbPath, "");
            File.WriteAllText(publicDbPath, "");
        }

        private static async Task DownloadPythonRuntime()
        {
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string targetDir = Path.Combine(projectRoot, "Synthesis.Pro", "Server", "python");

            if (Directory.Exists(targetDir) && Directory.GetFiles(targetDir).Length > 0)
            {
                Debug.Log("[Synthesis] Python runtime already exists");
                return;
            }

            try
            {
                using (var client = new HttpClient())
                {
                    client.Timeout = System.TimeSpan.FromMinutes(5);

                    var response = await client.GetAsync(PYTHON_DOWNLOAD_URL);
                    if (!response.IsSuccessStatusCode)
                    {
                        throw new System.Exception($"Download failed: {response.StatusCode}");
                    }

                    var zipPath = "python-embedded.zip";
                    using (var fs = new FileStream(zipPath, FileMode.Create))
                    {
                        await response.Content.CopyToAsync(fs);
                    }

                    // Extract zip
                    Directory.CreateDirectory(targetDir);
                    System.IO.Compression.ZipFile.ExtractToDirectory(zipPath, targetDir);
                    File.Delete(zipPath);

                    Debug.Log("[Synthesis] Python runtime downloaded");
                }
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Synthesis] Python download failed: {e.Message}. User will need to install manually.");
            }
        }

        private static async Task DownloadModels()
        {
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string targetDir = Path.Combine(projectRoot, "Synthesis.Pro", "Server", "models");

            if (Directory.Exists(targetDir) && Directory.GetFiles(targetDir).Length > 0)
            {
                Debug.Log("[Synthesis] Models already exist");
                return;
            }

            try
            {
                using (var client = new HttpClient())
                {
                    client.Timeout = System.TimeSpan.FromMinutes(10);

                    var response = await client.GetAsync(MODELS_DOWNLOAD_URL);
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
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Synthesis] Models download failed: {e.Message}. RAG features may be limited.");
            }
        }

        private static void InitializePythonEnvironment()
        {
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string pythonPath = Path.Combine(projectRoot, "Synthesis.Pro", "Server", "python", "python.exe");

            if (!File.Exists(pythonPath))
            {
                Debug.LogWarning("[Synthesis] Python runtime not found");
                return;
            }

            try
            {
                // Install required packages
                var process = new System.Diagnostics.Process();
                process.StartInfo.FileName = pythonPath;
                process.StartInfo.Arguments = "-m pip install sqlite-rag chromadb sentence-transformers";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.CreateNoWindow = true;
                process.Start();
                process.WaitForExit();

                Debug.Log("[Synthesis] Python environment configured");
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Synthesis] Python setup warning: {e.Message}");
            }
        }

        private static void CreateInitialPublicContent()
        {
            // Create some initial entries in public DB
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string publicDbPath = Path.Combine(projectRoot, "Synthesis.Pro", "Server", "synthesis_public.db");

            if (!File.Exists(publicDbPath))
            {
                return;
            }

            Debug.Log("[Synthesis] Creating initial public KB content");

            // Add welcome entry, documentation links, etc.
            // This will be expanded with actual initial content
        }

        [MenuItem("Synthesis/Setup/Reset Setup", false, 101)]
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
