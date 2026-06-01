## Type assertion

Type assertion in Go is a way to extract the concrete value/type stored inside an interface.

An interface in Go can hold values of many different concrete types.

```go
value, ok := i.(T)
```
- `i` -> interface value
- `T` -> expected concrete type

If the underlying value inside `i` is actually T, it succeeds.

```go
package main

import "fmt"

func main() {
    var v interface{}
    v = 123

    s, ok := v.(string)

    fmt.Println(s)
    fmt.Println(ok)
}
```

## Marshal and Unmarshal

`Marshal`: take an in-memory Go value (struct/map) and encode it into a transferable format (JSON/YAML bytes/text).

`Unmarshal`: take data that was parsed/loaded (JSON/YAML, or a generic map of keys/values) and decode it back into a Go value.

## `init()`

Every package can have its own `init()` function(s).

When a package is imported, Go automatically:
1. Initializes package-level variables
2. Runs all `init()` functions in that package
3. Then continues to the importing package

`init()` belongs to the package
It is not tied to a specific file.

if a package has multiple files
```
mypkg/
├── a.go
├── b.go
└── c.go
```
All `init()` functions across those files belong to the same package initialization phase.

`Init()` vs `init()`

`Init()` is Just a normal exported function. It is not automatically called when the package is imported.
It is used for Explicit initialization, which is cleaner than hidden `init()` behavior.

## Interface

An interface is a type that defines a set of methods a value must have. It describes **behavior, not data**.

Interfaces let you write code based on behavior instead of specific concrete types. this makes code:
- flexible
- reusable
- decoupled
- testable
- extensible

Without interfaces. A function only works with ONE exact type.
With interfaces: The function works with ANY type that has the required behavior.
- You can extend the system without modifying existing code.
- This is a major software engineering advantage.

### Examples
1. Decoupling code
Without interfaces:
```go
type PostgresDB struct{}
```
Your business logic depends directly on PostgreSQL. Hard to replace later.

With interfaces:
```go
type UserStore interface {
    GetUser(id int) User
}
```
Now business logic only cares about behavior. Implementation could be:
- PostgreSQL
- SQLite
- in-memory cache

2. Logger
Imagine an app that saves logs to a file.

Without interfaces:
```go
// define a struct
type FileLogger struct{}

// method declaration with receiver
func (f FileLogger) Log(msg string) {
    fmt.Println("writing to file:", msg)
}

// another process that uses the logger
func ProcessPayment(logger FileLogger) {
    logger.Log("payment processed")
}
```
Usage:
```go
logger := FileLogger{}
ProcessPayment(logger)
```
- this implements bounds `ProcessPayment` with `FileLogger`.
- if you want to introduce console logger for example, you need to re-write the `ProcessPayment` function to accept a `ConsoleLogger` struct with a `Log` method.

With interfaces:
```go
// define a general logger interface with a Log method
type Logger interface {
    Log(msg string)
}

// FileLogger struct and method
type FileLogger struct{}
func (f FileLogger) Log(msg string) {
    fmt.Println("writing to file:", msg)
}

// ConsoleLogger struct and method
type ConsoleLogger struct{}
func (c ConsoleLogger) Log(msg string) {
    fmt.Println("writing to console:", msg)
}

// the payment process
func ProcessPayment(logger Logger) {
    logger.Log("payment processed")
}
```
Usage:
```go
ProcessPayment(FileLogger{})
ProcessPayment(ConsoleLogger{})
```
- `ProcessPayment()` now depends on `Logger` interface. Not a specific concrete logger struct.
- interface implementation in golang is completely implicit.
  - `func (f FileLogger) Log(msg string)` and `func (c ConsoleLogger) Log(msg string)` implement `Logger.Log(msg string)`, because they both have a `Log` method.



### Structs vs interfaces

Struct defines data layout. Interface define behavior contract.

```go
type User struct {
    Name string
}
```

```go
type Greeter interface {
    Greet()
}
```

## Function vs Method

The difference between a function and a method is mainly about whether the function is attached to a type.

### Function
A function is a standalone piece of code.
It is not associated with any specific type.

```go
package main

import "fmt"

// Function (no receiver)
func Info(msg string) int {
    fmt.Println(msg)
}

func main() {
    Info("server started")
}
```
* Lives independently
* Called directly: `Info()`
* No connection to structs or types

