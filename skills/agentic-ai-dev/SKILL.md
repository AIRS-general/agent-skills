# Develop LLM-based AI applications

## Python langgraph

## Golang EINO

## llama.cpp

```zsh
brew install llama.cpp
```

create a folder for models
```zsh
mkdir models
```

Download a GGUF model
llama.cpp uses `.gguf` models.

Run a local chat server:
```zsh
llama-server \
  -m models/Qwen2.5-7B-Instruct-Q4_K_M.gguf \
  -c 8192 \
  -ngl 999
```
- `-m`: model path
- `-c`: context window
- `-ngl`: GPU layers (999 = offload all possible layers to Apple GPU).

Recommended models for MacBooks:
- 16GB RAM: 3B–7B Q4 models
- 32GB RAM: 7B–14B Q4/Q5
- 64GB+ RAM: 32B quantized models possible

Models

`google/gemma-4-26B-A4B-it`
- `it`: instruction tuned
- `26B`: total parameter count
- `A4B`: ~4B active parameters per token. indicates a Mixture-of-Experts (MoE) model.

`~/llms`
Create venv with uv
```zsh
uv add huggingface_hub
```

```zsh
hf download google/gemma-4-26B-A4B-it --local-dir ./models/gemma-4-26B
```

## quantization

Q4_K_M (recommended default): This is the standard “sweet spot”.

Pros:
* Very good quality
* Good speed
* Fits large models on consumer hardware
* Most tested/popular quant

Cons:
* Slight quality loss vs FP16

IQ4_XS: A newer “importance-aware” quantization.
squeezing large models into smaller RAM. longer contexts.

Pros
* Smaller than Q4_K_M
* Lower RAM usage
* Often surprisingly strong quality

Cons:
* Slightly slower
* Less universally tested

Q5_K_M: Higher quality 5-bit quant.

Pros
* Better reasoning retention
* Better coding/math
* Closer to FP16

Cons
* Larger
* More RAM usage
* Slightly slower

Q6_K: very high-quality quantization
Pros
* Near-FP16 quality
* Excellent reasoning

Cons
* Heavy
* Large disk size
* More VRAM/RAM needed

Q8_0: 8-bit quantization. almost full precision.
Pros
* Minimal quality loss

Cons
* Huge
* Slow
* Massive RAM usage

For MacBook with 32 GB memory, Q4_K_M first, then IQ4_XS if memory is a concern.

## WebSocket chat with Golang

ChatMessage type
```go
type WSClientMessage struct {
	// options: user_message, ping, cancel
	Type      string `json:"type,omitempty"`
	// used for identify different chat sessions
	//   a user can have multiple sessions. If only one endless chat, can remove.
	SessionID string `json:"session_id,omitempty"`
	// used for identify different messages
	MessageID string `json:"message_id,omitempty"`
	Content   string `json:"content,omitempty"`
}
```


```go

import "github.com/coder/websocket"

type ChatHandler struct{}

func () {

	// Upgrade the incoming HTTP request to a WebSocket connection.
	conn, err := websocket.Accept(w, r, &websocket.AcceptOptions{
		InsecureSkipVerify: true,
	})
	if err != nil {
		return
	}
	// Best-effort close handshake when we exit the handler.
	defer conn.Close(websocket.StatusNormalClosure, "")

}
```

## Golang, Python, TypeScript for AI agents

How well the language supports:
* LLM orchestration
* Concurrency
* State management
* Tool execution
* Reliability
* Maintainability of large agent systems

Aspect | Go | Python | TypeScript
-|-|-|-
Simplicity | Excellent | Excellent | Good
Type Safety | Strong | Weak | Strong
Concurrency | Excellent | Good | Good
Async Programming | Simple (goroutines) | Moderate | Complex but powerful
Performance | Excellent | Poor | Moderate
Memory Usage | Excellent | Poor | Moderate
Large Codebase Maintainability | Excellent | Moderate | Good
Rapid Prototyping | Moderate | Excellent | Good
Runtime Errors | Few | Many |Few
Agent Orchestration | Excellent | Good | Good
Learning Curve | Low | Lowest | Medium

1. Type system

For AI agents, many bugs appear during execution:
* Wrong tool schema
* Wrong state structure
* Missing fields
* Wrong message format
Large multi-agent systems become difficult to maintain.

With type system, compiler catches many issues.
For agent systems with:
* tools
* memory
* state machines
* workflows
this becomes valuable.

Go and TypeScript win here.

2. Concurrency
Agents spend most of their time waiting for:
* LLM responses
* APIs
* databases
* tools
Concurrency matters more than raw speed.

Go has the best concurrency model.

3. Error handling

Agent systems fail constantly:
* tool unavailable
* model timeout
* malformed JSON
* network issues

Go explicitly handles errors. verbose by reliable.

4. Data structures for Agent state
Agents usually maintain:
- messages
- memory
- plan
- tool results
- context
- status

More explicit.
Go, better for long-term maintenance.

TypeScript > Go > Python.

5. Generics
Modern agent frameworks heavily use generics.

TypeScript > Go > Python.

6. Parallel Tool Execution
Suppose an agent needs:
- Search
- Weather
- Database
- Calculator
simultaneously.

Go > TypeScript > Python.

7. Building long-running agents
Imagine:
```
Agent runs for weeks
Maintains memory
Coordinates workers
Handles retries
Processes queues
```

Go, excellent fit.
- compiled
- low memory
- strong typing
- goroutines
- predictable behavior

Go > TypeScript > Python.

### Summary:

1. Golang
Best for:
- Production agent runtimes
- Long-running workflows
- Multi-agent orchestration
- High concurrency

Strength:
- simplicity + concurrency + reliability

Weakness:
- More boilerplate
- Less expressive

2. Python
Best for:
* Research
* Rapid prototyping
* Experimental agent designs

Strength:
* Fastest development speed

Weakness:
* Weak type safety
* Harder to maintain at scale
