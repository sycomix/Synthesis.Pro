using UnityEditor;
using UnityEngine;
using System.IO;
using System.Linq;

namespace Synthesis.Editor
{
    /// <summary>
    /// Exports Synthesis.Pro as a Unity package for distribution
    /// Copies UPM package from Synthesis.Pro/ to Assets/ for export, then cleans up
    /// </summary>
    public static class ExportPackage
    {
        // Runtime dependencies excluded from package (downloaded via FirstTimeSetup)
        private static readonly string[] EXCLUDED_FOLDERS = new string[]
        {
            "python",
            "node",
            "models"
        };

        private static readonly string[] EXCLUDED_FILES = new string[]
        {
            "synthesis_private.db",
            "synthesis_knowledge.db",
            "synthesis_public.db"
        };

        [MenuItem("Tools/Synthesis/Export Package")]
        public static void Export()
        {
            string packageName = "Synthesis.Pro.unitypackage";
            string sourceFolder = Path.Combine(Application.dataPath, "..", "Synthesis.Pro");
            string targetFolder = Path.Combine(Application.dataPath, "Synthesis.Pro");

            if (!Directory.Exists(sourceFolder))
            {
                Debug.LogError($"[Export] Source folder not found: {sourceFolder}");
                return;
            }

            try
            {
                Debug.Log("[Export] Copying package to Assets for export...");

                // Copy to Assets, excluding runtime deps
                CopyDirectoryFiltered(sourceFolder, targetFolder);

                // Refresh so Unity sees the new files
                AssetDatabase.Refresh();

                Debug.Log($"[Export] Creating package: {packageName}");

                // Export the package
                AssetDatabase.ExportPackage(
                    "Assets/Synthesis.Pro",
                    packageName,
                    ExportPackageOptions.Recurse
                );

                Debug.Log($"[Export] Package created successfully: {packageName}");

                // Show in file explorer
                EditorUtility.RevealInFinder(Path.GetFullPath(packageName));
            }
            finally
            {
                // Clean up - remove from Assets
                if (Directory.Exists(targetFolder))
                {
                    Debug.Log("[Export] Cleaning up temporary files...");
                    Directory.Delete(targetFolder, true);
                    File.Delete(targetFolder + ".meta");
                    AssetDatabase.Refresh();
                }
            }
        }

        private static void CopyDirectoryFiltered(string sourcePath, string targetPath)
        {
            Directory.CreateDirectory(targetPath);

            // Copy files
            foreach (string file in Directory.GetFiles(sourcePath))
            {
                string fileName = Path.GetFileName(file);

                // Skip excluded files
                if (EXCLUDED_FILES.Any(excluded => fileName.Contains(excluded)))
                {
                    Debug.Log($"[Export] Excluding file: {fileName}");
                    continue;
                }

                string targetFile = Path.Combine(targetPath, fileName);
                File.Copy(file, targetFile, true);
            }

            // Copy subdirectories recursively
            foreach (string directory in Directory.GetDirectories(sourcePath))
            {
                string dirName = Path.GetFileName(directory);

                // Skip excluded folders
                if (EXCLUDED_FOLDERS.Contains(dirName))
                {
                    Debug.Log($"[Export] Excluding folder: {dirName}");
                    continue;
                }

                string targetDir = Path.Combine(targetPath, dirName);
                CopyDirectoryFiltered(directory, targetDir);
            }
        }

        /// <summary>
        /// Export method for CI/CD (no UI interactions)
        /// </summary>
        public static void ExportCI()
        {
            try
            {
                Export();
                EditorApplication.Exit(0);
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Export CI] Failed: {e.Message}");
                EditorApplication.Exit(1);
            }
        }
    }
}
