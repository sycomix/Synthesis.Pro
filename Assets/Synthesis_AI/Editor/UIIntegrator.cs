using UnityEngine;
using UnityEditor;
using UnityEngine.UI;
using System.IO;
using System.Collections.Generic;

namespace Synthesis.Editor
{
    /// <summary>
    /// Integrates LegendaryWarriorUI components into MMORPG Kit CanvasGameplay
    /// </summary>
    public class UIIntegrator : EditorWindow
    {
        private const string CANVAS_PATH = "Assets/UI Project/CanvasGameplay.prefab";
        private const string LEGENDARY_UI_PATH = "Assets/LegendaryWarriorUI/Prefabs/";

        private GameObject canvasPrefab;
        private bool integrationComplete = false;

        [MenuItem("Synthesis/UI Integration/Open UI Integrator")]
        public static void OpenWindow()
        {
            UIIntegrator window = GetWindow<UIIntegrator>("UI Integrator");
            window.minSize = new Vector2(400, 600);
            window.Show();
        }

        private void OnGUI()
        {
            GUILayout.Label("LegendaryWarriorUI Integration Tool", EditorStyles.boldLabel);
            GUILayout.Space(10);

            // Status
            EditorGUILayout.HelpBox(
                "This tool integrates LegendaryWarriorUI visual components into the MMORPG Kit CanvasGameplay prefab.\n\n" +
                "All MMORPG Kit functionality will be preserved - only visuals will be enhanced.",
                MessageType.Info
            );

            GUILayout.Space(10);

            // Load prefab
            if (GUILayout.Button("1. Load CanvasGameplay Prefab", GUILayout.Height(30)))
            {
                LoadCanvasPrefab();
            }

            if (canvasPrefab != null)
            {
                EditorGUILayout.HelpBox("✅ Prefab Loaded: " + canvasPrefab.name, MessageType.None);
            }

            GUILayout.Space(10);

            EditorGUI.BeginDisabledGroup(canvasPrefab == null);

            // Integration options
            GUILayout.Label("Integration Options:", EditorStyles.boldLabel);

            if (GUILayout.Button("2. Add Status Bar (HP/MP)", GUILayout.Height(30)))
            {
                IntegrateStatusBar();
            }

            if (GUILayout.Button("3. Add Minimap", GUILayout.Height(30)))
            {
                IntegrateMinimap();
            }

            if (GUILayout.Button("4. Integrate All Components", GUILayout.Height(30)))
            {
                IntegrateAll();
            }

            GUILayout.Space(10);
            GUILayout.Label("Sizing Fixes:", EditorStyles.boldLabel);

            if (GUILayout.Button("5. Fix Sizing (Use MMORPG Kit Proportions)", GUILayout.Height(30)))
            {
                FixComponentSizing();
            }

            if (GUILayout.Button("6. Clean Up Duplicates", GUILayout.Height(30)))
            {
                CleanUpDuplicates();
            }

            EditorGUI.EndDisabledGroup();

            GUILayout.Space(20);

            if (integrationComplete)
            {
                EditorGUILayout.HelpBox("✅ Integration Complete! Check CanvasGameplay prefab.", MessageType.Info);
            }

            GUILayout.FlexibleSpace();

            // Documentation
            EditorGUILayout.HelpBox(
                "For more information, see:\n" +
                "- UI_INTEGRATION_STRATEGY.md\n" +
                "- Assets/LegendaryWarriorUI/Documentation.pdf",
                MessageType.None
            );
        }

        private void LoadCanvasPrefab()
        {
            canvasPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(CANVAS_PATH);

            if (canvasPrefab == null)
            {
                EditorUtility.DisplayDialog(
                    "Error",
                    $"Could not load prefab at:\n{CANVAS_PATH}\n\nMake sure the prefab exists.",
                    "OK"
                );
                return;
            }

            Debug.Log($"[UIIntegrator] Loaded prefab: {canvasPrefab.name}");
        }

