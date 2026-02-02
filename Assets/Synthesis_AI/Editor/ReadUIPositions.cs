using UnityEngine;
using UnityEditor;

namespace Synthesis.Editor
{
    public static class ReadUIPositions
    {
        [MenuItem("Synthesis/Debug/Read UI Positions")]
        public static void ReadPositions()
        {
            string canvasPath = "Assets/UI Project/CanvasGameplay.prefab";
            GameObject canvasPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(canvasPath);

            if (canvasPrefab == null)
            {
                Debug.LogError("Could not find CanvasGameplay prefab");
                return;
            }

            // Instantiate to read actual values
            GameObject instance = PrefabUtility.InstantiatePrefab(canvasPrefab) as GameObject;

            if (instance == null)
            {
                Debug.LogError("Could not instantiate prefab");
                return;
            }

            Debug.Log("=== Reading UI Component Positions ===");

            // Find RPGStatusBar
            Transform statusBar = instance.transform.Find("RPGStatusBar");
            if (statusBar != null)
            {
                RectTransform rect = statusBar.GetComponent<RectTransform>();
                if (rect != null)
                {
                    Debug.Log($"RPGStatusBar:");
                    Debug.Log($"  anchorMin: {rect.anchorMin}");
                    Debug.Log($"  anchorMax: {rect.anchorMax}");
                    Debug.Log($"  pivot: {rect.pivot}");
                    Debug.Log($"  anchoredPosition: {rect.anchoredPosition}");
                    Debug.Log($"  localScale: {rect.localScale}");
                    Debug.Log($"  sizeDelta: {rect.sizeDelta}");
                }
            }
            else
            {
                Debug.Log("RPGStatusBar not found");
            }

            // Find Minimap
            Transform minimap = instance.transform.Find("Minimap");
            if (minimap != null)
            {
                RectTransform rect = minimap.GetComponent<RectTransform>();
                if (rect != null)
                {
                    Debug.Log($"Minimap:");
                    Debug.Log($"  anchorMin: {rect.anchorMin}");
                    Debug.Log($"  anchorMax: {rect.anchorMax}");
                    Debug.Log($"  pivot: {rect.pivot}");
                    Debug.Log($"  anchoredPosition: {rect.anchoredPosition}");
                    Debug.Log($"  localScale: {rect.localScale}");
                    Debug.Log($"  sizeDelta: {rect.sizeDelta}");
                }
            }
            else
            {
                Debug.Log("Minimap not found");
            }

            // Cleanup
            Object.DestroyImmediate(instance);

            Debug.Log("=== Done ===");
        }
    }
}
