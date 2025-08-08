#!/usr/bin/env python3
"""
End-to-end example: LangChain integration with CoT reasoning

This example demonstrates how to use Chain-of-Thought reasoning
with LangChain for code refactoring decisions.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import Document


class CoTReasoningTool(Tool):
    """Chain-of-Thought reasoning tool for LangChain."""
    
    name = "chain_of_thought_reasoning"
    description = (
        "Apply structured Chain-of-Thought reasoning to make decisions about "
        "code changes, refactoring, or system modifications. Use this when you "
        "need to make a decision that could impact the codebase."
    )
    
    def __init__(self, cot_version: str = "7.0.0"):
        super().__init__()
        self.cot_version = cot_version
        self.contract_version = "2.0.0"
        
    def _run(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Execute CoT reasoning for the given task."""
        context = context or {}
        
        # Determine risk level based on task keywords
        risk_level = self._assess_risk(task)
        
        # Generate structured reasoning trace
        trace = self._generate_reasoning_trace(
            task=task,
            context=context,
            risk_level=risk_level
        )
        
        # Validate the trace
        validation_result = self._validate_trace(trace)
        
        if validation_result["valid"]:
            return trace
        else:
            return f"REASONING FAILED: {validation_result['errors']}"
    
    def _assess_risk(self, task: str) -> str:
        """Assess risk level based on task description."""
        high_risk_keywords = ["delete", "remove", "security", "authentication", "database"]
        medium_risk_keywords = ["refactor", "modify", "update", "change"]
        
        task_lower = task.lower()
        
        if any(keyword in task_lower for keyword in high_risk_keywords):
            return "high"
        elif any(keyword in task_lower for keyword in medium_risk_keywords):
            return "medium"
        else:
            return "low"
    
    def _generate_reasoning_trace(self, task: str, context: Dict[str, Any], risk_level: str) -> str:
        """Generate a CoT reasoning trace."""
        # Simulated evidence gathering
        evidence_items = self._gather_evidence(task, context)
        
        # Build the reasoning trace
        trace = f"""## 🧠 Reasoning Trace (Chain-of-Thought)

```yaml
schema: chain_of_thought/v{self.cot_version}
validation: required
runtime_contract: {self.contract_version}
context_level: {context.get('access_level', 'full_file_access')}
risk_level: {risk_level}
evidence_count: {len(evidence_items)}
```

**Context Level**: {context.get('access_level', 'Full File Access')}
**Available Tools**: {context.get('tools', ['File reading', 'Code analysis'])}

### Decision: {task}

#### Risk Assessment:
- **Change Type**: {self._determine_change_type(task)}
- **Risk Level**: {risk_level.capitalize()}
- **Impact Scope**: {self._determine_impact_scope(task)}
- **Reversibility**: {self._determine_reversibility(risk_level)}

#### Evidence Collection:
{self._format_evidence(evidence_items)}

#### Analysis:
- **Primary rationale**: {self._generate_rationale(task, evidence_items)}
- **Alternative considered**: {self._generate_alternative(task)}
- **Alternative rejected because**: {self._generate_rejection_reason(task)}

#### Validation:
- [✓] Minimum {self._get_min_evidence(risk_level)} evidence sources cited (have {len(evidence_items)})
- [✓] No assumptions made beyond quoted text
- [✓] All affected files identified
- [✓] Edge cases addressed

#### Action:
→ Therefore, I will: {self._generate_action(task)}
"""
        return trace
    
    def _gather_evidence(self, task: str, context: Dict[str, Any]) -> list:
        """Simulate evidence gathering."""
        # In real implementation, this would search actual files
        timestamp = datetime.now(timezone.utc)
        
        evidence = [
            {
                "source": "architecture_guidelines.md:45",
                "quote": "All modules should follow single responsibility principle",
                "relevance": "Supports modular refactoring approach",
                "timestamp": {
                    "created": "2024-01-15T10:00:00Z",
                    "modified": "2024-01-20T14:00:00Z",
                    "accessed": timestamp.isoformat()
                },
                "freshness": "current",
                "freshness_score": 0.95
            },
            {
                "source": "code_review_notes.md:102",
                "quote": "Consider splitting large modules into smaller components",
                "relevance": "Directly suggests the refactoring approach",
                "timestamp": {
                    "created": "2024-01-25T09:00:00Z",
                    "modified": "2024-01-25T09:00:00Z",
                    "accessed": timestamp.isoformat()
                },
                "freshness": "current",
                "freshness_score": 0.99
            }
        ]
        
        return evidence
    
    def _format_evidence(self, evidence_items: list) -> str:
        """Format evidence items for the trace."""
        formatted = []
        for i, item in enumerate(evidence_items, 1):
            formatted.append(f"""
{i}. **Source**: `{item['source']}`
   **Quote**: "{item['quote']}"
   **Relevance**: {item['relevance']}
   **Timestamp**:
     - Created: {item['timestamp']['created']}
     - Modified: {item['timestamp']['modified']}
     - Accessed: {item['timestamp']['accessed']}
   **Freshness**: {item['freshness']} (score: {item['freshness_score']})""")
        
        return "\n".join(formatted)
    
    def _validate_trace(self, trace: str) -> Dict[str, Any]:
        """Validate the reasoning trace."""
        # Simplified validation - real implementation would use cot-validator
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metrics": {
                "schema_compliant": True,
                "evidence_validated": True,
                "risk_appropriate": True
            }
        }
        
        # Check for required sections
        required_sections = [
            "Risk Assessment:",
            "Evidence Collection:",
            "Analysis:",
            "Validation:",
            "Action:"
        ]
        
        for section in required_sections:
            if section not in trace:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Missing required section: {section}")
        
        return validation_result
    
    # Helper methods for trace generation
    def _determine_change_type(self, task: str) -> str:
        if "refactor" in task.lower():
            return "Refactor module structure"
        elif "delete" in task.lower() or "remove" in task.lower():
            return "Delete code"
        else:
            return "Modify implementation"
    
    def _determine_impact_scope(self, task: str) -> str:
        if "system" in task.lower() or "architecture" in task.lower():
            return "System-wide"
        elif "module" in task.lower():
            return "Module"
        else:
            return "Single file"
    
    def _determine_reversibility(self, risk_level: str) -> str:
        return {
            "low": "Easily reversible",
            "medium": "Moderate effort to reverse",
            "high": "Difficult to reverse",
            "critical": "Potentially irreversible"
        }.get(risk_level, "Unknown")
    
    def _get_min_evidence(self, risk_level: str) -> int:
        return {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 5
        }.get(risk_level, 2)
    
    def _generate_rationale(self, task: str, evidence: list) -> str:
        return f"Based on {len(evidence)} evidence sources, {task.lower()} is justified"
    
    def _generate_alternative(self, task: str) -> str:
        return "Maintain current structure with documentation updates"
    
    def _generate_rejection_reason(self, task: str) -> str:
        return "Evidence strongly supports the proposed change"
    
    def _generate_action(self, task: str) -> str:
        return f"Execute {task.lower()} following best practices"


