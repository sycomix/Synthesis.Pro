using UnityEngine;
using UnityEditor;
using Synthesis.Bridge;

namespace Synthesis.Editor
{
    /// <summary>
    /// Test RAG Bridge integration
    /// Menu: Synthesis > Test RAG Bridge
    /// </summary>
    public class TestRAGBridge
    {
        [MenuItem("Synthesis/Test RAG Bridge")]
        public static void RunTest()
        {
            Debug.Log("=== Testing RAG Bridge ===");

            // Clean up any existing RAGBridge instances (might have old code)
            var existingBridges = GameObject.FindObjectsByType<RAGBridge>(FindObjectsSortMode.None);
            foreach (var existing in existingBridges)
            {
                Debug.Log($"Destroying old RAGBridge: {existing.gameObject.name}");
                GameObject.DestroyImmediate(existing.gameObject);
            }

            // Reset singleton instance (prevents Awake from destroying new component)
            RAGBridge.ResetInstance();

            // Create fresh RAGBridge with current code
            Debug.Log("Creating fresh RAGBridge GameObject...");
            var go = new GameObject("RAGBridge_Test");
            var bridge = go.AddComponent<RAGBridge>();

            // Check if RAG is available
            if (!bridge.IsRAGAvailable())
            {
                Debug.LogError("[FAIL] RAG Bridge not available");
                Debug.LogError("Check console above for '[RAG Bridge] Python not found at:' to see the path Unity is checking");
                return;
            }

            Debug.Log("[OK] RAG Bridge available");

            // Test 1: Start Session
            Debug.Log("\n[TEST 1] Starting RAG session...");
            string preview = bridge.StartSession("test-session-001");

            if (preview != null && !string.IsNullOrEmpty(preview))
            {
                Debug.Log($"[OK] Session started with preview:\n{preview}");
            }
            else
            {
                Debug.Log("[OK] Session started (no preview - fresh start)");
            }

            // Test 2: Process User Message
            Debug.Log("\n[TEST 2] Processing user message...");
            string testMessage = "How do I create VFX assets in Unity?";
            string context = bridge.ProcessUserMessage(testMessage);

            if (context != null && !string.IsNullOrEmpty(context))
            {
                Debug.Log($"[OK] Context found:\n{context}");
            }
            else
            {
                Debug.Log("[OK] No context found for message (expected if DB is empty)");
            }

            // Test 3: Process AI Response (uncertainty detection)
            Debug.Log("\n[TEST 3] Processing AI response with uncertainty...");
            string aiResponse = "I'm not sure what the VFX creation workflow is in your project.";
            string aiUserMessage = "How do I create VFX?";
            string result = bridge.ProcessAIResponse(aiResponse, aiUserMessage);

            if (result != null && !string.IsNullOrEmpty(result))
            {
                Debug.Log($"[OK] AI response processed:\n{result}");
            }
            else
            {
                Debug.Log("[OK] AI response processed (no uncertainty context)");
            }

            // Test 4: Process confident AI response (should not trigger)
            Debug.Log("\n[TEST 4] Processing confident AI response...");
            string confidentResponse = "To create VFX in Unity, use the VFX Graph window.";
            result = bridge.ProcessAIResponse(confidentResponse, aiUserMessage);

            Debug.Log($"[OK] Confident response processed");

            // Test 5: End Session
            Debug.Log("\n[TEST 5] Ending session...");
            bridge.EndSession();
            Debug.Log("[OK] Session ended");

            Debug.Log("\n=== RAG Bridge Test Complete ===");
            Debug.Log("Check console output above for any errors.");
            Debug.Log("If Python errors occurred, check the Unity console for details.");
        }

        [MenuItem("Synthesis/Test RAG Bridge (Verbose)")]
        public static void RunVerboseTest()
        {
            Debug.Log("=== Verbose RAG Bridge Test ===");

            var bridge = GameObject.FindFirstObjectByType<RAGBridge>();

            if (bridge == null)
            {
                var go = new GameObject("RAGBridge_Test");
                bridge = go.AddComponent<RAGBridge>();
            }

            Debug.Log($"RAG Available: {bridge.IsRAGAvailable()}");

            // Test with VFX-specific query (should match private DB entry)
            if (bridge.IsRAGAvailable())
            {
                Debug.Log("\nStarting session...");
                bridge.StartSession("verbose-test");

                Debug.Log("\nQuerying for VFX information...");
                string vfxContext = bridge.ProcessUserMessage("VFX asset creation ManageVFX.cs reflection");

                if (vfxContext != null && !string.IsNullOrEmpty(vfxContext))
                {
                    Debug.Log($"VFX Context Found:\n{vfxContext}");
                }
                else
                {
                    Debug.Log("No VFX context found - check if private DB has entries");
                }

                bridge.EndSession();
            }

            Debug.Log("\n=== Verbose Test Complete ===");
        }
    }
}
