## Websocket

A WebSocket connection starts as a normal HTTP request, then the server upgrades it to a persistent WebSocket connection.
```
Browser/Electron
    ↓ HTTP request
GET /ws
Upgrade: websocket
Connection: Upgrade
    ↓
Go server upgrades connection
    ↓
Persistent bidirectional socket
```
After the upgrade:
* HTTP is finished
* the TCP connection stays open
* both sides can send messages anytime

Typical Go WebSocket flow:
1. Client connects
Frontend:
```ts
const ws = new WebSocket("ws://localhost:8080/ws");

ws.onopen = () => {
  ws.send("hello");
};

ws.onmessage = (e) => {
  console.log(e.data);
};
```
Browser sends: 
```
GET /ws HTTP/1.1
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: ...
```

2. Go backend
```go
package main

import (
    "context"
    "log"
    "net/http"

    "github.com/coder/websocket"
)

func wsHandler(w http.ResponseWriter, r *http.Request) {

    // performs the WebSocket handshake using the HTTP response writer w and request r. If it succeeds, you get conn, a WebSocket connection you can read/write messages on.
    // AcceptOptions{ ... } configures how the handshake is validated.
    // InsecureSkipVerify: true disables some security checks during the handshake (commonly origin/TLS-related validation depending on the library). This is usually only acceptable for local dev; in production it can allow unwanted cross-origin connections or weaken security assumptions.
    conn, err := websocket.Accept(w, r, &websocket.AcceptOptions{
        InsecureSkipVerify: true,
    })

    if err != nil {
        log.Println(err)
        return
    }

    // ensures the WebSocket connection is gracefully closed when your handler finishes.
    // websocket.StatusNormalClosure indicates a normal, graceful shutdown (close code 1000 ).
    // "" is an empty “reason” string (optional human-readable text).
    defer conn.Close(websocket.StatusNormalClosure, "")

    // coder/websocket’s APIs are context-aware
    ctx := context.Background()

    // starts an infinite loop.
    // Keep reading messages from the same WebSocket connection ( conn.Read(ctx) )
    // Exit the loop only when something goes wrong or the connection closes
    for {
        // reads the next WebSocket message from the connection.
        // typ is the WebSocket message type (usually text vs binary)
        // data is the full payload for that message as []byte (what the peer sent).
        typ, data, err := conn.Read(ctx)
        if err != nil {
            log.Println("read:", err)
            return
        }

        log.Printf("recv: %s\n", data)

        // sends a WebSocket message back to the client.
        // ctx controls cancellation/deadline for the write (if ctx is canceled or times out, the write fails).
        // data is the payload ( []byte ) to send.
        err = conn.Write(ctx, typ, data)
        if err != nil {
            log.Println("write:", err)
            return
        }
    }
}

func main() {
    http.HandleFunc("/ws", wsHandler)

    log.Println("listening on :8080")

    log.Fatal(http.ListenAndServe(":8080", nil))
}
```


`github.com/coder/websocket`

Another option: `github.com/gorilla/websocket`

tool: `brew install websocat`

```zsh
websocat ws://127.0.0.1:3333/api/v1/ws/chat
```

then send a JSON message (one per line):
```zsh
{"message":"hello"}
```
you will receive a response:
```zsh
{"reply":"..."}
```

`github.com/coder/websocket` rejects cross-origin WebSocket handshakes by default.


## Documentation

REST API
swagger

How to use Swaggo:
- Install Swaggo: `go get github.com/swaggo/swag/cmd/swag`
- Add Swagger comments to your handlers
- Run `swag init` to generate the OpenAPI spec
```zsh
swag init -g cmd/server/main.go -o internal/http/swagger
```
- `-g cmd/server/main.go` specifies the main package where your handlers are defined
- `-o internal/http/swagger` specifies the output file path for the generated OpenAPI spec file

Endpoints:
- `/swagger/index.html`: Swagger UI
- `/swagger/doc.json`: OpenAPI JSON
- `/swagger/*`: Swagger assets

Swagger assets

## AsyncAPI
WebSocket API

## Database

### `sqlc` + `goose` + `pgx`
This is preferred in production.
Tool | Responsibility
-|-
pgx | PostgreSQL driver + connection pool
sqlc | Generate type-safe Go code from SQL
goose | Database schema migrations

High-level architecture
```
SQL files
   │
   ▼
sqlc generates typed Go code
   │
   ▼
Generated code uses pgx
   │
   ▼
pgx talks to PostgreSQL
```
Meanwhile: goose manages schema migrations

For sqlite, need a different driver `modernc.org/sqlite`

### `gorm` + `golang-migrate/migrate`
Fast prototyping.

# air
Live-reload (hot reload) tool
- Watches your Go source files
- Automatically rebuilds and restarts your app when files change

`go install github.com/air-verse/air@latest`

`air -v`

`.air.toml`, the configuration file for the Air tool
```toml
#:schema https://json.schemastore.org/any.json
root = "."
tmp_dir = "tmp"

[build]
  cmd = "go build -o ./tmp/app ./cmd/server"
  bin = "tmp/app"
  include_ext = ["go"]
  exclude_dir = ["tmp", ".vscode", "docs", "tests"]
  delay = 1000

[log]
  time = true

[misc]
  clean_on_exit = true
```