        private void IntegrateStatusBar()
        {
            Debug.Log("[UIIntegrator] Starting Status Bar integration...");

            // Load the LegendaryWarriorUI status bar prefab
            string statusBarPath = LEGENDARY_UI_PATH + "RPGStatusBar.prefab";
            GameObject statusBarPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(statusBarPath);

            if (statusBarPrefab == null)
            {
                Debug.LogError($"[UIIntegrator] Could not find status bar at: {statusBarPath}");
                EditorUtility.DisplayDialog("Error", "Could not find RPGStatusBar prefab", "OK");
                return;
            }

            // Instantiate the canvas for editing
            GameObject canvasInstance = PrefabUtility.InstantiatePrefab(canvasPrefab) as GameObject;

            if (canvasInstance == null)
            {
                Debug.LogError("[UIIntegrator] Failed to instantiate canvas prefab");
                return;
            }

            // Remove existing status bar if present (avoid duplicates)
            Transform existingStatusBar = canvasInstance.transform.Find("RPGStatusBar(Clone)");
            if (existingStatusBar == null)
            {
                existingStatusBar = canvasInstance.transform.Find("RPGStatusBar");
            }
            if (existingStatusBar != null)
            {
                Debug.Log("[UIIntegrator] Removing existing status bar to avoid duplicates");
                DestroyImmediate(existingStatusBar.gameObject);
            }

            // Create status bar instance as child of canvas
            GameObject statusBar = PrefabUtility.InstantiatePrefab(statusBarPrefab, canvasInstance.transform) as GameObject;

            if (statusBar == null)
            {
                Debug.LogError("[UIIntegrator] Failed to instantiate status bar");
                DestroyImmediate(canvasInstance);
                return;
            }

            // PROPER SIZING: Match reference layout (bottom-left, compact horizontal)
            RectTransform statusBarRect = statusBar.GetComponent<RectTransform>();
            if (statusBarRect != null)
            {
                // Scale it down first (original is 701.8x261, scaled to 0.25 = 175.5x65.25)
                float scale = 0.25f;
                statusBarRect.localScale = new Vector3(scale, scale, 1f);

                // Original size from prefab
                Vector2 originalSize = new Vector2(701.8f, 261f);
                Vector2 scaledSize = originalSize * scale; // 175.5 x 65.25

                // Position: Bottom-left with center pivot (0.5, 0.5)
                // Center pivot means we offset by half the element's size
                statusBarRect.anchorMin = new Vector2(0, 0);
                statusBarRect.anchorMax = new Vector2(0, 0);
                statusBarRect.pivot = new Vector2(0.5f, 0.5f); // Center pivot like original

                // Position = margin + half of scaled size
                float margin = 15f;
                float xPos = margin + (scaledSize.x / 2f); // 15 + 87.75 = 102.75
                float yPos = margin + (scaledSize.y / 2f); // 15 + 32.63 = 47.63
                statusBarRect.anchoredPosition = new Vector2(xPos, yPos);

                // Keep original sizeDelta (don't override)
                // sizeDelta is relative to anchors, keep the prefab's value
            }

            // Apply changes back to prefab
            string prefabPath = AssetDatabase.GetAssetPath(canvasPrefab);
            PrefabUtility.SaveAsPrefabAsset(canvasInstance, prefabPath);

            // Cleanup
            DestroyImmediate(canvasInstance);

            Debug.Log("[UIIntegrator] ✅ Status Bar integrated successfully with proper sizing!");
            EditorUtility.DisplayDialog("Success", "Status Bar integrated with proper sizing!", "OK");

            integrationComplete = true;
        }

