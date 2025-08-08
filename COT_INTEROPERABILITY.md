# Chain-of-Thought Interoperability Guide

## Overview

This guide provides mappings and adapters for using Chain-of-Thought (CoT) reasoning with popular AI frameworks and standards.

## Version Support

### Multi-Version Configuration

All adapters MUST support version selection to ensure compatibility:

```python
# Version selector configuration
COT_VERSION_CONFIG = {
    "default": "7.0.0",
    "supported": ["7.0.0", "6.0.0", "5.0.0"],
    "minimum": "5.0.0",
    "validator_mapping": {
        "7.0.0": "cot-validator>=2.0.0",
        "6.0.0": "cot-validator>=1.2.0,<2.0.0",
        "5.0.0": "cot-validator>=1.1.0,<1.2.0"
    }
}

def get_cot_version(requested_version=None):
    """Get appropriate CoT version with validation."""
    version = requested_version or COT_VERSION_CONFIG["default"]
    if version not in COT_VERSION_CONFIG["supported"]:
        raise ValueError(f"Unsupported CoT version: {version}. Supported: {COT_VERSION_CONFIG['supported']}")
    return version
```

## LangChain Integration

### CoT as a LangChain Tool

```python
from langchain.tools import Tool
from langchain.agents import AgentExecutor
from cot_validator import ChainOfThoughtReasoner

class CoTReasoningTool(Tool):
    name = "chain_of_thought_reasoning"
    description = "Apply structured CoT reasoning to complex decisions"
    
    def __init__(self, version=None):
        self.version = get_cot_version(version)
        self.reasoner = ChainOfThoughtReasoner(version=self.version)
    
    def _run(self, task: str, context: dict = None) -> str:
        # Generate CoT reasoning trace
        trace = self.reasoner.reason(
            decision=task,
            context=context,
            risk_level="auto",
            context_level="full_file_access"
        )
        
        # Validate output
        if not self.reasoner.validate(trace):
            return self._handle_failure(trace)
            
        return trace.to_markdown()
    
    def _handle_failure(self, trace):
        return f"DEFERRED: {trace.failure_reason}"

# Usage in LangChain
cot_tool = CoTReasoningTool(version="7.0.0")  # Or None for default
agent = AgentExecutor.from_tools([cot_tool, ...])
```

### CoT Chain Example

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

cot_prompt = PromptTemplate(
    input_variables=["task", "context"],
    template="""
---
cot_contract:
  version: 1.0.0
  mode: strict
  context: {context_level}
---

Apply Chain-of-Thought reasoning to: {task}
Context: {context}

Generate reasoning following CoT v{version} specification.
"""
)

cot_chain = LLMChain(
    llm=llm,
    prompt=cot_prompt,
    output_parser=CoTOutputParser()
)
```

## OpenAI Function Calling

### CoT as an OpenAI Function

```python
cot_function = {
    "name": "apply_chain_of_thought_reasoning",
    "description": "Apply structured reasoning following CoT standard",
    "parameters": {
        "version": {"type": "string", "default": "7.0.0", "enum": ["7.0.0", "6.0.0", "5.0.0"]},
    "parameters": {
        "type": "object",
        "properties": {
            "decision": {
                "type": "string",
                "description": "The decision or action to reason about"
            },
            "risk_assessment": {
                "type": "object",
                "properties": {
                    "change_type": {"type": "string"},
                    "risk_level": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"]
                    },
                    "impact_scope": {"type": "string"},
                    "reversibility": {"type": "string"}
                }
            },
            "evidence_collection": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "quote": {"type": "string"},
                        "relevance": {"type": "string"},
                        "freshness": {"type": "string"}
                    }
                }
            },
            "context_level": {
                "type": "string",
                "enum": ["full_file_access", "summary_only", "chat_context", "mixed", "undefined"]
            }
        },
        "required": ["decision", "risk_assessment", "evidence_collection", "context_level"]
    }
}

