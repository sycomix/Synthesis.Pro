using System;
using System.Collections.Generic;
using UnityEngine;

namespace Synthesis.Bridge
{
    /// <summary>
    /// ScriptableObject that persists UI changes made at runtime
    /// </summary>
    [CreateAssetMenu(fileName = "UIChangeLog", menuName = "Synthesis/UI Change Log")]
    public class UIChangeLog : ScriptableObject
    {
        [System.Serializable]
        public class UIChange
        {
            public string objectPath; // Hierarchy path to object (e.g., "Canvas/HealthBar")
            public string componentType;
            public string fieldName;
            public ChangeType changeType;
            public string stringValue;
            public float floatValue;
            public bool boolValue;
            public Vector3 vector3Value;
            public Vector2 vector2Value;
            public Color colorValue;
            public string timestamp;
        }

        public enum ChangeType
        {
            String,
            Float,
            Bool,
            Vector3,
            Vector2,
            Color,
            Position,
            Scale,
            Rotation
        }

        [Header("Change Log")]
        public List<UIChange> changes = new List<UIChange>();

        [Header("Settings")]
        public bool autoApplyOnExitPlayMode = true;
        public bool clearAfterApply = true;

        /// <summary>
        /// Records a change to be applied later.
        /// </summary>
        public void RecordChange(UIChange change)
        {
            change.timestamp = System.DateTime.Now.ToString("HH:mm:ss");
            changes.Add(change);
            
            #if UNITY_EDITOR
            // Force save the ScriptableObject
            UnityEditor.EditorUtility.SetDirty(this);
            UnityEditor.AssetDatabase.SaveAssets();
            #endif
            
            Debug.Log($"[UIChangeLog] Recorded: {change.objectPath}.{change.fieldName} = {GetValueString(change)}");
        }

        /// <summary>
        /// Records a position change.
        /// </summary>
        public void RecordPositionChange(string objectPath, Vector3 position)
        {
            RecordChange(new UIChange
            {
                objectPath = objectPath,
                changeType = ChangeType.Position,
                vector3Value = position
            });
        }

        /// <summary>
        /// Records a component field/property change.
        /// </summary>
        public void RecordComponentChange(string objectPath, string componentType, string fieldName, object value)
        {
            UIChange change = new UIChange
            {
                objectPath = objectPath,
                componentType = componentType,
                fieldName = fieldName
            };

            // Determine type and store value
            if (value is string s)
            {
                change.changeType = ChangeType.String;
                change.stringValue = s;
            }
            else if (value is float f)
            {
                change.changeType = ChangeType.Float;
                change.floatValue = f;
            }
            else if (value is int i)
            {
                change.changeType = ChangeType.Float;
                change.floatValue = i;
            }
            else if (value is bool b)
            {
                change.changeType = ChangeType.Bool;
                change.boolValue = b;
            }
            else if (value is Vector3 v3)
            {
                change.changeType = ChangeType.Vector3;
                change.vector3Value = v3;
            }
            else if (value is Vector2 v2)
            {
                change.changeType = ChangeType.Vector2;
                change.vector2Value = v2;
            }
            else if (value is Color c)
            {
                change.changeType = ChangeType.Color;
                change.colorValue = c;
            }

            RecordChange(change);
        }

        /// <summary>
        /// Clears all recorded changes.
        /// </summary>
        public void Clear()
        {
            changes.Clear();
            
            #if UNITY_EDITOR
            UnityEditor.EditorUtility.SetDirty(this);
            UnityEditor.AssetDatabase.SaveAssets();
            #endif
            
            Debug.Log("[UIChangeLog] Cleared all changes");
        }

        private string GetValueString(UIChange change)
        {
            switch (change.changeType)
            {
                case ChangeType.String: return change.stringValue;
                case ChangeType.Float: return change.floatValue.ToString();
                case ChangeType.Bool: return change.boolValue.ToString();
                case ChangeType.Vector3:
                case ChangeType.Position: return change.vector3Value.ToString();
                case ChangeType.Vector2: return change.vector2Value.ToString();
                case ChangeType.Color: return change.colorValue.ToString();
                default: return "Unknown";
            }
        }
    }
}
