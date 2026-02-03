using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Synthesis.Bridge;

namespace Synthesis.Editor
{
    /// <summary>
    /// Applies changes from UIChangeLog to scene objects and prefabs
    /// </summary>
    [InitializeOnLoad]
    public static class UIChangeApplicator
    {
        private static UIChangeLog changeLog;

        static UIChangeApplicator()
        {
            EditorApplication.playModeStateChanged += OnPlayModeStateChanged;
        }

        private static void OnPlayModeStateChanged(PlayModeStateChange state)
        {
            // Apply changes when exiting Play mode
            if (state == PlayModeStateChange.EnteredEditMode)
            {
                ApplyChanges();
            }
        }

        [MenuItem("Synthesis/Apply Recorded Changes")]
        public static void ApplyChanges()
        {
            // Find the UIChangeLog asset
            string[] guids = AssetDatabase.FindAssets("t:UIChangeLog");
            if (guids.Length == 0)
            {
                Debug.LogWarning("[UIChangeApplicator] No UIChangeLog asset found. Create one at Assets > Create > Synthesis > UI Change Log");
                return;
            }

            string path = AssetDatabase.GUIDToAssetPath(guids[0]);
            changeLog = AssetDatabase.LoadAssetAtPath<UIChangeLog>(path);

            if (changeLog == null || changeLog.changes.Count == 0)
            {
                Debug.Log("[UIChangeApplicator] No changes to apply.");
                return;
            }

            if (!changeLog.autoApplyOnExitPlayMode)
            {
                Debug.Log("[UIChangeApplicator] Auto-apply is disabled. Enable it in the UIChangeLog asset.");
                return;
            }

            Debug.Log($"[UIChangeApplicator] Applying {changeLog.changes.Count} changes...");

            int appliedCount = 0;
            foreach (var change in changeLog.changes)
            {
                if (ApplyChange(change))
                    appliedCount++;
            }

            Debug.Log($"[UIChangeApplicator] Applied {appliedCount}/{changeLog.changes.Count} changes.");

            if (changeLog.clearAfterApply)
            {
                changeLog.Clear();
            }

            // Save all changes
            AssetDatabase.SaveAssets();
            EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
        }

        private static bool ApplyChange(UIChangeLog.UIChange change)
        {
            // Find object in scene by path
            GameObject obj = FindObjectByPath(change.objectPath);
            if (obj == null)
            {
                Debug.LogWarning($"[UIChangeApplicator] Object not found: {change.objectPath}");
                return false;
            }

            try
            {
                // Handle position/transform changes
                if (change.changeType == UIChangeLog.ChangeType.Position)
                {
                    Undo.RecordObject(obj.transform, "Apply Position Change");
                    obj.transform.position = change.vector3Value;
                    Debug.Log($"[UIChangeApplicator] ✅ Set {change.objectPath} position to {change.vector3Value}");
                    return true;
                }

                if (change.changeType == UIChangeLog.ChangeType.Scale)
                {
                    Undo.RecordObject(obj.transform, "Apply Scale Change");
                    obj.transform.localScale = change.vector3Value;
                    Debug.Log($"[UIChangeApplicator] ✅ Set {change.objectPath} scale to {change.vector3Value}");
                    return true;
                }

                // Handle component changes
                if (!string.IsNullOrEmpty(change.componentType))
                {
                    Component comp = obj.GetComponent(change.componentType);
                    if (comp == null)
                    {
                        Debug.LogWarning($"[UIChangeApplicator] Component not found: {change.componentType} on {change.objectPath}");
                        return false;
                    }

                    Undo.RecordObject(comp, "Apply Component Change");

                    // Use reflection to set value
                    var field = comp.GetType().GetField(change.fieldName,
                        System.Reflection.BindingFlags.Public |
                        System.Reflection.BindingFlags.NonPublic |
                        System.Reflection.BindingFlags.Instance);

                    if (field != null)
                    {
                        object value = GetChangeValue(change);
                        field.SetValue(comp, value);
                        EditorUtility.SetDirty(comp);
                        Debug.Log($"[UIChangeApplicator] ✅ Set {change.objectPath}.{change.componentType}.{change.fieldName} = {value}");
                        return true;
                    }

                    // Try property
                    var property = comp.GetType().GetProperty(change.fieldName);
                    if (property != null && property.CanWrite)
                    {
                        object value = GetChangeValue(change);
                        property.SetValue(comp, value);
                        EditorUtility.SetDirty(comp);
                        Debug.Log($"[UIChangeApplicator] ✅ Set {change.objectPath}.{change.componentType}.{change.fieldName} = {value}");
                        return true;
                    }

                    Debug.LogWarning($"[UIChangeApplicator] Field/Property not found: {change.fieldName} on {change.componentType}");
                    return false;
                }
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"[UIChangeApplicator] Error applying change: {ex.Message}");
                return false;
            }

            return false;
        }

        private static GameObject FindObjectByPath(string path)
        {
            // Simple implementation - find by name first
            // TODO: Implement proper hierarchy path search
            string[] parts = path.Split('/');
            string objectName = parts[parts.Length - 1];

            GameObject[] allObjects = GameObject.FindObjectsByType<GameObject>(FindObjectsInactive.Include, FindObjectsSortMode.None);
            foreach (var obj in allObjects)
            {
                if (obj.name == objectName)
                {
                    // Verify full path matches
                    if (GetGameObjectPath(obj) == path)
                        return obj;
                }
            }

            return null;
        }

        private static string GetGameObjectPath(GameObject obj)
        {
            string path = obj.name;
            Transform current = obj.transform.parent;
            while (current != null)
            {
                path = current.name + "/" + path;
                current = current.parent;
            }
            return path;
        }

        private static object GetChangeValue(UIChangeLog.UIChange change)
        {
            switch (change.changeType)
            {
                case UIChangeLog.ChangeType.String: return change.stringValue;
                case UIChangeLog.ChangeType.Float: return change.floatValue;
                case UIChangeLog.ChangeType.Bool: return change.boolValue;
                case UIChangeLog.ChangeType.Vector3: return change.vector3Value;
                case UIChangeLog.ChangeType.Vector2: return change.vector2Value;
                case UIChangeLog.ChangeType.Color: return change.colorValue;
                default: return null;
            }
        }
    }
}