# Usage
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": f"You are a CoT v{version} compliant reasoning system."},
        {"role": "user", "content": "Should we refactor the authentication module?"}
    ],
    functions=[cot_function],
    function_call={"name": "apply_chain_of_thought_reasoning"}
)
```

### Response Parser

```python
def parse_cot_function_response(response):
    """Convert OpenAI function response to CoT format."""
    args = response["choices"][0]["message"]["function_call"]["arguments"]
    cot_data = json.loads(args)
    
    # Convert to CoT markdown format
    markdown = f"""## 🧠 Reasoning Trace (Chain-of-Thought)

```yaml
schema: chain_of_thought/v{version}
validation: required
```

**Context Level**: {cot_data['context_level']}

### Decision: {cot_data['decision']}

#### Risk Assessment:
- **Change Type**: {cot_data['risk_assessment']['change_type']}
- **Risk Level**: {cot_data['risk_assessment']['risk_level']}
- **Impact Scope**: {cot_data['risk_assessment']['impact_scope']}
- **Reversibility**: {cot_data['risk_assessment']['reversibility']}

#### Evidence Collection:
"""
    
    for i, evidence in enumerate(cot_data['evidence_collection'], 1):
        markdown += f"""
{i}. **Source**: `{evidence['source']}`
   **Quote**: "{evidence['quote']}"
   **Relevance**: {evidence['relevance']}
   **Freshness**: {evidence['freshness']}
"""
    
    return markdown
```

## JSON-RPC Format

### CoT over JSON-RPC

```json
{
  "jsonrpc": "2.0",
  "method": "cot.reason",
  "params": {
    "contract": {
      "version": "1.0.0",
      "mode": "strict",
      "context": "full_file_access"
    },
    "task": {
      "decision": "Remove deprecated API endpoints",
      "context": {
        "files": ["api/v1/users.py", "api/v1/auth.py"],
        "constraints": ["maintain backward compatibility"]
      }
    },
    "options": {
      "include_token_metrics": true,
      "max_reasoning_chains": 5
    }
  },
  "id": "cot-req-001"
}
```

### JSON-RPC Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "reasoning_trace": {
      "schema": f"chain_of_thought/v{version}",
      "context_level": "full_file_access",
      "decision": "DEFERRED - Need usage metrics",
      "risk_assessment": {
        "risk_level": "high",
        "impact_scope": "system-wide"
      },
      "evidence_collection": [...],
      "validation": {
        "passed": true,
        "warnings": []
      },
      "metrics": {
        "token_usage": 1847,
        "reasoning_chains": 3,
        "evidence_sources": 4
      }
    }
  },
  "id": "cot-req-001"
}
```

## AutoGPT/Agent Protocol

### CoT as Agent Protocol Action

```yaml
# agent-protocol.yaml
actions:
  - name: chain_of_thought_reasoning
    description: Apply CoT reasoning to decisions (supports v5.0.0-v7.0.0)
    input_schema:
      $ref: "https://cot-standard.org/schemas/input/${version}.json"
    output_schema:
      $ref: "https://cot-standard.org/schemas/output/${version}.json"
    constraints:
      max_tokens: 2500
      timeout_seconds: 60
    capabilities:
      - file_access
      - tool_use
      - memory_access
```

## Semantic Kernel Integration

### CoT Skill for Semantic Kernel

```csharp
public class ChainOfThoughtSkill
{
    [SKFunction("Apply Chain-of-Thought reasoning")]
    [SKFunctionInput(Description = "The decision to reason about")]
    public async Task<string> ReasonAsync(
        string decision,
        SKContext context)
    {
        var cotRequest = new CotRequest
        {
            Decision = decision,
            ContextLevel = DetermineContextLevel(context),
            RiskLevel = "auto",
            Contract = new CotContract
            {
                Version = GetCotVersion(requestedVersion),
                Mode = "strict"
            }
        };
        
        var reasoning = await _cotService.GenerateReasoningAsync(cotRequest);
        
        if (!reasoning.IsValid)
        {
            return HandleInvalidReasoning(reasoning);
        }
        
        return reasoning.ToMarkdown();
    }
}
```

## Hugging Face Transformers

### CoT Generation Pipeline

