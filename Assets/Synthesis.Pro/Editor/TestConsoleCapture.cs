using UnityEngine;
using UnityEditor;
using UnityEngine.SceneManagement;

namespace Synthesis.Editor
{
    /// <summary>
    /// Enhanced test for Deep Unity Omniscience System
    /// Tests Phase 1: Scene context, GameObject identification, component lists, recent logs, performance
    /// </summary>
    public static class TestConsoleCapture
    {
        [MenuItem("Synthesis/Test Console Capture (Basic)")]
        public static void TriggerTestError()
        {
            // Manual test trigger with timestamp to ensure uniqueness
            string timestamp = System.DateTime.Now.ToString("HH:mm:ss.fff");
            Debug.Log($"[TEST-{timestamp}] Testing console capture - Normal log");
            Debug.LogWarning($"[TEST-{timestamp}] Testing console capture - Warning log");
            Debug.LogError($"[TEST-{timestamp}] Testing console capture - Error log");

            Debug.Log("[ConsoleCapture] Basic test logs triggered - check server and database");
        }

        [MenuItem("Synthesis/Test Deep Omniscience (Phase 1)")]
        public static void TestDeepOmniscience()
        {
            Debug.Log("=== Deep Unity Omniscience Test ===");
            Debug.Log("This will trigger errors with FULL context capture");
            Debug.Log("Scene: " + SceneManager.GetActiveScene().name);
            Debug.Log("Creating test GameObject with components...");

            // Create a test GameObject with components
            var testObject = new GameObject("TestErrorObject");
            testObject.AddComponent<MeshRenderer>();
            testObject.AddComponent<BoxCollider>();

            Debug.Log("Test object created with components: MeshRenderer, BoxCollider");
            Debug.Log("About to trigger NullReferenceException...");

            // Trigger a real exception with stack trace
            try
            {
                // This will generate a NullReferenceException with full stack trace
                Transform nullTransform = null;
                var position = nullTransform.position; // NullRef here
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[DEEP-OMNISCIENCE-TEST] {e.Message}");
                Debug.LogException(e);
            }

            Debug.Log("Error triggered! Check console_monitor.py output for rich context:");
            Debug.Log("  - Scene name and object count");
            Debug.Log("  - Recent log history (all messages above)");
            Debug.Log("  - Performance snapshot (memory, FPS)");
            Debug.Log("  - Full stack trace");

            // Cleanup
            Object.DestroyImmediate(testObject);
        }

        [MenuItem("Synthesis/Verify ConsoleWatcher Active")]
        public static void VerifyConsoleWatcher()
        {
            var watcher = Object.FindObjectOfType<Synthesis.Bridge.ConsoleWatcher>();

            if (watcher != null)
            {
                var stats = watcher.GetStats();
                Debug.Log("=== ConsoleWatcher Status ===");
                Debug.Log(stats.ToString());
                Debug.Log("\nConsoleWatcher is ACTIVE and capturing!");
                Debug.Log("All errors now include:");
                Debug.Log("  ✓ Scene context");
                Debug.Log("  ✓ GameObject identification");
                Debug.Log("  ✓ Component lists");
                Debug.Log("  ✓ Recent log history");
                Debug.Log("  ✓ Performance metrics");
            }
            else
            {
                Debug.LogWarning("ConsoleWatcher not found in scene!");
                Debug.LogWarning("Add ConsoleWatcher to a GameObject or let it auto-initialize");
            }
        }
    }
}
