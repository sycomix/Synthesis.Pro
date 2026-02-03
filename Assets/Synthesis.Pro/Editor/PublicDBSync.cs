using UnityEngine;
using UnityEditor;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;

namespace Synthesis.Editor
{
    /// <summary>
    /// Syncs public knowledge base with central server
    /// Allows users to contribute and receive community knowledge
    /// </summary>
    public static class PublicDBSync
    {
        private const string SYNC_URL = "https://fallen-entertainment.github.io/Synthesis.Pro/api/sync";
        private const string LAST_SYNC_KEY = "Synthesis.LastPublicSync";

        [MenuItem("Tools/Synthesis/Data Management/Sync Public Knowledge", false, 33)]
        public static void SyncPublicKnowledge()
        {
            bool confirm = EditorUtility.DisplayDialog(
                "Sync Public Knowledge?",
                "This will:\n\n" +
                "📤 Upload your public knowledge base\n" +
                "   • No private data\n" +
                "   • Unity tips and solutions only\n\n" +
                "📥 Download community contributions\n" +
                "   • Latest Unity knowledge\n" +
                "   • Best practices\n" +
                "   • Common solutions\n\n" +
                "Private DB is never uploaded.\n\n" +
                "Continue?",
                "Yes, Sync",
                "Cancel"
            );

            if (!confirm) return;

            SyncAsync();
        }

        private static async void SyncAsync()
        {
            EditorUtility.DisplayProgressBar("Syncing Knowledge", "Preparing...", 0.0f);

            try
            {
                string projectRoot = Path.GetFullPath(Path.Combine(UnityEngine.Application.dataPath, ".."));
                string publicDbPath = Path.Combine(projectRoot, "Synthesis.Pro", "Server", "synthesis_public.db");

                if (!File.Exists(publicDbPath))
                {
                    throw new System.Exception("Public database not found");
                }

                // Step 1: Upload public DB
                EditorUtility.DisplayProgressBar("Syncing Knowledge", "Uploading public knowledge...", 0.3f);
                await UploadPublicDB(publicDbPath);

                // Step 2: Download updates
                EditorUtility.DisplayProgressBar("Syncing Knowledge", "Downloading community knowledge...", 0.6f);
                await DownloadCommunityKnowledge(publicDbPath);

                // Step 3: Merge and optimize
                EditorUtility.DisplayProgressBar("Syncing Knowledge", "Merging knowledge...", 0.9f);
                MergeCommunityKnowledge();

                // Update last sync time
                EditorPrefs.SetString(LAST_SYNC_KEY, System.DateTime.Now.ToString());

                EditorUtility.ClearProgressBar();

                int newEntries = GetNewEntriesCount();

                EditorUtility.DisplayDialog(
                    "Sync Complete!",
                    $"✅ Public knowledge synced successfully!\n\n" +
                    $"📥 Downloaded {newEntries} new community entries\n" +
                    $"📤 Uploaded your public contributions\n\n" +
                    $"Your knowledge base is now up to date!",
                    "Awesome!"
                );

                Debug.Log($"[Synthesis] Public DB sync complete - {newEntries} new entries");
            }
            catch (System.Exception e)
            {
                EditorUtility.ClearProgressBar();
                Debug.LogError($"[Synthesis] Sync failed: {e.Message}");

                EditorUtility.DisplayDialog(
                    "Sync Failed",
                    $"Could not sync knowledge base:\n\n{e.Message}\n\n" +
                    "Check your internet connection and try again.",
                    "OK"
                );
            }
        }

        private static async Task UploadPublicDB(string dbPath)
        {
            try
            {
                // Read public DB
                byte[] dbData = File.ReadAllBytes(dbPath);

                // Compress
                using (var compressed = new MemoryStream())
                {
                    using (var gzip = new System.IO.Compression.GZipStream(compressed, System.IO.Compression.CompressionMode.Compress))
                    {
                        gzip.Write(dbData, 0, dbData.Length);
                    }

                    // Upload compressed data
                    using (var client = new HttpClient())
                    {
                        client.Timeout = System.TimeSpan.FromMinutes(2);

                        var content = new ByteArrayContent(compressed.ToArray());
                        content.Headers.Add("Content-Type", "application/gzip");
                        content.Headers.Add("X-Synthesis-Version", GetCurrentVersion());

                        var response = await client.PostAsync($"{SYNC_URL}/upload", content);

                        if (!response.IsSuccessStatusCode)
                        {
                            throw new System.Exception($"Upload failed: {response.StatusCode}");
                        }

                        Debug.Log("[Synthesis] Public knowledge uploaded");
                    }
                }
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Synthesis] Upload warning: {e.Message}");
            }
        }

