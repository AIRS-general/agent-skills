## The `net/http` package

`net/http` is Go’s standard library package for:
* HTTP servers
* HTTP clients
* routing
* middleware
* REST APIs

1. Minimal HTTP server

```go
package main

import (
    "fmt"
    "net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintln(w, "hello")
}

func main() {
    http.HandleFunc("/", handler)

    http.ListenAndServe(":8080", nil)
}
```
- open `http://localhost:8080` 

2. Core concepts
Three fundamental pieces: 
Concept | Purpose 
-|-
`http.Request` | incoming request
`http.ResponseWriter` | outgoing response
handler | function that processes request

3. Handler function
Signature:
```go
func(w http.ResponseWriter, r *http.Request)
```

```go
func hello(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintln(w, "hello world")
}
```

4. Request object
contains everything from the client.
```go
func handler(w http.ResponseWriter, r *http.Request) {
    fmt.Println(r.Method)
    fmt.Println(r.URL.Path)
    fmt.Println(r.Header)
}
```

Common fields:
Field | Meaning
-|-
`r.Method` | GET/POST/etc
`r.URL` | URL info
`r.Header` | request headers
`r.Body` | request body
`r.Context()` | request context
`r.RemoteAddr` | client address

5. ResponseWriter
Used to send response back.
```go
w.Write([]byte("hello"))
```

6. HTTP status code
```go
w.WriteHeader(http.StatusCreated)
```
Example:
```go
func handler(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusCreated)
    w.Write([]byte("created"))
}
```

`WriteHeader()` must happen before writing body.

7. JSON response
Very common in APIs.

```go
package main

import (
    "encoding/json"
    "net/http"
)

type User struct {
    Name string `json:"name"`
    Age  int    `json:"age"`
}

func handler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    user := User{
        Name: "Alice",
        Age:  25,
    }

    json.NewEncoder(w).Encode(user)
}
```
- `json.NewEncoder(w).Encode(user)` encodes `user` into JSON and writes it to `w`.

8. Reading JSON requests
```go
func handler(w http.ResponseWriter, r *http.Request) {
    var user User

    err := json.NewDecoder(r.Body).Decode(&user)
    if err != nil {
        http.Error(w, "bad request", http.StatusBadRequest)
        return
    }

    fmt.Println(user.Name)
}
```
- `json.NewDecoder(r.Body).Decode(&user)` decodes `r.Body` into `user`.

9. Routing
Basic stdlib routing.
```go
http.HandleFunc("/users", usersHandler)
http.HandleFunc("/posts", postsHandler)
```

stdlib routing is limited.

10. Middleware concept
**Middleware wraps handlers**.

```go
func logger(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        fmt.Println(r.Method, r.URL.Path)
        next.ServeHTTP(w, r)
    })
}
```
`next.ServeHTTP(w, r)` passes control to the next handler in the chain.

11. `http.Handler` interface
Very important concept.
```go
type Handler interface {
    ServeHTTP(w http.ResponseWriter, r *http.Request)
}
```
- Anything implementing this becomes a handler.

12. `http.HandlerFunc`
Adapter type:
```go
type HandlerFunc func(w http.ResponseWriter, r *http.Request)
```
This lets normal functions behave like handlers.

That’s why this works:
```go
http.HandleFunc("/", hello)
```

13. Server lifecycle
```go
Client -> TCP connection -> HTTP request -> Handler -> Response
```

14. Concurrency model
Very important: each request is handled in its own goroutine.
`func handler(w, r)` may run concurrently thousands of times.
Shared data needs synchronization:
```go
sync.Mutex
sync.RWMutex
atomic
channels
```

15. HTTP client basics 
```go
resp, err := http.Get("https://example.com")
if err != nil {
    panic(err)
}
defer resp.Body.Close()
```

Reading body:
```go
body, _ := io.ReadAll(resp.Body)
fmt.Println(string(body))
```

### Start server
1. Simplified version
`http.ListenAndServe`
```go
http.ListenAndServe(":8080", handler)
```

Internally:
```go
server := &http.Server{
    Addr:    ":8080",
    Handler: handler,
}

server.ListenAndServe()
```

2. Configurable server (production style)
```go
server := &http.Server{
    Addr:              addr,
    Handler:           v1.NewRouter(cfg),
    ReadHeaderTimeout: 5 * time.Second,
    ReadTimeout:       15 * time.Second,
    WriteTimeout:      60 * time.Second,
    IdleTimeout:       60 * time.Second,
}

server.ListenAndServe()
```

### production best practices

Usually you want:
* custom http.Server
* timeouts
* graceful shutdown
* middleware
* structured logging
* context propagation

### Modern stack
* net/http
* Chi
* slog
* pgx
* sqlc

### http.Handler vs http.HanderFunc

Use http.HandlerFunc for:
* **API endpoints**
* route handlers
* most business logic handlers

```go
r.Get("/users", getUsers)
```

Use http.Handler interface for:
* **middleware**
* reusable infrastructure
* generic components
* wrappers/proxies

```go
func Auth(next http.Handler) http.Handler
```