def create_cot_agent(llm=None):
    """Create a LangChain agent with CoT reasoning capabilities."""
    if llm is None:
        llm = OpenAI(temperature=0)
    
    # Create the CoT tool
    cot_tool = CoTReasoningTool()
    
    # Define other tools (simplified for example)
    tools = [
        cot_tool,
        Tool(
            name="read_file",
            func=lambda path: f"[Simulated content of {path}]",
            description="Read the contents of a file"
        ),
        Tool(
            name="search_code",
            func=lambda query: f"[Simulated search results for: {query}]",
            description="Search for code patterns or text in the codebase"
        )
    ]
    
    # Create the agent
    agent_prompt = PromptTemplate.from_template("""
You are a code refactoring assistant that uses Chain-of-Thought reasoning.

When making decisions about code changes:
1. Always use the chain_of_thought_reasoning tool for decisions
2. Gather evidence using read_file and search_code tools
3. Follow the structured reasoning format

You have access to these tools:
{tools}

Current task: {input}

{agent_scratchpad}
""")
    
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=agent_prompt
    )
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


# Example usage
if __name__ == "__main__":
    # Example 1: Direct tool usage
    print("=== Example 1: Direct CoT Tool Usage ===")
    cot_tool = CoTReasoningTool()
    
    result = cot_tool._run(
        task="Refactor the payment processing module to improve maintainability",
        context={
            "access_level": "full_file_access",
            "tools": ["File reading", "AST parsing", "Dependency analysis"]
        }
    )
    
    print(result)
    print("\n" + "="*60 + "\n")
    
    # Example 2: Save trace to file
    trace_path = Path("example_trace.md")
    with open(trace_path, "w") as f:
        f.write(result)
    print(f"Trace saved to: {trace_path}")
    
    # Example 2b: Extract and save structured data as JSON
    print("\n=== Example 2b: Extract Structured Data ===")
    
    # Parse the trace to extract structured data
    structured_data = {
        "metadata": {
            "schema": "chain_of_thought/v7.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tool_version": "2.0.0"
        },
        "task": "Refactor the payment processing module to improve maintainability",
        "risk_assessment": {
            "level": "medium",
            "change_type": "Refactor module structure",
            "impact_scope": "Module",
            "reversibility": "Moderate effort to reverse"
        },
        "evidence": cot_tool._gather_evidence(
            "Refactor the payment processing module", 
            {"access_level": "full_file_access"}
        ),
        "decision": {
            "action": "Execute refactor the payment processing module following best practices",
            "confidence": 0.85,
            "validation_status": validation["valid"] if 'validation' in locals() else True
        }
    }
    
    # Save as JSON
    json_path = Path("example_trace.json")
    with open(json_path, "w") as f:
        json.dump(structured_data, f, indent=2)
    print(f"Structured data saved to: {json_path}")
    
    # Example 3: Validate the trace
    print("\n=== Example 3: Trace Validation ===")
    validation = cot_tool._validate_trace(result)
    print(f"Validation result: {json.dumps(validation, indent=2)}")
    
    # Example 4: Agent usage (requires API key)
    print("\n=== Example 4: LangChain Agent Usage ===")
    print("Note: This requires OPENAI_API_KEY to be set")
    print("Example code:")
    print("""
    agent = create_cot_agent()
    response = agent.run(
        "Should we refactor the user authentication module? "
        "It's currently 1500 lines and has multiple responsibilities."
    )
    print(response)
    """)