```python
from transformers import pipeline
from cot_validator import CoTValidator

class CoTGenerationPipeline:
    def __init__(self, model_name="cot-standard/cot-reasoner-v6"):
        self.generator = pipeline(
            "text-generation",
            model=model_name,
            device=0
        )
        self.validator = CoTValidator(version=get_cot_version(version))
        
    def reason(self, task, context=None, **kwargs):
        prompt = self._build_cot_prompt(task, context)
        
        # Generate with constraints
        output = self.generator(
            prompt,
            max_new_tokens=2500,
            temperature=0.7,
            do_sample=True,
            **kwargs
        )
        
        # Extract and validate reasoning
        reasoning = self._extract_reasoning(output[0]['generated_text'])
        validation = self.validator.validate(reasoning)
        
        if not validation.is_valid:
            return self._handle_invalid(validation)
            
        return reasoning
```

## REST API Schema

This section describes the schema for both JSON-RPC and REST endpoints for CoT reasoning services.

### REST Endpoints and Schema Definition

```yaml
openapi: 3.0.0
info:
  title: Chain-of-Thought Reasoning API
  version: 1.0.0
  description: REST API for CoT v5.0.0-v7.0.0 reasoning

paths:
  /api/v1/reason:
    post:
      summary: Generate CoT reasoning trace
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                decision:
                  type: string
                  description: The decision or action to reason about
                context:
                  type: object
                  description: Context information for reasoning
                risk_level:
                  type: string
                  enum: [auto, low, medium, high, critical]
                  default: auto
                context_level:
                  type: string
                  enum: [full_file_access, summary_only, chat_context, mixed, undefined]
                  default: undefined
                version:
                  type: string
                  enum: ["7.0.0", "6.0.0", "5.0.0"]
                  default: "7.0.0"
              required: [decision]
      responses:
        200:
          description: Successful reasoning generation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ReasoningResponse'
        400:
          description: Invalid request or validation failure
        
  /api/v1/validate:
    post:
      summary: Validate a CoT reasoning trace
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                trace:
                  type: string
                  description: The reasoning trace to validate
                version:
                  type: string
                  description: CoT version to validate against
      responses:
        200:
          description: Validation result
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ValidationResponse'

components:
  schemas:
    ReasoningResponse:
      type: object
      properties:
        reasoning_trace:
          type: string
          description: Generated CoT reasoning in markdown format
        validation:
          type: object
          properties:
            valid:
              type: boolean
            errors:
              type: array
              items:
                type: string
            warnings:
              type: array
              items:
                type: string
        metrics:
          type: object
          properties:
            token_count:
              type: integer
            evidence_count:
              type: integer
            reasoning_depth:
              type: integer
        
    ValidationResponse:
      type: object
      properties:
        valid:
          type: boolean
        version:
          type: string
        errors:
          type: array
          items:
            type: string
        warnings:
          type: array
          items:
            type: string
```

### JSON-RPC Schema Definition

```typescript
// JSON-RPC 2.0 Method Definitions
interface CoTMethods {
  // Generate reasoning trace
  "cot.reason": {
    params: {
      contract: {
        version: "1.0.0" | "2.0.0";
        mode: "strict" | "lenient";
        context: string;
      };
      task: {
        decision: string;
        context?: Record<string, any>;
        constraints?: string[];
      };
      options?: {
        include_token_metrics?: boolean;
        max_reasoning_chains?: number;
        cot_version?: string;
      };
    };
    result: {
      reasoning_trace: ReasoningTrace;
      metrics?: ReasoningMetrics;
    };
  };
  
  // Validate existing trace
  "cot.validate": {
    params: {
      trace: string;
      version?: string;
      strict?: boolean;
    };
    result: {
      valid: boolean;
      errors: string[];
      warnings: string[];
    };
  };
  
  // Get version info
  "cot.version": {
    params: {};
    result: {
      current: string;
      supported: string[];
      latest: string;
    };
  };
}

// Type definitions
interface ReasoningTrace {
  schema: string;
  context_level: ContextLevel;
  decision: string;
  risk_assessment: RiskAssessment;
  evidence_collection: Evidence[];
  analysis: string;
  validation: ValidationStep[];
  action: string;
}

interface ReasoningMetrics {
  token_usage: number;
  reasoning_chains: number;
  evidence_sources: number;
  processing_time_ms: number;
}
```

