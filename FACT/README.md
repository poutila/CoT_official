# 🧠 README: Usage of `Fact` Object in Chain of Thought Systems

## 📘 What is a `Fact`?

A `Fact` is a verifiable, objective statement used as a trustworthy building block in AI reasoning processes.

It must:
- ✅ Be **verifiable**: Confirmable through empirical evidence or documentation.
- ✅ Be **objective**: Not based on personal belief or interpretation.

---

## 🔹 Use Cases in Chain of Thought (CoT) Systems

| Use Case                  | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| 🧱 Reasoning Block         | Used as a unit in step-by-step logical inference chains.                    |
| 🔍 Validation              | Compare claims or predictions against known facts using semantic similarity.|
| ❌ Contradiction Detection| Flag logical inconsistencies in reasoning chains.                           |
| 📊 Grounding              | Serve as evidence to justify AI decisions or statements.                    |
| 🗃️ Knowledge Graph        | Stored as nodes in structured semantic knowledge representations.           |

---

## ✅ Code Examples

### 1. Use in Reasoning Chains

```python
if fact.is_fact():
    reasoning_chain.append(fact.statement)
```

### 2. Semantic Similarity Validation

```python
claim = "Water usually boils at 100 degrees."
if validate_against_fact(claim, fact):
    print("Claim is consistent with known fact.")
else:
    print("Claim deviates from verified fact.")
```

### 3. Building Vector Indexes

Facts can be embedded and indexed for fast semantic retrieval:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
embedding = model.encode(fact.statement)
```

---

## 🔗 Integration in AI Pipelines

- **Input**: Use known facts to provide context to LLMs.
- **Intermediate**: Filter or refine decisions with validated facts.
- **Output**: Validate or reject AI-generated output using fact consistency.

---

## 📦 Suggestion

Store facts as `.json` or `.jsonl` using the defined schema to enable structured validation, loading, and semantic querying.