## `sync` package

Provides synchronization primitives for coordinating concurrent goroutines safely.

The most commonly used types are:
* `sync.Mutex`
* `sync.RWMutex`
* `sync.WaitGroup`
* `sync.Once`
* `sync.Cond`
* `sync.Map`
* `sync.Pool`

1. `sync.Mutex`
A mutex **protects shared data from being accessed simultaneously by multiple goroutines**.

**Without a mutex**:
```go
package main

import (
  "fmt"
  "sync"
)

var counter int

func increment() {
  counter++
}

func main() {
  const goroutines = 8
  const incrementsPerGoroutine = 100_000

  var wg sync.WaitGroup
  wg.Add(goroutines)

  for i := 0; i < goroutines; i++ {
    go func() {
      defer wg.Done()
      for j := 0; j < incrementsPerGoroutine; j++ {
        increment()
      }
    }()
  }

  wg.Wait()

  expected := goroutines * incrementsPerGoroutine
  fmt.Println("expected:", expected, "got:", counter)
}
```
This causes a race condition.

Reason: `counter++` is a read-modify-write sequence, not an atomic operation.
- Goroutine A reads `counter` (say it reads 41)
- Goroutine B reads `counter` (also reads 41)
- A writes back 42
- B writes back 42

One increment is “lost”, so you often print a value smaller than `expected`.

**With mutex**:
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
    c.mu.Lock()   // Acquire lock, block other goroutines
    defer c.mu.Unlock() // Release lock when function returns, so other goroutines can enter
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

`mu.Lock()`, only one goroutine can enter. other goroutines block until `mu.Unlock()`.

2. `sync.RWMutex`

A read-write mutex.

Allows:
* **multiple readers** simultaneously
* only **one writer** exclusively

Useful when:
* reads are frequent
* writes are rare

Example:
```go
package main

import (
	"fmt"
	"sync"
)

type Cache struct {
	mu   sync.RWMutex
	data map[string]string
}

func (c *Cache) Get(key string) string {
	c.mu.RLock()
	defer c.mu.RUnlock()

	return c.data[key]
}

func (c *Cache) Set(key, value string) {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.data[key] = value
}

func main() {
	cache := Cache{
		data: make(map[string]string),
	}

	cache.Set("name", "golang")

	fmt.Println(cache.Get("name"))
}
```

`mu.RLock()` / `mu.RUnlock()` = shared (read) lock.
- Multiple goroutines can read from the cache simultaneously.
- Write is blocked by the read locks until all read locks are released.

`mu.Lock()` / `mu.Unlock()` = exclusive (write) lock
- only one goroutine can hold it, and it blocks all readers and writers. 

Difference between `sync.Mutex` and `sync.RWMutex`
Lock Type | Readers | Writers
`.Mutex` | onc at a time | one at a time
`RWMutex` | many readers | one writer

3. `sync.WaitGroup`
Waits for goroutines to finish. Very common in production.

```go
package main

import (
	"fmt"
	"sync"
	"time"
)

func worker(id int, wg *sync.WaitGroup) {
	defer wg.Done()

	time.Sleep(time.Second)

	fmt.Println("worker done:", id)
}

func main() {
  // define a wait group
	var wg sync.WaitGroup

	for i := 1; i <= 3; i++ {
    // add 1 to the counter
		wg.Add(1)

    // start a goroutine
    // when the goroutine finishes, decrement the counter
		go worker(i, &wg)
	}

  // block for all goroutines to finish
	wg.Wait()

	fmt.Println("all workers done")
}
```

`wg.Done()` = decrement the counter by 1.
- When the counter reaches 0, `Wait()` returns.

`wg.Add(n)` = increment the counter by n.

`wg.Wait()` = block until the counter reaches 0.

4. `sync.Once`
Ensures something runs only once.

Very common for:
* singleton initialization
* config loading
* DB connection setup

Example:
```go
package main

import (
	"fmt"
	"sync"
)

// declare a once variable
var once sync.Once

func initialize() {
	fmt.Println("initialized")
}

func main() {
	for i := 0; i < 5; i++ {
    // run initialize() only once, even multiple goroutines call it
		go once.Do(initialize)
	}

	// wait a bit
	fmt.Scanln()
}
```
