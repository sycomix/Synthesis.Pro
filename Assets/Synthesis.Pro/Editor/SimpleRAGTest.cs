using UnityEngine;
using UnityEditor;
using Synthesis.Bridge;

namespace Synthesis.Editor
{
    public class SimpleRAGTest
    {
        [MenuItem("Synthesis/Simple RAG Test")]
        public static void RunSimpleTest()
        {
            Debug.LogWarning("===== SIMPLE TEST START =====");

            // Check if RAGBridge class exists and can be referenced
            Debug.Log($"RAGBridge type: {typeof(RAGBridge).FullName}");

            // Create GameObject
            var go = new GameObject("SimpleTest");
            Debug.Log($"GameObject created: {go.name}");

            // Add component
            Debug.Log("About to add RAGBridge component...");
            var bridge = go.AddComponent<RAGBridge>();
            Debug.Log($"Component added, instance null? {bridge == null}");

            if (bridge != null)
            {
                Debug.Log($"Component type: {bridge.GetType().Name}");
                Debug.Log($"Checking IsRAGAvailable...");

                try
                {
                    bool available = bridge.IsRAGAvailable();
                    Debug.Log($"IsRAGAvailable returned: {available}");
                }
                catch (System.Exception e)
                {
                    Debug.LogError($"Exception in IsRAGAvailable: {e.Message}\n{e.StackTrace}");
                }
            }

            Debug.LogWarning("===== SIMPLE TEST END =====");
        }
    }
}
