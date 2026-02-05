using UnityEngine;
using UnityEditor;
using Synthesis.Bridge;
using System.Collections;

namespace Synthesis.Editor
{
    /// <summary>
    /// Play mode test for RAG Bridge - Awake() will actually be called
    /// </summary>
    public class PlayModeRAGTest
    {
        private static bool testRunning = false;

        [MenuItem("Synthesis/Test RAG Bridge (Play Mode)")]
        public static void RunPlayModeTest()
        {
            if (EditorApplication.isPlaying)
            {
                Debug.LogError("Already in play mode. Stop play mode first, then run this test.");
                return;
            }

            Debug.LogWarning("===== STARTING PLAY MODE RAG TEST =====");
            Debug.Log("This will enter play mode and create a RAGBridge component.");
            Debug.Log("Watch for '[RAG Bridge] ===== AWAKE CALLED =====' in the console.");

            // Subscribe to play mode state change
            EditorApplication.playModeStateChanged += OnPlayModeStateChanged;

            // Enter play mode
            testRunning = true;
            EditorApplication.isPlaying = true;
        }

        private static void OnPlayModeStateChanged(PlayModeStateChange state)
        {
            if (!testRunning)
                return;

            if (state == PlayModeStateChange.EnteredPlayMode)
            {
                Debug.LogWarning("===== ENTERED PLAY MODE - CREATING RAG BRIDGE =====");

                // Create RAGBridge in play mode (Awake will be called)
                var go = new GameObject("RAGBridge_PlayModeTest");
                var bridge = go.AddComponent<RAGBridge>();

                Debug.Log($"Component added. Waiting for Awake() to execute...");

                // Give it a frame to initialize
                EditorApplication.delayCall += () =>
                {
                    Debug.Log("===== CHECKING RAG BRIDGE AFTER AWAKE =====");

                    if (bridge.IsRAGAvailable())
                    {
                        Debug.Log("✅ [SUCCESS] RAG Bridge is available!");
                        Debug.Log("Awake() executed and Python was found.");
                    }
                    else
                    {
                        Debug.LogError("❌ [FAIL] RAG Bridge not available");
                        Debug.LogError("Check above for '[RAG Bridge] Python not found at:' message");
                    }

                    Debug.LogWarning("===== PLAY MODE TEST COMPLETE =====");
                    Debug.Log("You can now stop play mode or continue testing manually.");

                    testRunning = false;
                    EditorApplication.playModeStateChanged -= OnPlayModeStateChanged;
                };
            }
        }
    }
}