### Method
A method is a function with a **receiver**.
That receiver “attaches” the function to a type (usually a struct).

```go
package main

import "fmt"

type Logger struct {
    prefix string
}

// Method (has receiver)
func (l Logger) Info(msg string) int {
    fmt.Println(l.prefix + " INFO: " + msg)
}

func main() {
    logger := Logger{prefix: "Backend"}
    logger.Info("server started")
}
```
- `(l Logger)`, `l` is the receiver variable.
- `Info()` is the method name. It is attached to `Logger`.
- equivalent normal function: `func Info(l Logger, msg string)`

Pointer receiver
Suppose the logger tracks log count.
```go
type Logger struct {
    prefix string
    count  int
}

func (l *Logger) Info(msg string) {
    l.count++

    fmt.Printf("%s INFO: %s (%d logs)\n",
        l.prefix,
        msg,
        l.count,
    )
}

func main() {
    logger := Logger{
        prefix: "[AuthService]",
    }

    logger.Info("user login")
    logger.Info("token refreshed")
}

```
- `(l *Logger)`, this is a pointer receiver.
- With pointer receiver, you can modify the struct fields, e.g. `l.count++`. Without pointer receiver, the method would modify only a copy.

When to use pointer receiver and when not to?
* ask one question: Do you need to modify the original value or avoid copying it?
* Value receiver -> small, read-only, stateless behavior
* Pointer receiver -> mutation, shared state, large structs, interface consistency

## goroutine

A goroutine in Go is a **lightweight thread** managed by the **Go runtime**. It allows you to **run functions concurrently**.

What is goroutine?
A goroutine is simply a function that runs with the keyword:
```
go functionName()
```
Example:
```go
package main

import (
    "fmt"
    "time"
)

func sayHello() {
    fmt.Println("Hello")
}

func main() {
    go sayHello() // runs concurrently

    time.Sleep(1 * time.Second) // give goroutine time to run
}
```
* go sayHello() starts a new goroutine
* It runs independently of main()

Why goroutines exist?
They make it easy to do concurrent programming.
* Handle multiple requests
* Run background tasks
* Parallelize workloads
* Build pipelines

How goroutines work?
Go runtime has a schedular:
* Many goroutines
* Fewer OS threads
* Goroutines are multiplexed onto threads

```
Goroutines (G1, G2, G3, G4...)
        ↓
Go Scheduler
        ↓
OS Threads (T1, T2)
        ↓
CPU cores
```

Go goroutine with parameters

```go
func printNumber(n int) {
    fmt.Println(n)
}

func main() {
    go printNumber(1)
    go printNumber(2)
}
```

### Wait group
A wait group is a way to wait for multiple goroutines to finish.

```go
package main

import (
    "fmt"
    "sync"
)

// this is a goroutine that waits for a wait group to finish
func task(wg *sync.WaitGroup) {
    defer wg.Done()
    fmt.Println("working")
}

func main() {
    // create a wait group
    var wg sync.WaitGroup

    // add a task to the wait group
    wg.Add(1)
    // start goroutine
    go task(&wg)

    // wait for all tasks to finish
    wg.Wait()
}
```

More about wait group:


### Goroutines + Channels

Use goroutines with channels to communicate between them.

```go

// this is a goroutine that sends a message to the channel
func worker(ch chan int) {
    ch <- 42
}

func main() {

    // create a channel
    ch := make(chan int)

    // start goroutine
    go worker(ch)

    // receive message from channel
    fmt.Println(<-ch)
}
```
- `ch := make(chan int)` creates a channel of type `chan int`.
  - unbuffered channel. send and receive must happen at the same time. 
  - x

## map

a `map` is a built-in data structure that stores key-value pairs

Syntax:
```go
map[keyType]valueType
```

Example:
```go
ages := map[string]int{
    "Alice": 25,
    "Bob":   30,
}
```

## Mutexes in Go

Mutexes (mutual exclusion) are synchronization primitives used to protect shared resources from concurrent access in Go.
- Prevent race conditions when multiple goroutines access shared data
- Ensure only one goroutine can access a critical section at a time
- Provide thread-safe operations