        private void IntegrateMinimap()
        {
            Debug.Log("[UIIntegrator] Starting Minimap integration...");

            string minimapPath = LEGENDARY_UI_PATH + "Minimap.prefab";
            GameObject minimapPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(minimapPath);

            if (minimapPrefab == null)
            {
                Debug.LogError($"[UIIntegrator] Could not find minimap at: {minimapPath}");
                EditorUtility.DisplayDialog("Error", "Could not find Minimap prefab", "OK");
                return;
            }

            GameObject canvasInstance = PrefabUtility.InstantiatePrefab(canvasPrefab) as GameObject;
            if (canvasInstance == null) return;

            // Remove existing minimap if present (avoid duplicates)
            Transform existingMinimap = canvasInstance.transform.Find("Minimap(Clone)");
            if (existingMinimap == null)
            {
                existingMinimap = canvasInstance.transform.Find("Minimap");
            }
            if (existingMinimap != null)
            {
                Debug.Log("[UIIntegrator] Removing existing minimap to avoid duplicates");
                DestroyImmediate(existingMinimap.gameObject);
            }

            GameObject minimap = PrefabUtility.InstantiatePrefab(minimapPrefab, canvasInstance.transform) as GameObject;
            if (minimap == null)
            {
                DestroyImmediate(canvasInstance);
                return;
            }

            // PROPER SIZING: Match reference layout (very compact)
            RectTransform minimapRect = minimap.GetComponent<RectTransform>();
            if (minimapRect != null)
            {
                // Scale it down first (original is 350x349, scaled to 0.2 = 70x69.8)
                float scale = 0.2f;
                minimapRect.localScale = new Vector3(scale, scale, 1f);

                // Original size from prefab
                Vector2 originalSize = new Vector2(350f, 349f);
                Vector2 scaledSize = originalSize * scale; // 70 x 69.8

                // Position: Top-right with center pivot (0.5, 0.5)
                // Center pivot means we offset by half the element's size
                minimapRect.anchorMin = new Vector2(1, 1);
                minimapRect.anchorMax = new Vector2(1, 1);
                minimapRect.pivot = new Vector2(0.5f, 0.5f); // Center pivot like original

                // Position = -margin - half of scaled size (negative for top-right)
                float margin = 15f;
                float xPos = -(margin + (scaledSize.x / 2f)); // -(15 + 35) = -50
                float yPos = -(margin + (scaledSize.y / 2f)); // -(15 + 34.9) = -49.9
                minimapRect.anchoredPosition = new Vector2(xPos, yPos);

                // Keep original sizeDelta (don't override)
                // sizeDelta is relative to anchors, keep the prefab's value
            }

            string prefabPath = AssetDatabase.GetAssetPath(canvasPrefab);
            PrefabUtility.SaveAsPrefabAsset(canvasInstance, prefabPath);
            DestroyImmediate(canvasInstance);

            Debug.Log("[UIIntegrator] ✅ Minimap integrated with proper sizing!");
            EditorUtility.DisplayDialog("Success", "Minimap integrated with proper sizing!", "OK");

            integrationComplete = true;
        }

        private void IntegrateAll()
        {
            if (EditorUtility.DisplayDialog(
                "Integrate All Components?",
                "This will integrate all LegendaryWarriorUI components into CanvasGameplay.\n\n" +
                "This process cannot be undone (backup recommended).\n\n" +
                "Continue?",
                "Yes, Integrate",
                "Cancel"))
            {
                Debug.Log("[UIIntegrator] Starting full integration...");

                // Integrate components in order
                IntegrateStatusBar();
                IntegrateMinimap();
                // TODO: Add more integrations as needed

                Debug.Log("[UIIntegrator] ✅ Full integration complete!");
                EditorUtility.DisplayDialog(
                    "Integration Complete",
                    "All LegendaryWarriorUI components have been integrated!\n\n" +
                    "Check CanvasGameplay prefab to see the results.",
                    "OK"
                );

                integrationComplete = true;
            }
        }