air with swag 
```toml
[build]
  cmd = "swag init -g cmd/server/main.go -o internal/http/swagger && go build -o ./tmp/app ./cmd/server"
  exclude_dir = ["internal/http/swagger"]
```
- `#:schema ...`, adds a Taplo schema directive, stops the false “Additional properties are not allowed”.
- `cmd=...`, generate swagger docs then build
- need to exclude the `internal/http/swagger` directory from the build process, otherwise it will cause infinite recursion.

Sometimes need to restart air manually.

## Centralised configuration with Viper

`./internal/config/config.go`
`./internal/config/config.yaml`
`./.env` (optional)

Environment variables in bash. e.g. `export APP_ENV=dev`

```go
import (
	"github.com/spf13/viper"
)

type Config struct {
	Server   ServerConfig   `mapstructure:"server"`
	Logger   LoggerConfig   `mapstructure:"logger"`
	Database DatabaseConfig `mapstructure:"database"`
	CORS     CORSConfig     `mapstructure:"cors"`
}

type ServerConfig struct {
	Host string `mapstructure:"host"`
	Port string `mapstructure:"port"`
	Mode string `mapstructure:"mode"`
}

func LoadConfig() (*Config, error) {
  v := viper.New()

  // config.yaml file
	v.SetConfigName("config")
	v.SetConfigType("yaml")

	// when launch from backend root
	v.AddConfigPath("./internal/config")

  if err := v.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return nil, err
		}
	}

	var cfg Config
  // decode config.yaml file into your Go struct
  // viper uses mapstructure: "..." tags to map keys. e.g server.host -> cfg.Server.Host
	if err := v.Unmarshal(&cfg); err != nil {
		return nil, err
	}

	return &config, nil
}
```

```yaml
server:
  host: 0.0.0.0
  port: 3333
  mode: "debug"  # Default mode. Options debug, production
```

## Structured Logger with `log/slog`

Standard structured logging package introduced in Go 1.21.

It replaces the older style of plain text logging with structured, machine-readable logs.

Regular logging
```go
log.Println("user login", userID, ip)
```

Structured logging
```go
slog.Info("user login",
	"user_id", userID,
	"ip", ip,
)
```

Produces structured data like:
```json
{
  "time": "2026-05-22T09:00:00Z",
  "level": "INFO",
  "msg": "user login",
  "user_id": 123,
  "ip": "1.2.3.4"
}
```
Much better for:
* log searching
* observability
* monitoring systems
* cloud platforms

### Basic concepts
1. Logger
Main object used to write logs.
```go
logger := slog.Default()
```
Or create your own.
```go
logger := slog.New(handler)
```
2. Log levels
- Debug
- Info
- Warn
- Error
```go
slog.Debug("debug message")
slog.Info("server started")
slog.Warn("high memory usage")
slog.Error("database failed")
```
3. Structured fields
Instead of formatting strings. You attach key-value pairs. These fields become searchable metadata.

```go
slog.Info("login", "user", "alice", "ip", "1.2.3.4")
```
- `login` is the message
- `user` is a field
- `alice` is the value
- `ip` is a field
- `1.2.3.4` is the value

4. Handlers
Handlers decide:
* output format
* output destination
* filtering behavior

Two built-in handlers:
- TextHandler
- JSONHandler

TextHandler: Human readable
```go
handler := slog.NewTextHandler(os.Stdout, nil)
logger := slog.New(handler)
```
Output text:
```bash
time=2026-05-22T09:00:00Z level=INFO msg="started"
```

JSONHandler: Structured JSON logs.
```go
handler := slog.NewJSONHandler(os.Stdout, nil)
logger := slog.New(handler)
```
Output:
```go
{
  "time":"2026-05-22T09:00:00Z",
  "level":"INFO",
  "msg":"started"
}
```
- Very common in production systems.

5. Logger options
Configure behavior
```go
handler := slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
	Level: slog.LevelDebug,
})
```

6. Contextual logging
```go
logger := slog.Default().With(
	"service", "auth",
	"version", "1.0",
)

logger.Info("started")
```
Output includes those fields automatically.

7. Groups
Group related fields
```go
slog.Info("request",
	slog.Group("http",
		"method", "GET",
		"path", "/users",
	),
)
```
JSON:
```json
{
  "msg": "request",
  "http": {
    "method": "GET",
    "path": "/users"
  }
}
```

### components

`slog.Logger`

`slog.Level`

`slog.HandlerOptions{}`

`slog.New()`

`slog.NewJSONHandler(0)`

`slog.NewTextHandler(os.Stdout, nil)`

`slog.SetDefault()`
This sets the process-wide “default” slog logger to your configured Logger instance. 
It’s useful because other packages don’t need to import your internal/logger package or reference logger.Logger directly; they can just use slog.* and still get your formatting and level settings.

```go
logger.Init("info", "release") // sets default

slog.Debug("hidden") // filtered out at info
slog.Info("visible") // emitted using JSON handler to stdout
```
