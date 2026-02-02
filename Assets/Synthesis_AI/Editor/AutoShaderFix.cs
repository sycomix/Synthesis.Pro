using UnityEngine;
using UnityEditor;
using System.IO;

namespace Synthesis.Editor
{
    /// <summary>
    /// Automatically fixes LegendaryWarriorUI shaders on first import
    /// Runs once, then marks itself as complete
    /// </summary>
    [InitializeOnLoad]
    public static class AutoShaderFix
    {
        private const string PREF_KEY = "Synthesis.ShaderFixComplete";

        static AutoShaderFix()
        {
            // Only run once
            if (EditorPrefs.GetBool(PREF_KEY, false))
            {
                return;
            }

            // Check if LegendaryWarriorUI is imported
            if (!Directory.Exists("Assets/LegendaryWarriorUI"))
            {
                return;
            }

            // Delay to let Unity finish initializing
            EditorApplication.delayCall += () =>
            {
                // Check if shaders exist
                string[] shaderPaths = new string[]
                {
                    "Assets/LegendaryWarriorUI/Shaders/CanvasShaders/HpBar.shadergraph",
                    "Assets/LegendaryWarriorUI/Shaders/CanvasShaders/BlueMenSymetric.shadergraph",
                    "Assets/LegendaryWarriorUI/Shaders/CanvasShaders/MPLine.shadergraph"
                };

                bool anyExist = false;
                foreach (string path in shaderPaths)
                {
                    if (File.Exists(path))
                    {
                        anyExist = true;
                        break;
                    }
                }

                if (!anyExist)
                {
                    return;
                }

                Debug.Log("[AutoShaderFix] LegendaryWarriorUI detected - fixing shaders automatically...");

                // Run the fix
                try
                {
                    ShaderGraphFixer.FixShaders();
                    EditorPrefs.SetBool(PREF_KEY, true);
                    Debug.Log("[AutoShaderFix] ✅ Shaders fixed! This will not run again.");
                }
                catch (System.Exception e)
                {
                    Debug.LogError($"[AutoShaderFix] Failed to auto-fix shaders: {e.Message}");
                    Debug.Log("[AutoShaderFix] You can manually fix via: Synthesis > Fix LegendaryWarriorUI Shaders");
                }
            };
        }

        [MenuItem("Synthesis/Reset Shader Auto-Fix")]
        public static void ResetAutoFix()
        {
            EditorPrefs.DeleteKey(PREF_KEY);
            Debug.Log("[AutoShaderFix] Reset complete. Auto-fix will run on next Unity restart.");
        }
    }
}
