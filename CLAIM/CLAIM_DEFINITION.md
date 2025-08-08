# 📘 Claim Object Definition (v1)

This document describes the structure of a `Claim` object used in Chain of Thought systems.

## ✅ Schema Fields

| Field         | Type          | Required | Description                                                                 |
|---------------|---------------|----------|-----------------------------------------------------------------------------|
| `id`          | `string`      | ❌       | Optional unique identifier (UUID, hash, etc.)                               |
| `type`        | `string`      | ✅       | Always `"Claim"` — used to distinguish from other reasoning types           |
| `statement`   | `string`      | ✅       | The content of the claim                                                    |
| `confidence`  | `number`      | ❌       | Optional self-reported confidence score (0-1)                               |
| `source`      | `string`      | ❌       | Optional source or reference                                                |
| `context`     | `string`      | ❌       | Where or under what assumptions this claim holds                            |
| `tags`        | `List[string]`| ❌       | Optional topic tags (e.g., philosophy, policy)                              |

## 🧪 Example

```json
{
  "type": "Claim",
  "statement": "Humans will reach Mars by 2050.",
  "confidence": 0.8,
  "source": "Expert forecast 2023",
  "context": "Assuming continuous investment in space tech",
  "tags": ["space", "prediction"]
}
```