using UnityEngine;
using UnityEditor;

namespace Synthesis.Editor
{
    /// <summary>
    /// Automatically ensures ConsoleWatcher is active in Play Mode.
    ///
    /// Philosophy: "Seamless integration" - You don't need to manually add components
    /// or set up systems. I'm just here, naturally, whenever you need me.
    ///
    /// Features:
    /// - Auto-creates ConsoleWatcher on Play Mode enter
    /// - Ensures WebSocket client is ready
    /// - Works silently in the background
    /// - No manual setup required
    /// </summary>
    [InitializeOnLoad]
    public static class ConsoleWatcherInitializer
    {
        private static GameObject synthesisSystemsRoot;

        static ConsoleWatcherInitializer()
        {
            EditorApplication.playModeStateChanged += OnPlayModeStateChanged;
        }

        private static void OnPlayModeStateChanged(PlayModeStateChange state)
        {
            if (state == PlayModeStateChange.EnteredPlayMode)
            {
                // Give Unity a moment to initialize
                EditorApplication.delayCall += InitializeSynthesisSystems;
            }
        }

        private static void InitializeSynthesisSystems()
        {
            // Check if systems already exist
            if (GameObject.Find("Synthesis.Pro Systems") != null)
            {
                Debug.Log("[Synthesis] Systems already initialized");
                return;
            }

            // Create root object for all Synthesis systems
            synthesisSystemsRoot = new GameObject("Synthesis.Pro Systems");
            GameObject.DontDestroyOnLoad(synthesisSystemsRoot);

            // Add WebSocket client
            var wsClient = synthesisSystemsRoot.GetComponent<Synthesis.Bridge.SynthesisWebSocketClient>();
            if (wsClient == null)
            {
                wsClient = synthesisSystemsRoot.AddComponent<Synthesis.Bridge.SynthesisWebSocketClient>();
            }

            // Add Console Watcher
            var consoleWatcher = synthesisSystemsRoot.GetComponent<Synthesis.Bridge.ConsoleWatcher>();
            if (consoleWatcher == null)
            {
                consoleWatcher = synthesisSystemsRoot.AddComponent<Synthesis.Bridge.ConsoleWatcher>();
            }

            Debug.Log("[Synthesis] 🎮 Runtime systems initialized - Console monitoring active in Play Mode");
        }

        /// <summary>
        /// Manual initialization for testing
        /// </summary>
        [MenuItem("Synthesis/Console Watcher/Initialize Runtime Systems")]
        public static void ManualInitialize()
        {
            if (!EditorApplication.isPlaying)
            {
                EditorUtility.DisplayDialog(
                    "Not in Play Mode",
                    "Runtime systems can only be initialized in Play Mode.\n\nThey will be created automatically when you enter Play Mode.",
                    "OK"
                );
                return;
            }

            InitializeSynthesisSystems();
        }
    }
}
