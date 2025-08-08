# 📘 Fact Object Definition (v2)

This document describes the structure of a `Fact` object used in Chain of Thought systems.

## ✅ Schema Fields

| Field           | Type          | Required | Description                                                                               |
| -------------- | ------------- | -------- | ------------------------------------------------------------------------------------------ |
| `id`           | `string`      | ❌       | Optional unique identifier (UUID, hash, etc.)                                              |
| `type`         | `string`      | ✅       | Always `"Fact"` — used to distinguish from other reasoning types (e.g., Claim, Hypothesis) |
| `statement`    | `string`      | ✅       | Plain-language factual statement                                                           |
| `is_verifiable`| `boolean`     | ✅       | Can the fact be verified with evidence or experimentation?                                 |
| `is_objective` | `boolean`     | ✅       | Is the fact independent of opinion or belief?                                              |
| `source`       | `string`      | ❌       | Optional source or reference for validation (e.g., document, URL, org)                     |
| `context`      | `string`      | ❌       | Optional condition or scope where the fact holds (e.g., "at sea level")                    |
| `tags`         | `List[string]`| ❌       | Optional topic tags (e.g., physics, history)                                               |


## 🧪 Example

```json
{
  "type": "Fact",
  "statement": "Water boils at 100°C at sea level.",
  "is_verifiable": true,
  "is_objective": true,
  "source": "Chemistry Handbook",
  "context": "Standard atmospheric pressure",
  "tags": ["chemistry", "boiling point"]
}
```