        private void FixComponentSizing()
        {
            Debug.Log("[UIIntegrator] Starting sizing fix...");

            // Load reference prefab (Demo CanvasGameplay)
            string demoCanvasPath = "Assets/UnityMultiplayerARPG/Demo/Prefabs/UI/_Gameplay/CanvasGameplay.prefab";
            GameObject demoCanvas = AssetDatabase.LoadAssetAtPath<GameObject>(demoCanvasPath);

            if (demoCanvas == null)
            {
                Debug.LogWarning("[UIIntegrator] Could not find demo canvas for reference, using hardcoded values");
            }

            GameObject canvasInstance = PrefabUtility.InstantiatePrefab(canvasPrefab) as GameObject;
            if (canvasInstance == null)
            {
                Debug.LogError("[UIIntegrator] Failed to instantiate canvas");
                return;
            }

            int fixedCount = 0;

            // Find and fix RPGStatusBar - MATCH REFERENCE LAYOUT
            Transform statusBar = canvasInstance.transform.Find("RPGStatusBar");
            if (statusBar != null)
            {
                RectTransform rect = statusBar.GetComponent<RectTransform>();
                if (rect != null)
                {
                    // REFERENCE LAYOUT: Compact horizontal bar, bottom-left
                    rect.anchorMin = new Vector2(0, 0);
                    rect.anchorMax = new Vector2(0, 0);
                    rect.pivot = new Vector2(0, 0);
                    rect.anchoredPosition = new Vector2(15, 80); // Bottom-left with padding
                    rect.localScale = new Vector3(0.25f, 0.25f, 1f); // 25% scale for compactness
                    rect.sizeDelta = new Vector2(350, 120); // Horizontal layout
                    fixedCount++;
                    Debug.Log("[UIIntegrator] Fixed RPGStatusBar to match reference layout");
                }
            }

            // Find and fix Minimap - MATCH REFERENCE LAYOUT
            Transform minimap = canvasInstance.transform.Find("Minimap");
            if (minimap != null)
            {
                RectTransform rect = minimap.GetComponent<RectTransform>();
                if (rect != null)
                {
                    // REFERENCE LAYOUT: Very small, top-right or could be diamond item grid bottom-right
                    // For now, keeping top-right but much smaller
                    rect.anchorMin = new Vector2(1, 1);
                    rect.anchorMax = new Vector2(1, 1);
                    rect.pivot = new Vector2(1, 1);
                    rect.anchoredPosition = new Vector2(-15, -15);
                    rect.localScale = new Vector3(0.2f, 0.2f, 1f); // 20% scale - very compact
                    rect.sizeDelta = new Vector2(180, 180);
                    fixedCount++;
                    Debug.Log("[UIIntegrator] Fixed Minimap to match reference layout");
                }
            }

            // Find and fix any other oversized LegendaryWarriorUI components
            foreach (Transform child in canvasInstance.transform)
            {
                // Check if it's a LegendaryWarriorUI component (they're typically large)
                RectTransform rect = child.GetComponent<RectTransform>();
                if (rect != null && rect.sizeDelta.magnitude > 500)
                {
                    // If it's unusually large and not one we already fixed
                    if (child.name != "RPGStatusBar" && child.name != "Minimap")
                    {
                        // Apply conservative scaling
                        float currentScale = rect.localScale.x;
                        if (currentScale > 0.5f)
                        {
                            rect.localScale = new Vector3(0.5f, 0.5f, 1f);
                            fixedCount++;
                            Debug.Log($"[UIIntegrator] Fixed {child.name} sizing");
                        }
                    }
                }
            }

            // Save changes
            string prefabPath = AssetDatabase.GetAssetPath(canvasPrefab);
            PrefabUtility.SaveAsPrefabAsset(canvasInstance, prefabPath);
            DestroyImmediate(canvasInstance);

            Debug.Log($"[UIIntegrator] ✅ Fixed {fixedCount} component(s)!");
            EditorUtility.DisplayDialog(
                "Sizing Fixed",
                $"Fixed {fixedCount} component(s) to match MMORPG Kit proportions.\n\n" +
                "Components are now sized appropriately for gameplay.",
                "OK"
            );

            integrationComplete = true;
        }