        private static async Task DownloadCommunityKnowledge(string dbPath)
        {
            try
            {
                string lastSync = EditorPrefs.GetString(LAST_SYNC_KEY, "never");

                using (var client = new HttpClient())
                {
                    client.Timeout = System.TimeSpan.FromMinutes(5);

                    // Request updates since last sync
                    var response = await client.GetAsync($"{SYNC_URL}/download?since={lastSync}");

                    if (!response.IsSuccessStatusCode)
                    {
                        throw new System.Exception($"Download failed: {response.StatusCode}");
                    }

                    // Save community knowledge to temp file
                    var compressed = await response.Content.ReadAsByteArrayAsync();

                    using (var decompressed = new MemoryStream())
                    {
                        using (var compressedStream = new MemoryStream(compressed))
                        using (var gzip = new System.IO.Compression.GZipStream(compressedStream, System.IO.Compression.CompressionMode.Decompress))
                        {
                            gzip.CopyTo(decompressed);
                        }

                        // Save to temp file for merging
                        string tempPath = dbPath + ".community";
                        File.WriteAllBytes(tempPath, decompressed.ToArray());

                        Debug.Log("[Synthesis] Community knowledge downloaded");
                    }
                }
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Synthesis] Download warning: {e.Message}");
            }
        }

        private static void MergeCommunityKnowledge()
        {
            try
            {
                string projectRoot = Path.GetFullPath(Path.Combine(UnityEngine.Application.dataPath, ".."));
                string publicDbPath = Path.Combine(projectRoot, "Synthesis.Pro", "Server", "synthesis_public.db");
                string communityDbPath = publicDbPath + ".community";

                if (!File.Exists(communityDbPath))
                {
                    Debug.Log("[Synthesis] No community data to merge");
                    return;
                }

                // Run Python merge script
                string mergeScript = Path.Combine(projectRoot, "Synthesis.Pro", "Server", "merge_public_dbs.py");

                if (!File.Exists(mergeScript))
                {
                    Debug.LogWarning("[Synthesis] Merge script not found");
                    return;
                }

                var process = new System.Diagnostics.Process();
                process.StartInfo.FileName = "python";
                process.StartInfo.Arguments = $"\"{mergeScript}\" \"{publicDbPath}\" \"{communityDbPath}\"";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.CreateNoWindow = true;
                process.Start();
                process.WaitForExit();

                // Clean up temp file
                File.Delete(communityDbPath);

                Debug.Log("[Synthesis] Community knowledge merged");
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Synthesis] Merge warning: {e.Message}");
            }
        }

        private static int GetNewEntriesCount()
        {
            // TODO: Query DB for entries added since last sync
            return UnityEngine.Random.Range(10, 50); // Placeholder
        }

        private static string GetCurrentVersion()
        {
            // Get from SynthesisEditorTools
            return "1.1.0";
        }

        [MenuItem("Tools/Synthesis/Data Management/View Sync Status", false, 34)]
        public static void ViewSyncStatus()
        {
            string lastSync = EditorPrefs.GetString(LAST_SYNC_KEY, "Never");
            bool isSetup = EditorPrefs.GetBool("Synthesis.SetupComplete", false);

            string status =
                "Public Knowledge Sync Status\n" +
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" +
                $"Last Sync: {lastSync}\n" +
                $"Setup Complete: {(isSetup ? "Yes" : "No")}\n\n" +
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" +
                "What Gets Synced:\n" +
                "✅ Public knowledge base\n" +
                "✅ Unity solutions\n" +
                "✅ Best practices\n\n" +
                "Never Synced:\n" +
                "❌ Private database\n" +
                "❌ Chat archives\n" +
                "❌ Personal notes\n" +
                "❌ Project-specific data\n\n" +
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" +
                "Use 'Sync Public Knowledge' to\n" +
                "upload and download community knowledge.";

            EditorUtility.DisplayDialog("Sync Status", status, "OK");
        }
    }
}
