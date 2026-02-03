using UnityEditor;
using UnityEngine;
using System.IO;

namespace Synthesis.Editor
{
    /// <summary>
    /// Exports Synthesis.Pro as a Unity package for distribution
    /// Called by GitHub Actions for automated releases
    /// </summary>
    public static class ExportPackage
    {
        [MenuItem("Tools/Synthesis/Export Package")]
        public static void Export()
        {
            string packageName = "Synthesis.Pro.unitypackage";

            // Define what to include in the package
            string[] assetPaths = new string[]
            {
                "Assets/Synthesis.Pro",
                "Assets/Synthesis_AI" // Legacy name support
            };

            // Filter to only existing paths
            var existingPaths = new System.Collections.Generic.List<string>();
            foreach (var path in assetPaths)
            {
                if (AssetDatabase.IsValidFolder(path) || File.Exists(path))
                {
                    existingPaths.Add(path);
                }
            }

            if (existingPaths.Count == 0)
            {
                Debug.LogError("[Export] No valid asset paths found to export!");
                return;
            }

            // Export flags
            ExportPackageOptions options =
                ExportPackageOptions.Recurse |
                ExportPackageOptions.IncludeDependencies;

            Debug.Log($"[Export] Creating package: {packageName}");
            Debug.Log($"[Export] Including paths: {string.Join(", ", existingPaths)}");

            // Export the package
            AssetDatabase.ExportPackage(
                existingPaths.ToArray(),
                packageName,
                options
            );

            Debug.Log($"[Export] ✅ Package created successfully: {packageName}");

            // Show in file explorer
            EditorUtility.RevealInFinder(Path.GetFullPath(packageName));
        }

        /// <summary>
        /// Export method for CI/CD (no UI interactions)
        /// </summary>
        public static void ExportCI()
        {
            string packageName = "Synthesis.Pro.unitypackage";

            string[] assetPaths = new string[]
            {
                "Assets/Synthesis.Pro",
                "Assets/Synthesis_AI"
            };

            var existingPaths = new System.Collections.Generic.List<string>();
            foreach (var path in assetPaths)
            {
                if (AssetDatabase.IsValidFolder(path) || File.Exists(path))
                {
                    existingPaths.Add(path);
                }
            }

            if (existingPaths.Count == 0)
            {
                Debug.LogError("[Export CI] No valid asset paths found!");
                EditorApplication.Exit(1);
                return;
            }

            ExportPackageOptions options =
                ExportPackageOptions.Recurse |
                ExportPackageOptions.IncludeDependencies;

            Debug.Log($"[Export CI] Exporting {packageName}...");

            try
            {
                AssetDatabase.ExportPackage(
                    existingPaths.ToArray(),
                    packageName,
                    options
                );

                Debug.Log($"[Export CI] ✅ Success: {packageName}");
                EditorApplication.Exit(0);
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Export CI] ❌ Failed: {e.Message}");
                EditorApplication.Exit(1);
            }
        }
    }
}
