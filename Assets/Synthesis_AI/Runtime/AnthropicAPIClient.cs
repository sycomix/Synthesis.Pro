using UnityEngine;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine.Networking;
using Newtonsoft.Json;

namespace Synthesis.Runtime
{
    /// <summary>
    /// Direct Anthropic API client for Unity
    /// Communicate with Claude directly from Unity!
    /// </summary>
    public class AnthropicAPIClient : MonoBehaviour
    {
        [Header("Anthropic API Configuration")]
        [SerializeField] private string apiKey = "";
        [SerializeField] private string model = "claude-3-5-sonnet-20241022";
        [SerializeField] private int maxTokens = 4096;
        
        [Header("Settings")]
        [SerializeField] private float temperature = 1.0f;
        [SerializeField] private bool streamResponse = true;
        
        private const string ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages";
        private const string ANTHROPIC_VERSION = "2023-06-01";
        
        private List<Message> conversationHistory = new List<Message>();
        
        // Events
        public event Action<string> OnMessageReceived;
        public event Action<string> OnStreamChunk;
        public event Action<string> OnError;
        public event Action OnRequestStarted;
        public event Action OnRequestCompleted;
        
        [System.Serializable]
        private class Message
        {
            public string role;
            public string content;
            
            public Message(string role, string content)
            {
                this.role = role;
                this.content = content;
            }
        }
        
        [System.Serializable]
        private class AnthropicRequest
        {
            public string model;
            public List<Message> messages;
            public int max_tokens;
            public float temperature;
            public bool stream;
        }
        
        [System.Serializable]
        private class AnthropicResponse
        {
            public string id;
            public string type;
            public string role;
            public List<ContentBlock> content;
            public string model;
            public string stop_reason;
            public Usage usage;
        }
        
        [System.Serializable]
        private class ContentBlock
        {
            public string type;
            public string text;
        }
        
        [System.Serializable]
        private class Usage
        {
            public int input_tokens;
            public int output_tokens;
        }
        
        /// <summary>
        /// Set the API key programmatically
        /// </summary>
        public void SetAPIKey(string key)
        {
            apiKey = key;
            PlayerPrefs.SetString("Anthropic_API_Key", key);
            PlayerPrefs.Save();
        }
        
        /// <summary>
        /// Get the current API key
        /// </summary>
        public string GetAPIKey()
        {
            if (string.IsNullOrEmpty(apiKey))
            {
                apiKey = PlayerPrefs.GetString("Anthropic_API_Key", "");
            }
            return apiKey;
        }
        
        /// <summary>
        /// Set the model to use
        /// </summary>
        public void SetModel(string modelName)
        {
            model = modelName;
        }
        
        /// <summary>
        /// Send a message to Claude
        /// </summary>
        public void SendMessage(string userMessage)
        {
            if (string.IsNullOrEmpty(apiKey) || string.IsNullOrEmpty(GetAPIKey()))
            {
                OnError?.Invoke("API key not set! Please configure your Anthropic API key.");
                Debug.LogError("[AnthropicAPI] API key not set!");
                return;
            }
            
            // Add user message to history
            conversationHistory.Add(new Message("user", userMessage));
            
            // Start the request
            StartCoroutine(SendRequestCoroutine());
        }
        
        /// <summary>
        /// Clear conversation history
        /// </summary>
        public void ClearHistory()
        {
            conversationHistory.Clear();
            Debug.Log("[AnthropicAPI] Conversation history cleared");
        }
        
        /// <summary>
        /// Get conversation history
        /// </summary>
        public List<(string role, string content)> GetHistory()
        {
            var history = new List<(string, string)>();
            foreach (var msg in conversationHistory)
            {
                history.Add((msg.role, msg.content));
            }
            return history;
        }
        
        private IEnumerator SendRequestCoroutine()
        {
            OnRequestStarted?.Invoke();
            
            // Create request
            var request = new AnthropicRequest
            {
                model = model,
                messages = conversationHistory,
                max_tokens = maxTokens,
                temperature = temperature,
                stream = streamResponse
            };
            
            string jsonBody = JsonConvert.SerializeObject(request);
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonBody);
            
            // Create UnityWebRequest
            using (UnityWebRequest webRequest = new UnityWebRequest(ANTHROPIC_API_URL, "POST"))
            {
                webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
                webRequest.downloadHandler = new DownloadHandlerBuffer();
                
                // Set headers
                webRequest.SetRequestHeader("Content-Type", "application/json");
                webRequest.SetRequestHeader("anthropic-version", ANTHROPIC_VERSION);
                webRequest.SetRequestHeader("x-api-key", GetAPIKey());
                
                // Send request
                yield return webRequest.SendWebRequest();
                
                // Handle response
                if (webRequest.result == UnityWebRequest.Result.Success)
                {
                    string responseText = webRequest.downloadHandler.text;
                    
                    try
                    {
                        var response = JsonConvert.DeserializeObject<AnthropicResponse>(responseText);
                        
                        if (response.content != null && response.content.Count > 0)
                        {
                            string assistantMessage = response.content[0].text;
                            
                            // Add to history
                            conversationHistory.Add(new Message("assistant", assistantMessage));
                            
                            // Notify listeners
                            OnMessageReceived?.Invoke(assistantMessage);
                            
                            Debug.Log($"[AnthropicAPI] Response received ({response.usage.output_tokens} tokens)");
                        }
                    }
                    catch (Exception e)
                    {
                        OnError?.Invoke($"Failed to parse response: {e.Message}");
                        Debug.LogError($"[AnthropicAPI] Parse error: {e.Message}\nResponse: {responseText}");
                    }
                }
                else
                {
                    string errorMessage = $"API Error: {webRequest.error}\n{webRequest.downloadHandler.text}";
                    OnError?.Invoke(errorMessage);
                    Debug.LogError($"[AnthropicAPI] {errorMessage}");
                }
                
                OnRequestCompleted?.Invoke();
            }
        }
        
        private void Awake()
        {
            // Load saved API key
            if (string.IsNullOrEmpty(apiKey))
            {
                apiKey = PlayerPrefs.GetString("Anthropic_API_Key", "");
            }
        }
        
        private void OnValidate()
        {
            // Clamp temperature
            temperature = Mathf.Clamp(temperature, 0f, 1f);
            
            // Clamp max tokens
            maxTokens = Mathf.Max(1, maxTokens);
        }
    }
}
