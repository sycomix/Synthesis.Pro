using UnityEngine;
using UnityEditor;
using System.IO;
using System.Collections.Generic;

namespace Synthesis.Editor
{
    /// <summary>
    /// Fixes broken ShaderGraph files by forcing reimport
    /// LegendaryWarriorUI shaders need this after first import
    /// </summary>
    public class ShaderGraphFixer : EditorWindow
    {
        private static readonly string[] brokenShaderPaths = new string[]
        {
            "Assets/LegendaryWarriorUI/Shaders/CanvasShaders/HpBar.shadergraph",
            "Assets/LegendaryWarriorUI/Shaders/CanvasShaders/BlueMenSymetric.shadergraph",
            "Assets/LegendaryWarriorUI/Shaders/CanvasShaders/MPLine.shadergraph"
        };

        [MenuItem("Synthesis/Fix LegendaryWarriorUI Shaders")]
        public static void FixShaders()
        {
            Debug.Log("[ShaderFixer] Starting shader fix process...");

            int fixedCount = 0;
            int errorCount = 0;
            List<string> fixedShaders = new List<string>();
            List<string> errorShaders = new List<string>();

            foreach (string shaderPath in brokenShaderPaths)
            {
                if (!File.Exists(shaderPath))
                {
                    Debug.LogWarning($"[ShaderFixer] Shader not found: {shaderPath}");
                    continue;
                }

                try
                {
                    Debug.Log($"[ShaderFixer] Fixing: {shaderPath}");

                    // Force reimport with different import options
                    AssetDatabase.ImportAsset(shaderPath, ImportAssetOptions.ForceUpdate | ImportAssetOptions.DontDownloadFromCacheServer);

                    fixedShaders.Add(Path.GetFileName(shaderPath));
                    fixedCount++;
                }
                catch (System.Exception e)
                {
                    Debug.LogError($"[ShaderFixer] Failed to fix {shaderPath}: {e.Message}");
                    errorShaders.Add(Path.GetFileName(shaderPath));
                    errorCount++;
                }
            }

            AssetDatabase.Refresh();

            // Show results
            string resultMessage = $"Shader Fix Complete\n\n";
            resultMessage += $"✅ Fixed: {fixedCount}\n";
            if (fixedShaders.Count > 0)
            {
                resultMessage += string.Join("\n", fixedShaders) + "\n\n";
            }

            if (errorCount > 0)
            {
                resultMessage += $"❌ Errors: {errorCount}\n";
                resultMessage += string.Join("\n", errorShaders) + "\n\n";
                resultMessage += "You may need to manually open and save these shaders.\n";
                resultMessage += "See: Assets/LegendaryWarriorUI/FixShaders.pdf";
            }

            Debug.Log($"[ShaderFixer] {resultMessage}");

            EditorUtility.DisplayDialog("Shader Fix Complete", resultMessage, "OK");
        }

        [MenuItem("Synthesis/Fix All ShaderGraphs in Project")]
        public static void FixAllShaderGraphs()
        {
            Debug.Log("[ShaderFixer] Fixing ALL .shadergraph files in project...");

            string[] allShaderGraphs = AssetDatabase.FindAssets("t:Shader", new[] { "Assets" });
            int reimportedCount = 0;

            foreach (string guid in allShaderGraphs)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (path.EndsWith(".shadergraph"))
                {
                    Debug.Log($"[ShaderFixer] Reimporting: {path}");
                    AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceUpdate);
                    reimportedCount++;
                }
            }

            AssetDatabase.Refresh();

            string message = $"Reimported {reimportedCount} ShaderGraph files.\n\nCheck console for any remaining errors.";
            Debug.Log($"[ShaderFixer] {message}");
            EditorUtility.DisplayDialog("ShaderGraph Fix Complete", message, "OK");
        }
    }
}