## 1. `sync.Mutex`
Basic mutex for exclusive access:
```go
package main

import (
    "fmt"
    "sync"
    "time"
)

type Counter struct {
    mu    sync.Mutex
    value int
}

func (c *Counter) Increment() {
    c.mu.Lock()   // Acquire lock
    defer c.mu.Unlock() // Release lock when function returns
    c.value++
}

func (c *Counter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.value
}

func main() {
    counter := &Counter{}

    // Start 100 goroutines
    for i := 0; i < 100; i++ {
        go counter.Increment()
    }

    time.Sleep(time.Second)
    fmt.Println("Final value:", counter.Value()) // Will be 100
}
```

### 2. `sync.RWMutex`
Reader-writer mutex allowing multiple readers or one writer:
```go
type SafeMap struct {
    mu   sync.RWMutex
    data map[string]int
}

func (sm *SafeMap) Read(key string) int {
    sm.mu.RLock()   // Multiple readers can acquire this
    defer sm.mu.RUnlock()
    return sm.data[key]
}

func (sm *SafeMap) Write(key string, value int) {
    sm.mu.Lock()    // Exclusive access for writing
    defer sm.mu.Unlock()
    sm.data[key] = value
}
```

## Key Methods
- `Lock()`: Acquire exclusive lock
- `Unlock()`: Release exclusive lock
- `RLock()`: Acquire read lock (RWMutex only)
- `RUnlock()`: Release read lock (RWMutex only)

## Best Practices
1. Always use `defer` to ensure unlock
2. Keep critical sections small
3. Use RWMutex when you have many readers, few writers
4. Avoid nested locks to prevent deadlocks
5. Consider using channels for communication instead of shared memory when possible

## Channels

Channels in Go are a built-in mechanism for communication between goroutines.

**A channel lets one goroutine send data to another safely**.

```go
goroutine A  --->  channel  ---> goroutine B
```

1. Creating a channel:
```go
ch := make(chan int)
```
This creates a channel that transports int. 

2. Send and receive
Send:
```go
ch <- 10
```
Receive:
```go
value := <-ch
```

Example:
```go
package main

import "fmt"

func main() {
    // create a channel
   	ch := make(chan int)

    // send a value to the channel in a goroutine
	go func() {
		ch <- 42
	}()

    // receive a value from the channel
	value := <-ch

	fmt.Println(value)
}
```

3. Blocking
Channels are blocking by default.

**Send blocks**
```go
ch <- 10
```
blocks until another goroutine receives.

It blocks the current goroutine (the one executing `ch <- 10`).
- The goroutine is paused at that line and can’t proceed to the next statement.
- It stays paused until the channel operation can complete.
  - unbuffered channel: until another goroutine is ready to do `<-` (receive).
  - buffered channel: until there's space in the buffer (i.e. buffer is  not full).

Sending on a nil channel blocks forever.
Sending on a closed channel panics.

**Receive blocks**
```go
value := <-ch
```
blocks until data is available. it blocks the current goroutine (the one trying to receive).
It stays blocked until the receive can complete:
- unbuffered channel: until some other goroutine does `ch <- 10` (a send) at the same time.
- buffered channel: until the buffer has least one value (buffer not empty).

4. Unbuffered channels
Default channels are unbuffered.

```go
ch := make(chan int)
```
- sender waits for receiver
- receiver waits for sender

They synchronize goroutines.

5. Buffered channels

```go
ch := make(chan, int, 3)
```
Capacity = 3.
Sends do not block until buffer is full.

```go
package main

import "fmt"

func main() {
	ch := make(chan int, 2)

	ch <- 10
	ch <- 20

	fmt.Println(<-ch)
	fmt.Println(<-ch)
}
```
Output:
```go
10
20
```

6. Channel direction

**Send only**
Sometimes a function should only send or only receive.
```go
func producer(ch chan<- int) {
	ch <- 10
	ch <- 20
}
```

`chan<- int`: send only, cannot receive.

**Receive only**
```go
func consumer(ch <-chan int) {
	value := <-ch
	fmt.Println(value)
}
```

`<-chan int`: receive only, cannot send.

*Production code often uses directional channels* because they make APIs safer.

7. Close channels
When no more values will be sent:
```go
ch := make(chan int)

close(ch)
```
Closing indicates: no more data is coming.