### Schema Example Block

```json
{
  "$schema": "https://cot-standard.org/schemas/api/v1.0.0.json",
  "api_version": "1.0.0",
  "endpoints": {
    "rest": {
      "base_url": "https://api.cot-standard.org",
      "paths": {
        "/v1/reason": {
          "method": "POST",
          "request_schema": {
            "type": "object",
            "properties": {
              "decision": {"type": "string"},
              "context": {"type": "object"},
              "risk_level": {"type": "string", "enum": ["auto", "low", "medium", "high", "critical"]},
              "context_level": {"type": "string"},
              "version": {"type": "string"}
            },
            "required": ["decision"]
          }
        }
      }
    },
    "json_rpc": {
      "endpoint": "https://api.cot-standard.org/jsonrpc",
      "methods": {
        "cot.reason": {
          "params_schema": {
            "contract": {"type": "object"},
            "task": {"type": "object"},
            "options": {"type": "object"}
          }
        },
        "cot.validate": {
          "params_schema": {
            "trace": {"type": "string"},
            "version": {"type": "string"}
          }
        }
      }
    }
  }
}
```

### Concrete REST/JSON-RPC Examples

#### REST API Example Request/Response

```bash
# REST API Request Example
curl -X POST https://api.cot-standard.org/v1/reason \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "Should we refactor the authentication module?",
    "context": {
      "module_stats": {
        "lines_of_code": 2500,
        "cyclomatic_complexity": 45,
        "test_coverage": 65
      },
      "constraints": ["maintain backward compatibility", "zero downtime"]
    },
    "risk_level": "auto",
    "context_level": "full_file_access",
    "version": "7.0.0"
  }'

# REST API Response Example
{
  "reasoning_trace": "## 🧠 Reasoning Trace (Chain-of-Thought)\n\n```yaml\nschema: chain_of_thought/v7.0.0\nvalidation: required\n```\n\n### Decision: Should we refactor the authentication module?\n\n#### Risk Assessment:\n- **Risk Level**: High\n- **Change Type**: Structural refactoring\n- **Impact Scope**: System-wide (all authenticated endpoints)\n- **Reversibility**: Moderate (can rollback but may impact sessions)\n\n#### Evidence Collection:\n1. **Source**: `module_stats`\n   **Quote**: \"cyclomatic_complexity: 45\"\n   **Relevance**: Exceeds recommended threshold of 10\n   **Freshness**: Current\n\n#### Analysis:\nThe authentication module shows signs of technical debt...\n\n#### Action:\nPROCEED with phased refactoring approach...",
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": ["Consider increasing test coverage before refactoring"]
  },
  "metrics": {
    "token_count": 1247,
    "evidence_count": 3,
    "reasoning_depth": 2
  }
}
```

#### JSON-RPC Example Request/Response

```bash
# JSON-RPC Request Example
curl -X POST https://api.cot-standard.org/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "cot.reason",
    "params": {
      "contract": {
        "version": "2.0.0",
        "mode": "strict",
        "context": "full_file_access"
      },
      "task": {
        "decision": "Delete deprecated API endpoints",
        "context": {
          "endpoints": ["/api/v1/legacy/users", "/api/v1/legacy/auth"],
          "usage_last_30_days": 0,
          "deprecation_date": "2023-06-01"
        },
        "constraints": ["notify remaining users", "update documentation"]
      },
      "options": {
        "include_token_metrics": true,
        "max_reasoning_chains": 3,
        "cot_version": "7.0.0"
      }
    },
    "id": "cot-req-12345"
  }'

# JSON-RPC Response Example
{
  "jsonrpc": "2.0",
  "result": {
    "reasoning_trace": {
      "schema": "chain_of_thought/v7.0.0",
      "context_level": "full_file_access",
      "decision": "PROCEED - Safe to delete endpoints",
      "risk_assessment": {
        "risk_level": "low",
        "change_type": "removal",
        "impact_scope": "limited",
        "reversibility": "high"
      },
      "evidence_collection": [
        {
          "source": "usage_metrics",
          "quote": "usage_last_30_days: 0",
          "relevance": "No active usage indicates safe removal",
          "freshness": "current",
          "freshness_score": 1.0
        }
      ],
      "analysis": "Zero usage in 30 days confirms deprecation success...",
      "validation": {
        "passed": true,
        "checks": ["evidence_minimum", "risk_appropriate", "decision_clear"]
      },
      "action": "1. Delete endpoints\n2. Update API docs\n3. Notify users via changelog"
    },
    "metrics": {
      "token_usage": 892,
      "reasoning_chains": 2,
      "evidence_sources": 3,
      "processing_time_ms": 1247
    }
  },
  "id": "cot-req-12345"
}
```

