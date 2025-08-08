# 📘 Assumption Object Definition (v1)

This document describes the structure of an `Assumption` object used in Chain of Thought systems.

## ✅ Schema Fields

| Field         | Type          | Required | Description                                                                 |
|---------------|---------------|----------|-----------------------------------------------------------------------------|
| `id`          | `string`      | ❌       | Optional unique identifier (UUID, hash, etc.)                               |
| `type`        | `string`      | ✅       | Always `"Assumption"` — used to distinguish from other reasoning types      |
| `statement`   | `string`      | ✅       | The content of the assumption                                               |
| `scope`       | `string`      | ❌       | Logical or contextual scope where assumption is valid                       |
| `tags`        | `List[string]`| ❌       | Optional topic tags                                                         |

## 🧪 Example

```json
{
  "type": "Assumption",
  "statement": "The system has access to an uninterrupted power supply.",
  "scope": "During test conditions in lab environment",
  "tags": ["infrastructure", "environment"]
}
```