Reading until closed. A very common pattern.
```go
package main

import "fmt"

func main() {
	ch := make(chan int)

	go func() {
		ch <- 1
		ch <- 2
		ch <- 3
        // no more values will be sent
		close(ch)
	}()

	for value := range ch {
		fmt.Println(value)
	}
}
```
output:
```
1
2
3
```

The loop automatically exists when channel closes.

Checking whether channel is closed.
Receive returns two values:
```go
value, ok := <-ch
```
if closed: `ok = false`

```go
ch := make(chan int)

close(ch)

value, ok := <-ch

fmt.Println(value)
fmt.Println(ok)
```
Output:
```
0
false
```

8. Producer-Consumer pattern
One of the most common uses of channels.

Producer:
```go
func producer(ch chan<- int) {
	for i := 1; i <= 5; i++ {
		ch <- i
	}
	close(ch)
}
```

Consumer:
```go
func consumer(ch <-chan int) {
	for value := range ch {
		fmt.Println(value)
	}
}
```

Main:
```go
ch := make(chan int)
go producer(ch)
consumer(ch)
```

`go producer(ch)`, run `producer(ch)` in a new goroutine, concurrently.

`consumer()` runs synchronously in the main goroutine. Usually blocks reading from `ch` until the producer sends/close the channel.

9. Worker pool
Extremely common in production.

Jobs channel:
```go
jobs := make(chan int)
```
A channel to distribute jobs to workers.

Workers:
```go
func worker(id int, jobs <-chan int) {
	for job := range jobs {
		fmt.Printf("worker %d processing %d\n", id, job)
	}
}
```
A function to process jobs. 

Start workers:
```go
for i := 1; i <= 3; i++ {
	go worker(i, jobs)
}
```
Start 3 workers to process all the jobs concurrently.

Submit jobs:
```go
for i := 1; i <= 10; i++ {
	jobs <- i
}

close(jobs)
```

This pattern is used in:
- background processing
- image pipelines
- ETL jobs
- message consumers
- batch ML interface

10. Select statement
`select` works like switch for channels.

It lets a goroutine *wait on multiple channel operations simultaneously* and *execute* the case for whichever channel becomes *ready first*.

```go
select {
case msg := <-ch1:
	fmt.Println(msg)

case msg := <-ch2:
	fmt.Println(msg)

default:
	fmt.Println("no messages ready")
}
```
Whichever channel becomes ready first wins.

It lets one goroutine wait on multiple channel operations at the same time and proceed with whichever becomes ready first.
- It blocks the current goroutine until at least one case can run (unless there’s a default case).
- If `ch1` has a value available first, it receives from ch1 and prints it.
- If `ch2` becomes ready first, it receives from ch2 and prints it.
- If both are ready at the same time, Go chooses one case pseudo-randomly (fair-ish over time) to avoid starvation.

11. Timeout
Very common in production.

```go
select {
case result := <-resultCh:
	fmt.Println(result)

case <-time.After(5 * time.Second):
	fmt.Println("timeout")
}
```
If the result takes too long:
```
timeout
```

11. Fan-out
One producer -> many workers.
```
          Worker 1
         /
Producer
         \
          Worker 2
         \
          Worker 3
```

All workers consume from the same channel.
```go
jobs := make(chan Job)
```

Multiple goroutines:
```go
go worker(1, jobs)
go worker(2, jobs)
go worker(3, jobs)
```
Each job is handled by exactly one worker.

12. Fan-in
Many producers -> one consumer.
```
Worker 1 \
Worker 2  \
Worker 3   ---> Results Channel
Worker 4  /
```
All workers send results to one channel.
```
results <- value
```
Very common for parallel processing.

```go
package main

import (
	"fmt"
	"sync"
)

// Many producers (workers) -> one consumer (main goroutine).
func main() {
	jobs := []int{1, 2, 3, 4, 5, 6}
	results := make(chan int)

	var wg sync.WaitGroup

	workerCount := 3
	jobCh := make(chan int)

	// Start workers, that process jobs
	for workerID := 1; workerID <= workerCount; workerID++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()

			for job := range jobCh {
				// produce a result
				result := job * job
				results <- result
				_ = id // just to show we have worker id if needed
			}
		}(workerID)
	}

	// Feed jobs to job Channel
	go func() {
		for _, job := range jobs {
			jobCh <- job
		}
		close(jobCh) // tells workers "no more jobs"
	}()

	// Close results when all workers finish
	go func() {
		wg.Wait()
		close(results)
	}()

	// One consumer reads everything from the shared results channel
	for r := range results {
		fmt.Println("result:", r)
	}
}
```