## REST API Wrapper

### Universal CoT REST API

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="CoT Reasoning API")

class CoTRequest(BaseModel):
    decision: str
    context: dict = {}
    risk_level: str = "auto"
    context_level: str = "undefined"
    options: dict = {}

class CoTResponse(BaseModel):
    reasoning_trace: str
    validation: dict
    metrics: dict
    escalation: dict = None

@app.post("/v1/reason", response_model=CoTResponse)
async def apply_reasoning(request: CoTRequest):
    """Apply CoT reasoning to a decision."""
    try:
        # Generate reasoning
        trace = await generate_cot_reasoning(
            request.decision,
            request.context,
            request.risk_level,
            request.context_level
        )
        
        # Validate
        validation = validate_reasoning(trace)
        
        if not validation['valid']:
            raise HTTPException(400, detail=validation['errors'])
            
        return CoTResponse(
            reasoning_trace=trace,
            validation=validation,
            metrics=extract_metrics(trace)
        )
        
    except DeferralRequired as e:
        return CoTResponse(
            reasoning_trace=e.partial_trace,
            validation={"valid": False, "deferred": True},
            metrics=e.metrics,
            escalation=e.escalation_info
        )
```

## GraphQL Schema

### CoT as GraphQL Types

```graphql
type ChainOfThoughtReasoning {
  id: ID!
  schema: String!
  contextLevel: ContextLevel!
  decision: String!
  riskAssessment: RiskAssessment!
  evidenceCollection: [Evidence!]!
  analysis: Analysis!
  validation: Validation!
  action: String!
  metrics: ReasoningMetrics
}

enum ContextLevel {
  FULL_FILE_ACCESS
  SUMMARY_ONLY
  CHAT_CONTEXT
  MIXED
  UNDEFINED
}

type RiskAssessment {
  changeType: String!
  riskLevel: RiskLevel!
  impactScope: String!
  reversibility: String!
}

enum RiskLevel {
  LOW
  MEDIUM
  HIGH
  CRITICAL
}

type Query {
  validateReasoning(trace: String!): ValidationResult!
  estimateComplexity(task: String!): ComplexityEstimate!
}

type Mutation {
  generateReasoning(
    decision: String!
    context: JSON
    options: ReasoningOptions
  ): ChainOfThoughtReasoning!
  
  escalateReasoning(
    deferralId: ID!
    level: Int!
  ): EscalationResult!
}
```

## Migration Patterns

### From Free-Form to CoT

```python
def migrate_to_cot(legacy_reasoning: str) -> str:
    """Convert legacy reasoning to CoT format."""
    
    # Extract components using NLP/regex
    decision = extract_decision(legacy_reasoning)
    evidence = extract_evidence_mentions(legacy_reasoning)
    
    # Build CoT structure
    cot_trace = {
        "schema": f"chain_of_thought/v{version}",
        "context_level": "undefined",  # Conservative default
        "decision": decision,
        "risk_assessment": {
            "risk_level": "high",  # Conservative default
            "change_type": "unknown",
            "impact_scope": "unknown",
            "reversibility": "unknown"
        },
        "evidence_collection": [
            {
                "source": "legacy reasoning",
                "quote": evidence,
                "relevance": "extracted from unstructured text",
                "context": "migration from legacy format"
            }
        ]
    }
    
    return format_as_markdown(cot_trace)
