## How to build custom AI agent

Components:
- Agent loop
- LLM
- Tools
- Memory/State
- Human-in-the-loop
- State graph
- Multi-agent
- MCP
- x

### A basic Agent architecture
Think in terms of components.

A production AI agent is usually composed of:
```
User
 ↓
API Layer
 ↓
Agent Loop
 ↓
LLM
 ↓
Tools
 ↓
Memory / State
 ↓
Response
```

1. Define the agent's goal.
Before writing code, decide:
- what problem does the agent solve?
- what tools can it use?
- what actions can it perform?
- what should it never do?

2. Build the core LLM wrapper
Create a thin abstract over your LLM provider.
```go
type LLM interface {
  Generate(ctx context.Context, messages []Message) (string, error)
}
```
Implementation might call:
- OpenAI API
- Anthropic API
- Local models via llama.cpp

3. Define a tool interface
Agents become useful when they can do things.

```go
type Tool interface {
    Name() string
    Description() string

    Execute(
        ctx context.Context,
        input string,
    ) (string, error)
}
```
Example tools:
- web search
- database query
- calculator
- file reader

4. Create a tool registry
```go
type ToolRegistry struct {
    tools map[string]Tool
}
```
```go
registry.Register(searchTool)
registry.Register(weatherTool)
registry.Register(dbTool)
```
The agent can discover available tools dynamically.

5. Implement the Agent loop
This is the heart of the system.
```
1. Receive user request
2. Ask LLM what to do
3. Execute tool if needed
4. Feed result back to LLM
5. Repeat until final answer
```

Pseudo-code:
```go
for {
  decision := llm.Decide()

  switch decision.Type {
    case "tool":
      result := runTool()
      appendToContext(result)
    case "answer":
      return decision.Content
  }
}
```

This is essentially how many agent frameworks work internally.

6. Maintain conversation state
Define agent state.
```go
type AgentState struct{
  Messages []Message
  Variables map[string]any
}
```
State typically stores:
- User messages
- Tool results
- Intermediate reasoning 
- Session metadata

7. Add memory
Short-term memory.
Current conversation: `[]Message`

Long-term memory.
Store in:
- PostgreSQL
- SQLite
- Vector database
Example:
- User preferences
- Previous tasks
- Historical interactions

8. Add retrieval (RAG)
For domain-specific knowledge:
```
Question
 ↓
Embedding
 ↓
Vector Search
 ↓
Relevant Documents
 ↓
LLM
```

Common choices:
- pgvector
- Qdrant
- Weaviate

9. Add structured outputs 
Avoid parsing free text.
Ask the model for JSON.
```go
type AgentDecision struct {
  Action string `json:"action"`
  Tool   string `json:"tool"`
  Input  string `json:"input"`
}
```
```json
{
  "action": "tool",
  "tool": "search",
  "input": "latest golang release"
}
```
Structured outputs make agents mush more reliable. 

10. Add observability
Log everything.
```go
slog.Info(
    "tool executed",
    "tool", toolName,
    "duration", elapsed,
)
```
Track:
- Prompt
- Tool calls
- Latency
- Token usage
- Errors

11. Add reliability
Production agents need:
Retries
```
for i := 0; i < 3; i++ {
  ...
}
```

Timeouts
```go
ctx, cancel = context.WithTimeout(ctx, 30*time.Second)
```

Validation. Validate tool outputs before passing them back.

12. Add workflow orchestration
For long-running jobs:
```
Agent
 ↓
Temporal Workflow
 ↓
Activities
 ↓
External Systems
```
Useful for:
- ML training
- Report generation
- Batch processing
- Multi-day tasks

Example architecture:
```
HTTP API
    ↓
Agent Service
    ↓
Agent Loop
    ↓
LLM
    ↓
Tool Registry
        ├─ Search Tool
        ├─ DB Tool
        ├─ File Tool
        └─ Calculator Tool
    ↓
Memory Store
        ├─ PostgreSQL
        └─ pgvector
```

## Human-in-the-loop
Human-in-the-loop (HITL) is essentially **pausing the agent at specific decision points** and **waiting for a human response before continuing**.

It is a workflow/state management feature.

Architecture
```
User Request
     ↓
Agent
     ↓
Needs Approval?
     ↓
    Yes
     ↓
Create Review Task
     ↓
Human Reviews
     ↓
Approve / Reject / Edit
     ↓
Agent Continues
```
