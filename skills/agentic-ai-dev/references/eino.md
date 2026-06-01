## Eino

An LLM application framework for Go.

LangChain/LlamaIndex style architecture, but designed idiomatically for Go.

It focuses heavily on:
* type safety
* orchestration
* streaming
* concurrency
* production-grade AI services

### High level mental model
Eino is built around 3 major concepts:

concept | purpose
-|-
Components | reusable AI building blocks
Composition | connect components int workflows
Agents (ADK) | autonomous tool-using AI agents

1. Components
Components are the core primitives.

Component | Purpose
-|-
ChatModel | LLM wrapper
Tool | callable functions
Retriever | RAG retrieval
Embedding | Embeddings
PromptTemplate | prompt formatting

```go
model, _ := openai.NewChatModel(ctx, config)
```
Eino abstracts providers behind interfaces. Business logic stays unchanged when switching models.

2. Messages
LLMs communicate via messages.
Typical structure:
```go
[]*schema.Message
```

Example:
```go
messages := []*schema.Message{
    schema.SystemMessage("You are helpful"),
    schema.UserMessage("Hello"),
}
```
Very similar to OpenAI chat format.

3. Invoke vs stream
Most components support:

Method | Purpose
`Invoke()` | normal request/response
`Stream()` | token streaming

```go
resp, err := model.Invoke(ctx, messages)

stream, err := model.Stream(ctx, messages)
```

4. Tools
Tools are functions callable by the LLM.

Tool calling is fundamental for:
* agents
* automation
* RAG
* external APIs

5. Chains
Simplest orchestration.

Example:
```go
Prompt -> LLM -> Parser
```

Good for:
- simple workflow
- RAG pipelines
- prompt pipelines

6. Graphs
A major production-oriented feature.

Graphs allow:
- branching
- loops
- parallel execution
- state sharing
- retries
- complex orchestration

7. Workflow
Higher-level orchestration API.

Adds:
- field-level mapping
- structured data flow
- DAG-style execution

Good for:
- enterprise pipelines
- structured AI workflows
- multi-stage processing

8. Agents (ADK)
Agent development kit. provides prebuilt agent patterns.

```go
ChatModelAgent
```
implements ReAct-style agents:
```
Think -> Tool -> Observe -> Think
```
The agent automatically:
* decides tool usage
* manages memory/state
* loops until completion

9. Multi-agent support
Eino supports:
* agent-as-tool
* supervisor agents
* hierarchical agents
* orchestration agents

```
Supervisor Agent
    ├── Research Agent
    ├── Coding Agent
    └── Summary Agent
```

10. Streaming architecture (major concept)
Eino treats streaming as a core system primitive.
It automatically handles:
* stream merging
* stream splitting
* stream concatenation
* stream propagation

Meaning downstream nodes can transparently consume streamed tokens.  

This is one of the framework’s strongest technical features.

12. Callbacks/observability
Eino has middleware-like callbacks:

Callback | Purpose
-|-
OnStart | execution starts
OnEnd | execution ends
OnError | Errors
streaming callbacks | stream observability

useful for:
- logging
- tracing
- metrics
- debugging
- telemetry

13. Concurrency
Eino naturally leverages:

* goroutines
* channels
* context
* cancellation
* parallel execution

Better fit for high-concurrency backend services than many Python stacks.

14. Typical architecture

```
HTTP API
   ↓
Agent
   ↓
Graph
   ├── Retriever
   ├── ChatModel
   ├── Tool
   └── Memory
```

### APIs