```

## Compatibility Matrix

| Framework | Integration Type | Complexity | Validated |
|-----------|-----------------|------------|-----------|
| LangChain | Native Tool/Chain | Low | ✅ |
| OpenAI Functions | Function Schema | Low | ✅ |
| JSON-RPC | Protocol Wrapper | Low | ✅ |
| AutoGPT | Agent Action | Medium | ✅ |
| Semantic Kernel | Skill/Function | Medium | ✅ |
| HuggingFace | Pipeline | Medium | ✅ |
| REST API | HTTP Wrapper | Low | ✅ |
| GraphQL | Schema Types | Medium | ✅ |
| LlamaIndex | Custom Tool | Medium | 🔄 |
| Vertex AI | Request Processor | Medium | 🔄 |

Legend: ✅ Validated | 🔄 In Progress | ❌ Not Started

## Endpoint Contract Examples

### REST API Contract

```yaml
# REST API Endpoint Contract
openapi: 3.0.0
info:
  title: CoT Reasoning API Contract
  version: 1.0.0

paths:
  /api/v1/reason:
    post:
      operationId: generateReasoning
      summary: Generate CoT reasoning trace
      x-contract:
        input:
          required:
            - decision
          optional:
            - context
            - risk_level
            - context_level
            - version
        output:
          guaranteed:
            - reasoning_trace
            - validation.valid
          conditional:
            - metrics (if requested)
            - escalation (if deferred)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ReasonRequest'
      responses:
        200:
          description: Successful reasoning
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ReasonResponse'
        400:
          description: Invalid request
        500:
          description: Server error
```

### JSON-RPC Contract

```typescript
// JSON-RPC Method Contract
interface CoTJsonRpcContract {
  // Method: cot.reason
  "cot.reason": {
    // Input contract
    params: {
      required: {
        contract: {
          version: string;  // "1.0.0" | "2.0.0"
          mode: "strict" | "lenient";
        };
        task: {
          decision: string;
        };
      };
      optional: {
        task: {
          context?: Record<string, any>;
          constraints?: string[];
        };
        options?: {
          include_token_metrics?: boolean;
          max_reasoning_chains?: number;
          cot_version?: string;
        };
      };
    };
    
    // Output contract
    result: {
      guaranteed: {
        reasoning_trace: {
          schema: string;
          decision: string;
          risk_assessment: RiskAssessment;
          evidence_collection: Evidence[];
        };
      };
      optional: {
        metrics?: {
          token_usage: number;
          reasoning_chains: number;
          evidence_sources: number;
          processing_time_ms: number;
        };
      };
    };
    
    // Error contract
    error: {
      code: number;
      message: string;
      data?: {
        validation_errors?: string[];
        partial_trace?: string;
      };
    };
  };
}
```

### Contract Validation Example

```python
# Contract validation middleware
def validate_contract(request_data: dict, contract: dict) -> tuple[bool, list[str]]:
    """Validate request against contract."""
    errors = []
    
    # Check required fields
    for field in contract.get("required", []):
        if field not in request_data:
            errors.append(f"Missing required field: {field}")
    
    # Check field types
    for field, expected_type in contract.get("types", {}).items():
        if field in request_data:
            actual_type = type(request_data[field]).__name__
            if actual_type != expected_type:
                errors.append(f"Field {field} should be {expected_type}, got {actual_type}")
    
    return len(errors) == 0, errors

# Usage
contract = {
    "required": ["decision"],
    "types": {"decision": "str", "risk_level": "str"}
}

valid, errors = validate_contract({"decision": "refactor auth"}, contract)
```

## Best Practices

1. **Always validate** output regardless of framework
2. **Include contract metadata** in all requests
3. **Handle deferrals** gracefully with framework-specific patterns
4. **Monitor token usage** across all integrations
5. **Log reasoning traces** for audit and improvement
6. **Version your integrations** to match CoT specification versions

## Support

For framework-specific help:
- GitHub: https://github.com/cot-standard/integrations
- Discord: https://discord.gg/cot-standard
- Email: integrations@cot-standard.org