using UnityEngine;
using UnityEngine.Networking;
using System.IO;
using System.Collections.Generic;
using System.Collections;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Synthesis.Bridge
{
    /// <summary>
    /// SynLink Extended - AI Creative Commands
    /// 
    /// Extends SynLink with creative commands using direct OpenAI API integration:
    /// - GenerateImage: Create 2D assets with DALL-E
    /// - GenerateSound: Create audio with ElevenLabs (planned)
    /// - Generate3DModel: Create 3D models with Trellis (planned)
    /// - GenerateShader: Create shaders with AI
    /// - GenerateScript: Create C# scripts with AI
    /// 
    /// Self-contained implementation - no external dependencies!
    /// Now I can CREATE, not just manipulate! 🎨🎵🗿
    /// </summary>
    [AddComponentMenu("Synthesis/SynLink Extended (AI Creative)")]
    public class SynLinkExtended : MonoBehaviour
    {
        #region Singleton
        
        private static SynLinkExtended instance;
        public static SynLinkExtended Instance => instance;
        
        #endregion
        
        #region Settings
        
        [Header("Extended Bridge Settings")]
        [SerializeField] private bool enableExtendedCommands = true;
        [SerializeField] private string generatedAssetsPath = "Assets/AI_Generated";
        
        [Header("OpenAI API Settings")]
        [SerializeField] private string openAIApiKey = ""; // Set this in Inspector or via PlayerPrefs
        [SerializeField] private string openAIApiUrl = "https://api.openai.com/v1";
        
        [Header("File Paths")]
        [SerializeField] private string logsFileName = "unity_bridge_logs.txt";
        
        [Header("References")]
        [SerializeField] private SynLink baseBridge; // Reference to base SynLink
        
        private string logsFilePath;
        
        #endregion
        
        #region State
        
        private Dictionary<string, System.Action<BridgeCommand>> extendedCommands;
        private Dictionary<string, object> pendingResults = new Dictionary<string, object>();
        
        #endregion
        
        #region Unity Lifecycle
        
        private void Awake()
        {
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            instance = this;
            DontDestroyOnLoad(gameObject);
            
            // Setup log file path
            logsFilePath = Path.Combine(Application.dataPath, "..", logsFileName);
            
            // Load API key from PlayerPrefs if not set in inspector
            if (string.IsNullOrEmpty(openAIApiKey))
            {
                openAIApiKey = PlayerPrefs.GetString("OpenAI_API_Key", "");
            }
            
            // Setup extended command handlers
            InitializeExtendedCommands();
            
            Log("🚀 Unity Bridge Extended - AI SUPERPOWERS ACTIVATED! (Self-Contained)");
        }
        
        #endregion
        
        #region Initialization
        
        private void InitializeExtendedCommands()
        {
            extendedCommands = new Dictionary<string, System.Action<BridgeCommand>>
            {
                { "GenerateImage", HandleGenerateImage },
                { "GenerateSound", HandleGenerateSound },
                { "Generate3DModel", HandleGenerate3DModel },
                { "GenerateShader", HandleGenerateShader },
                { "GetCapabilities", HandleGetCapabilities },
                { "GenerateScript", HandleGenerateScript }
            };
        }
        
        #endregion
        
        #region Public API
        
        /// <summary>
        /// Process an extended command
        /// </summary>
        public void ProcessExtendedCommand(BridgeCommand cmd)
        {
            if (!enableExtendedCommands)
            {
                SendResult(cmd.id, false, "Extended commands are disabled");
                return;
            }
            
            if (extendedCommands.ContainsKey(cmd.type))
            {
                Log($"🎨 Extended Command: {cmd.type} (ID: {cmd.id})");
                extendedCommands[cmd.type](cmd);
            }
            else
            {
                SendResult(cmd.id, false, $"Unknown extended command: {cmd.type}");
            }
        }
        
        #endregion
        
        #region Extended Command Handlers
        
        private void HandleGenerateImage(BridgeCommand cmd)
        {
            string prompt = cmd.parameters?.GetValueOrDefault("prompt")?.ToString();
            string sizeStr = cmd.parameters?.GetValueOrDefault("size")?.ToString() ?? "1024x1024";
            string modelStr = cmd.parameters?.GetValueOrDefault("model")?.ToString() ?? "dall-e-3";
            int count = System.Convert.ToInt32(cmd.parameters?.GetValueOrDefault("count") ?? 1);
            
            if (string.IsNullOrEmpty(prompt))
            {
                SendResult(cmd.id, false, "Missing 'prompt' parameter");
                return;
            }
            
            if (string.IsNullOrEmpty(openAIApiKey))
            {
                SendResult(cmd.id, false, "OpenAI API key not set. Configure in Inspector or PlayerPrefs.");
                return;
            }
            
            SendResult(cmd.id, true, "Image generation started...", new Dictionary<string, object>
            {
                { "status", "generating" },
                { "prompt", prompt },
                { "model", modelStr },
                { "size", sizeStr }
            });
            
            // Start image generation coroutine
            StartCoroutine(GenerateImageWithDALLE(cmd.id, prompt, modelStr, sizeStr, count));
        }
        
        private IEnumerator GenerateImageWithDALLE(string commandId, string prompt, string model, string size, int count)
        {
            // Build request JSON
            var requestData = new
            {
                model = model,
                prompt = prompt,
                n = count,
                size = size,
                response_format = "url"
            };
            
            string jsonData = JsonConvert.SerializeObject(requestData);
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
            
            // Create request
            UnityWebRequest request = new UnityWebRequest($"{openAIApiUrl}/images/generations", "POST");
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("Authorization", $"Bearer {openAIApiKey}");
            
            // Send request
            yield return request.SendWebRequest();
            
            if (request.result != UnityWebRequest.Result.Success)
            {
                SendResult(commandId, false, $"Image generation failed: {request.error}");
                yield break;
            }
            
            // Parse response
            JObject response;
            JArray dataArray;
            List<string> imageUrls;
            
            try
            {
                response = JObject.Parse(request.downloadHandler.text);

                // Explicitly check if "data" field exists before casting
                if (response["data"] == null)
                {
                    SendResult(commandId, false, "API response missing 'data' field");
                    yield break;
                }

                dataArray = (JArray)response["data"];

                if (dataArray == null || dataArray.Count == 0)
                {
                    SendResult(commandId, false, "No images returned from API");
                    yield break;
                }
                
                // Download and save images
                imageUrls = new List<string>();
                foreach (var item in dataArray)
                {
                    string url = item["url"]?.ToString();
                    if (!string.IsNullOrEmpty(url))
                    {
                        imageUrls.Add(url);
                    }
                }
            }
            catch (System.Exception ex)
            {
                SendResult(commandId, false, $"Failed to parse response: {ex.Message}");
                yield break;
            }
            
            // Download and save images (outside try-catch to allow yield)
            yield return StartCoroutine(DownloadAndSaveImages(commandId, imageUrls));
        }
        
        private IEnumerator DownloadAndSaveImages(string commandId, List<string> imageUrls)
        {
            List<string> savedPaths = new List<string>();
            
            // Ensure directory exists
            string savePath = Path.Combine(Application.dataPath, generatedAssetsPath.Replace("Assets/", ""));
            if (!Directory.Exists(savePath))
            {
                Directory.CreateDirectory(savePath);
            }
            
            foreach (string url in imageUrls)
            {
                UnityWebRequest request = UnityWebRequestTexture.GetTexture(url);
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    Texture2D texture = DownloadHandlerTexture.GetContent(request);
                    
                    // Generate filename
                    string filename = $"AI_Image_{System.DateTime.Now:yyyyMMdd_HHmmss}_{savedPaths.Count}.png";
                    string fullPath = Path.Combine(savePath, filename);
                    
                    // Save texture
                    byte[] bytes = texture.EncodeToPNG();
                    File.WriteAllBytes(fullPath, bytes);
                    
                    string assetPath = fullPath.Replace(Application.dataPath, "Assets");
                    savedPaths.Add(assetPath);
                    
                    Log($"✅ Saved generated image: {assetPath}");
                }
                else
                {
                    Log($"⚠️ Failed to download image: {request.error}");
                }
            }
            
#if UNITY_EDITOR
            // Refresh asset database
            UnityEditor.AssetDatabase.Refresh();
#endif
            
            // Send completion result
            SendResult(commandId, true, $"Generated and saved {savedPaths.Count} image(s)", new Dictionary<string, object>
            {
                { "status", "complete" },
                { "imageCount", savedPaths.Count },
                { "paths", savedPaths }
            });
        }
        
        private void HandleGenerateSound(BridgeCommand cmd)
        {
            // TODO: Integrate ElevenLabs sound generation
            SendResult(cmd.id, true, "Sound generation - Coming soon! 🎵", new Dictionary<string, object>
            {
                { "status", "not_implemented" },
                { "message", "ElevenLabs integration planned" }
            });
        }
        
        private void HandleGenerate3DModel(BridgeCommand cmd)
        {
            // TODO: Integrate Trellis 3D model generation
            SendResult(cmd.id, true, "3D model generation - Coming soon! 🗿", new Dictionary<string, object>
            {
                { "status", "not_implemented" },
                { "message", "Trellis integration planned" }
            });
        }
        
        private void HandleGenerateShader(BridgeCommand cmd)
        {
            string prompt = cmd.parameters?.GetValueOrDefault("prompt")?.ToString();
            
            if (string.IsNullOrEmpty(prompt))
            {
                SendResult(cmd.id, false, "Missing 'prompt' parameter");
                return;
            }
            
            if (string.IsNullOrEmpty(openAIApiKey))
            {
                SendResult(cmd.id, false, "OpenAI API key not set. Configure in Inspector or PlayerPrefs.");
                return;
            }
            
            SendResult(cmd.id, true, "Shader generation started...", new Dictionary<string, object>
            {
                { "status", "generating" },
                { "prompt", prompt }
            });
            
            string systemPrompt = "You are a Unity shader expert. Generate shader code based on the user's description. Return ONLY the shader code, no explanations.";
            string userPrompt = $"Create a Unity shader for: {prompt}";
            
            StartCoroutine(GenerateCodeWithGPT(cmd.id, systemPrompt, userPrompt, "shader", prompt));
        }
        
        private void HandleGenerateScript(BridgeCommand cmd)
        {
            string prompt = cmd.parameters?.GetValueOrDefault("prompt")?.ToString();
            
            if (string.IsNullOrEmpty(prompt))
            {
                SendResult(cmd.id, false, "Missing 'prompt' parameter");
                return;
            }
            
            if (string.IsNullOrEmpty(openAIApiKey))
            {
                SendResult(cmd.id, false, "OpenAI API key not set. Configure in Inspector or PlayerPrefs.");
                return;
            }
            
            SendResult(cmd.id, true, "Script generation started...", new Dictionary<string, object>
            {
                { "status", "generating" },
                { "prompt", prompt }
            });
            
            string systemPrompt = "You are a professional Unity C# programmer. Generate clean, well-commented Unity scripts. Return ONLY the code, no explanations.";
            string userPrompt = $"Create a Unity C# script for: {prompt}";
            
            StartCoroutine(GenerateCodeWithGPT(cmd.id, systemPrompt, userPrompt, "script", prompt));
        }
        
        private void HandleGetCapabilities(BridgeCommand cmd)
        {
            var capabilities = new Dictionary<string, object>
            {
                { "version", "1.0" },
                { "name", "Unity Bridge Extended - AI Superpowers" },
                { "commands", new List<string>
                    {
                        "GenerateImage",
                        "GenerateSound", 
                        "Generate3DModel",
                        "GenerateShader",
                        "GenerateScript",
                        "GetCapabilities"
                    }
                },
                { "imageGeneration", new Dictionary<string, object>
                    {
                        { "enabled", !string.IsNullOrEmpty(openAIApiKey) },
                        { "provider", "DALL-E (OpenAI - Direct API)" },
                        { "models", new[] { "dall-e-3", "dall-e-2" } }
                    }
                },
                { "soundGeneration", new Dictionary<string, object>
                    {
                        { "enabled", false },
                        { "provider", "ElevenLabs" },
                        { "status", "planned" }
                    }
                },
                { "modelGeneration", new Dictionary<string, object>
                    {
                        { "enabled", false },
                        { "provider", "Trellis" },
                        { "status", "planned" }
                    }
                },
                { "shaderGeneration", new Dictionary<string, object>
                    {
                        { "enabled", !string.IsNullOrEmpty(openAIApiKey) },
                        { "provider", "GPT (OpenAI - Direct API)" }
                    }
                },
                { "scriptGeneration", new Dictionary<string, object>
                    {
                        { "enabled", !string.IsNullOrEmpty(openAIApiKey) },
                        { "provider", "GPT (OpenAI - Direct API)" }
                    }
                }
            };
            
            SendResult(cmd.id, true, "AI Capabilities", capabilities);
        }
        
        #endregion
        
        #region OpenAI API Integration
        
        private IEnumerator GenerateCodeWithGPT(string commandId, string systemPrompt, string userPrompt, string fileType, string originalPrompt)
        {
            // Build request JSON
            var requestData = new
            {
                model = "gpt-4",
                messages = new[]
                {
                    new { role = "system", content = systemPrompt },
                    new { role = "user", content = userPrompt }
                },
                temperature = 0.7
            };
            
            string jsonData = JsonConvert.SerializeObject(requestData);
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
            
            // Create request
            UnityWebRequest request = new UnityWebRequest($"{openAIApiUrl}/chat/completions", "POST");
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            request.SetRequestHeader("Authorization", $"Bearer {openAIApiKey}");
            
            // Send request
            yield return request.SendWebRequest();
            
            if (request.result != UnityWebRequest.Result.Success)
            {
                SendResult(commandId, false, $"{fileType} generation failed: {request.error}");
                yield break;
            }
            
            // Parse response
            try
            {
                JObject response = JObject.Parse(request.downloadHandler.text);
                string generatedCode = response["choices"]?[0]?["message"]?["content"]?.ToString();
                
                if (string.IsNullOrEmpty(generatedCode))
                {
                    SendResult(commandId, false, "No code returned from API");
                    yield break;
                }
                
                // Clean up markdown code blocks if present
                generatedCode = CleanCodeBlocks(generatedCode);
                
                // Save file
                SaveGeneratedCode(commandId, generatedCode, fileType, originalPrompt);
            }
            catch (System.Exception ex)
            {
                SendResult(commandId, false, $"Failed to parse response: {ex.Message}");
            }
        }
        
        private string CleanCodeBlocks(string code)
        {
            // Remove markdown code fences if present
            code = code.Trim();
            
            if (code.StartsWith("```"))
            {
                int firstNewline = code.IndexOf('\n');
                if (firstNewline > 0)
                {
                    code = code.Substring(firstNewline + 1);
                }
            }
            
            if (code.EndsWith("```"))
            {
                int lastFence = code.LastIndexOf("```");
                if (lastFence > 0)
                {
                    code = code.Substring(0, lastFence);
                }
            }
            
            return code.Trim();
        }
        
        private void SaveGeneratedCode(string commandId, string code, string fileType, string originalPrompt)
        {
            // Ensure directory exists
            string savePath = Path.Combine(Application.dataPath, generatedAssetsPath.Replace("Assets/", ""));
            if (!Directory.Exists(savePath))
            {
                Directory.CreateDirectory(savePath);
            }
            
            // Determine file extension
            string extension = fileType == "shader" ? ".shader" : ".cs";
            string prefix = fileType == "shader" ? "AI_Shader" : "AI_Script";
            
            // Generate filename
            string filename = $"{prefix}_{System.DateTime.Now:yyyyMMdd_HHmmss}{extension}";
            string fullPath = Path.Combine(savePath, filename);
            
            // Save file
            File.WriteAllText(fullPath, code);
            
            string assetPath = fullPath.Replace(Application.dataPath, "Assets");
            
            Log($"✅ Saved generated {fileType}: {assetPath}");
            
#if UNITY_EDITOR
            UnityEditor.AssetDatabase.Refresh();
#endif
            
            SendResult(commandId, true, $"{fileType} generated and saved", new Dictionary<string, object>
            {
                { "status", "complete" },
                { "path", assetPath },
                { "prompt", originalPrompt }
            });
        }
        
        #endregion
        
        #region Helpers
        
        private void SendResult(string commandId, bool success, string message, Dictionary<string, object> data = null)
        {
            var result = new BridgeResult
            {
                commandId = commandId,
                success = success,
                message = message,
                timestamp = System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"),
                data = data
            };
            
            // Write to results file (same as base bridge)
            string resultsFilePath = Path.Combine(Application.dataPath, "..", "unity_bridge_results.json");
            string json = JsonConvert.SerializeObject(result, Formatting.Indented);
            File.WriteAllText(resultsFilePath, json);
            
            Log(message);
        }
        
        private void Log(string message)
        {
            string logEntry = $"[{System.DateTime.Now:HH:mm:ss}] [Extended] {message}\n";
            Debug.Log($"[SynLinkExtended] {message}");
            
            try
            {
                File.AppendAllText(logsFilePath, logEntry);
            }
            catch (System.Exception ex)
            {
                Debug.LogWarning($"[SynLinkExtended] Failed to write to log file: {ex.Message}");
            }
        }
        
        #endregion
    }
}