## Conditional programming

`if`, `else`, `switch`

## if else

1. Basic if
```go
age := 20

if age >= 18 {
    fmt.Println("Adult")
}
```
Go does not require  parentheses around the condition:
```go
// Correct
if age >= 18 {
}

// Incorrect
if (age >= 18) {
}
```

2. if-else
```go
age := 16

if age >= 18 {
    fmt.Println("Adult")
} else {
    fmt.Println("Minor")
}
```

3. if-else if-else
```go
score := 85

if score >= 90 {
    fmt.Println("A")
} else if score >= 80 {
    fmt.Println("B")
} else if score >= 70 {
    fmt.Println("C")
} else {
    fmt.Println("Fail")
}
```

4. short variable declaration in if statement
A very common go pattern.
```go
if err := saveUser(); err != nil {
    log.Println(err)
}
```
The variable exists only within the if block.
This is used extensively in production Go code.

Example with map lookup:
```go
users := map[string]int{
    "alice": 1,
}

if id, ok := users["alice"]; ok {
    fmt.Println(id)
}
```
- `ok` = whether key exists.
- `id` = value of the key.

### Switch statement

```go
status := "pending"

switch status {
case "pending":
    fmt.Println("Waiting")
case "running":
    fmt.Println("In progress")
case "done":
    fmt.Println("Completed")
default:
    fmt.Println("Unknown")
}
```

Multiple values in a case: 
```go
switch role {
case "admin", "owner":
    fmt.Println("Full access")
case "user":
    fmt.Println("Limited access")
}
```

Expression-less switch
```go
score := 85

switch {
case score >= 90:
    fmt.Println("A")
case score >= 80:
    fmt.Println("B")
case score >= 70:
    fmt.Println("C")
default:
    fmt.Println("Fail")
}
```

Equivalent to a long if-else chain.

Type switch
```go
func printType(v interface{}) {
    switch v := v.(type) {
    case int:
        fmt.Println("int:", v)
    case string:
        fmt.Println("string:", v)
    default:
        fmt.Println("unknown")
    }
}
```
```go
printType(123)
printType("hello")
```
```bash
int: 123
string: hello
```

## Logical operators

&& - AND
```go
age := 25
hasLicense := true

if age >= 18 && hasLicense {
    fmt.Println("Can drive")
}
```

|| - OR
```go
role := "admin"
isOwner := false

if role == "admin" || isOwner {
    fmt.Println("Has access")
}
```

! - NOT
```go
isLoggedIn := false

if !isLoggedIn {
    fmt.Println("Please log in")
}
```

Use parentheses to group conditions.
```go
if (role == "admin" || role == "manager") && isActive {
    fmt.Println("Access granted")
}
```

## Loops

Only one loop keyword: `for`.

1. Traditional for loop 
syntax:
```go
for initialization; condition; post {
    // body
}
```

```go
for i := 0; i < 5; i++ {
    fmt.Println(i)
}
```

2. while style loop

Go does not have a while keyword.

```go
count := 0

for count < 5 {
    fmt.Println(count)
    count++
}
```

3. infinite loop
```go
for {
    fmt.Println("Hello, World!")
}
```

Usually combined with break
```go
for {
    if shouldStop() {
        break
    }

    doWork()
}
```

break, continue.

4. range over a slice
```go
nums := []int{10, 20, 30}

for i, v := range nums {
    fmt.Println(i, v)
}
```
- `i` = index of the element.
- `v` = value of the element.

ignore index:
```go
for _, v := range nums {
    fmt.Println(v)
}
```

5. range over a map
```go
users := map[string]int{
    "alice": 1,
    "bob":   2,
}

for k, v := range users {
    fmt.Println(k, v)
}
```
- `k` = key of the element.
- `v` = value of the element.
Map iteration is unordered.

6. Loop over a channel

```go
jobs := make(chan string)

go func() {
    jobs <- "job1"
    jobs <- "job2"
    close(jobs)
}

for job := range jobs {
    fmt.Println(job)
}
```
output:
```bash
job1
job2
```
The loop exists automatically when the channel is closed.
