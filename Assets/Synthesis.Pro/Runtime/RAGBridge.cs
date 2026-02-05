using UnityEngine;
using System.Diagnostics;
using System.IO;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Synthesis.Bridge
{
    /// <summary>
    /// RAG Bridge - Connects Unity to RAG Onboarding and Collective Learning systems
    ///
    /// Enables AI context awareness and collective intelligence through:
    /// - RAG Onboarding: Natural context presentation for AI sessions
    /// - Collective Learning: AI instances sharing abstracted patterns
    ///
    /// Philosophy: Enable, don't force. Make RAG usage natural and beneficial.
    /// </summary>
    public class RAGBridge : MonoBehaviour
    {
        #region Singleton

        private static RAGBridge instance;
        public static RAGBridge Instance => instance;

        #endregion

        #region Settings

        [Header("RAG Bridge Settings")]
        [SerializeField] private bool enableRAG = true;
        [SerializeField] private bool enableCollectiveLearning = false; // Requires user consent

        [Header("Python Paths")]
        private string pythonExe;
        private string serverPath;

        [Header("Session")]
        [SerializeField] private string currentSessionId;
        private bool sessionInitialized = false;

        #endregion

        #region Unity Lifecycle

        private void Awake()
        {
            // Singleton
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }

            instance = this;
            DontDestroyOnLoad(gameObject);

            // Setup paths
            serverPath = Path.Combine(Application.dataPath, "..", "Synthesis.Pro", "Server");
            pythonExe = Path.Combine(Application.dataPath, "Synthesis.Pro", "KnowledgeBase", "python", "python.exe");

            // Verify Python exists
            if (!File.Exists(pythonExe))
            {
                UnityEngine.Debug.LogWarning($"[RAG Bridge] Python not found at: {pythonExe}");
                UnityEngine.Debug.LogWarning("[RAG Bridge] RAG features disabled");
                enableRAG = false;
                return;
            }

            UnityEngine.Debug.Log($"[RAG Bridge] Initialized - Python: {pythonExe}");
        }

        #endregion

        #region Session Management

        /// <summary>
        /// Start new RAG session with optional context preview
        /// </summary>
        public string StartSession(string sessionId = null)
        {
            if (!enableRAG)
                return null;

            currentSessionId = sessionId ?? System.Guid.NewGuid().ToString();

            UnityEngine.Debug.Log($"[RAG Bridge] Starting session: {currentSessionId}");

            // Call Python RAG onboarding to get session preview
            string preview = CallPythonRAG("start_session", new JObject
            {
                ["session_id"] = currentSessionId
            });

            sessionInitialized = true;

            return preview;
        }

        /// <summary>
        /// Process user message and get relevant context if available
        /// </summary>
        public string ProcessUserMessage(string userMessage)
        {
            if (!enableRAG || !sessionInitialized)
                return null;

            string context = CallPythonRAG("process_user_message", new JObject
            {
                ["session_id"] = currentSessionId,
                ["message"] = userMessage
            });

            return context;
        }

        /// <summary>
        /// Process AI response for uncertainty detection and potential contribution
        /// </summary>
        public string ProcessAIResponse(string aiResponse, string userMessage)
        {
            if (!enableRAG || !sessionInitialized)
                return null;

            string result = CallPythonRAG("process_ai_response", new JObject
            {
                ["session_id"] = currentSessionId,
                ["ai_response"] = aiResponse,
                ["user_message"] = userMessage,
                ["enable_collective_learning"] = enableCollectiveLearning
            });

            return result;
        }

        /// <summary>
        /// End current session
        /// </summary>
        public void EndSession()
        {
            if (!sessionInitialized)
                return;

            UnityEngine.Debug.Log($"[RAG Bridge] Ending session: {currentSessionId}");
            sessionInitialized = false;
            currentSessionId = null;
        }

        #endregion

        #region Python Communication

        /// <summary>
        /// Call Python RAG system with command and data
        /// </summary>
        private string CallPythonRAG(string command, JObject data)
        {
            try
            {
                // Create temp file for input data
                string inputFile = Path.Combine(serverPath, $"rag_input_{System.Guid.NewGuid()}.json");
                string outputFile = Path.Combine(serverPath, $"rag_output_{System.Guid.NewGuid()}.json");

                // Add command and output path to data
                data["command"] = command;
                data["output_file"] = outputFile;

                // Write input data
                File.WriteAllText(inputFile, data.ToString());

                // Call Python script
                var process = new Process();
                process.StartInfo.FileName = pythonExe;
                process.StartInfo.Arguments = $"\"{Path.Combine(serverPath, "rag_bridge.py")}\" \"{inputFile}\"";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;
                process.StartInfo.WorkingDirectory = serverPath;

                process.Start();

                string output = process.StandardOutput.ReadToEnd();
                string error = process.StandardError.ReadToEnd();

                process.WaitForExit();

                // Check for errors
                if (process.ExitCode != 0)
                {
                    UnityEngine.Debug.LogError($"[RAG Bridge] Python error: {error}");
                    return null;
                }

                // Read result from output file
                if (File.Exists(outputFile))
                {
                    string result = File.ReadAllText(outputFile);

                    // Cleanup temp files
                    File.Delete(inputFile);
                    File.Delete(outputFile);

                    return result;
                }

                // Cleanup input file
                File.Delete(inputFile);

                return null;
            }
            catch (System.Exception e)
            {
                UnityEngine.Debug.LogError($"[RAG Bridge] Exception: {e.Message}");
                return null;
            }
        }

        #endregion

        #region Utility

        /// <summary>
        /// Check if RAG is available and functional
        /// </summary>
        public bool IsRAGAvailable()
        {
            return enableRAG && File.Exists(pythonExe);
        }

        /// <summary>
        /// Enable or disable collective learning (requires user consent)
        /// </summary>
        public void SetCollectiveLearning(bool enabled)
        {
            enableCollectiveLearning = enabled;
            UnityEngine.Debug.Log($"[RAG Bridge] Collective learning: {(enabled ? "enabled" : "disabled")}");
        }

        #endregion
    }
}