        private void CleanUpDuplicates()
        {
            Debug.Log("[UIIntegrator] Starting duplicate cleanup...");

            GameObject canvasInstance = PrefabUtility.InstantiatePrefab(canvasPrefab) as GameObject;
            if (canvasInstance == null)
            {
                Debug.LogError("[UIIntegrator] Failed to instantiate canvas");
                return;
            }

            int removedCount = 0;
            List<Transform> toRemove = new List<Transform>();

            // Strategy: Keep the smallest version of each component, remove oversized ones
            // This handles both duplicates and incorrectly sized originals

            // Find all RPGStatusBar components
            List<Transform> statusBars = new List<Transform>();
            foreach (Transform child in canvasInstance.transform)
            {
                if (child.name.Contains("RPGStatusBar"))
                {
                    statusBars.Add(child);
                }
            }

            // If multiple status bars, keep the one with scale closest to 0.25 (correct size)
            if (statusBars.Count > 1)
            {
                Debug.Log($"[UIIntegrator] Found {statusBars.Count} status bars, keeping correctly sized one");
                Transform bestStatusBar = null;
                float targetScale = 0.25f;
                float closestDiff = float.MaxValue;

                foreach (Transform sb in statusBars)
                {
                    float scaleDiff = Mathf.Abs(sb.localScale.x - targetScale);
                    if (scaleDiff < closestDiff)
                    {
                        closestDiff = scaleDiff;
                        bestStatusBar = sb;
                    }
                }

                // Mark all others for removal
                foreach (Transform sb in statusBars)
                {
                    if (sb != bestStatusBar)
                    {
                        toRemove.Add(sb);
                    }
                }
            }

            // Find all Minimap components
            List<Transform> minimaps = new List<Transform>();
            foreach (Transform child in canvasInstance.transform)
            {
                if (child.name.Contains("Minimap") && !child.name.Contains("Button"))
                {
                    minimaps.Add(child);
                }
            }

            // If multiple minimaps, keep the one with scale closest to 0.2 (correct size)
            if (minimaps.Count > 1)
            {
                Debug.Log($"[UIIntegrator] Found {minimaps.Count} minimaps, keeping correctly sized one");
                Transform bestMinimap = null;
                float targetScale = 0.2f;
                float closestDiff = float.MaxValue;

                foreach (Transform mm in minimaps)
                {
                    float scaleDiff = Mathf.Abs(mm.localScale.x - targetScale);
                    if (scaleDiff < closestDiff)
                    {
                        closestDiff = scaleDiff;
                        bestMinimap = mm;
                    }
                }

                // Mark all others for removal
                foreach (Transform mm in minimaps)
                {
                    if (mm != bestMinimap)
                    {
                        toRemove.Add(mm);
                    }
                }
            }

            // Remove marked components
            foreach (Transform t in toRemove)
            {
                Debug.Log($"[UIIntegrator] Removing duplicate: {t.name} (scale: {t.localScale.x})");
                DestroyImmediate(t.gameObject);
                removedCount++;
            }

            // Save changes
            string prefabPath = AssetDatabase.GetAssetPath(canvasPrefab);
            PrefabUtility.SaveAsPrefabAsset(canvasInstance, prefabPath);
            DestroyImmediate(canvasInstance);

            string message = removedCount > 0
                ? $"Removed {removedCount} duplicate component(s)!\n\nKept the correctly sized versions."
                : "No duplicates found. Canvas is clean!";

            Debug.Log($"[UIIntegrator] ✅ Cleanup complete: {removedCount} components removed");
            EditorUtility.DisplayDialog("Cleanup Complete", message, "OK");

            integrationComplete = true;
        }
    }
}
