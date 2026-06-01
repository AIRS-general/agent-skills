# Context

`context` is a standard way to carry **request-scoped information**, timeouts, deadlines, and cancellation signals across function calls and goroutines.

Provided by the standard library: `context`

### Why context exists?
Imagine:
* An HTTP request comes in
* Your server:
    * queries a database
    * calls another API
    * starts goroutines
* The client disconnects

Without context, all those operations may continue running unnecessarily.

`context` solves this by **allowing cancellation to propagate** through the call chain.

### Core concepts
1. Context carries cancellation A parent operation can cancel child operations. 

```go
ctx, cancel := context.WithCancel(context.Background())

go func() {
    <-ctx.Done()
    fmt.Println("cancelled")
}()

cancel()
```
Output:
```
cancelled
```

2. Context carries deadlines/timeouts
```go
ctx, cancel := context.WithTimeout(
    context.Background(),
    2*time.Second,
)
defer cancel()
```
After 2 seconds:
```go
<-ctx.Done()
fmt.Println(ctx.Err())
```
Output:
```
context deadline exceeded
```


3. Context propagates through function calls
Convention in Go:
- `ctx context.Context` is the first parameter
- pass it down
```go
func FetchUser(ctx context.Context, id int) error {
    // use ctx
}
```

### The context tree
Contexts forms a hierarchy.
```
Background()
   └── WithCancel()
         └── WithTimeout()
               └── WithValue()
```
Cancelling a parent cancels all its children.

### Context constructors
1. `context.Background()`
Root context.
Used at app startup or tests.
```go
ctx := context.Background()
```
2. `context.ToDO()`
Placeholder when unsure which context to use.
```go
ctx := context.TODO()
```
3. `context.WithCancel()`
Manual cancellation
```go
ctx, cancel := context.WithCancel(parent)
defer cancel()
```
4. `context.WithTimeout()`
Auto-cancel after duration.
```go
ctx, cancel := context.WithTimeout(parent, 5*time.Second)
defer cancel()
```
5. `context.WithDeadline()`
Cancel at exact time.
```go
deadline := time.Now().Add(5 * time.Second)

ctx, cancel := context.WithDeadline(parent, deadline)
defer cancel()
```
6. `context.WithValue()`
Attach request-scoped values.
```go
ctx := context.WithValue(
    context.Background(),
    "userID",
    123,
)
```
Retrieve:
```go
id := ctx.Value("userID")
```

### Methods

1. `ctx.Done()`, return a channel closed on cancellation.

`<-ctx.Done()`, one of the most common pattern in Go.

`ctx.Done()` returns a read-only channel. the channel is closed when the context is cancelled or times out.
`<-channel`, the `<-` operator receives from a channel:
```go
<-ctx.Done()
```
Block and wait until the context is cancelled.

the `Done()` channel is created when the context is created, but it is only closed when when the context is cancelled or times out. 
- Done is channel of empty struct: `<-chan struct{}`.
Before cancelling, `<-ctx.Done()` blocks.
- It blocks because the channel has no data. `<-ctx.Done()` waits for data or the channel to be closed.
- there will be no data in the channel.
- so just wait for the channel to be closed.
After cancelling (`cancel()`), `<-ctx.Done()` unblocks.

Example:
```go
ctx, cancel := context.WithCancel(context.Background())

go func() {
    fmt.Println("Waiting...")

    <-ctx.Done()

    fmt.Println("Cancelled!")
}()

time.Sleep(2 * time.Second)
cancel()

time.Sleep(time.Second)
```
Output
```
Waiting...
Cancelled!
```

What happened? 
- goroutine starts
- it reaches `<-ctx.Done()` and blocks
- main goroutine calls `cancel()`
- the context closes the `Done` channel
- `<-ctx.Done()` unblocks
- execution continues


`ctx.Err()`
Why context ended. Possible errors:
```go
context.Canceled
context.DeadlineExceeded
```

`context.CancelFunc` is the function you call to cancel a Context created with `WithCancel`, `WithTimeout`, or `WithDeadline`.
