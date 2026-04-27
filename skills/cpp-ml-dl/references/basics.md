# C++ Basics

## Minimal Program

```cpp
#include <iostream>  // library for input/output
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
```

* `#include` directive -> brings in libraries
* `main()` -> entry point
* `std::cout` -> output stream
* `return 0` -> program exit status

## Variables & Types

```cpp
int a = 10;          // integer
double b = 3.14;     // floating point
char c = 'x';        // character
bool flag = true;    // boolean
std::string s = "hi"; // string (needs <string>)
```

Modern C++ (type inference):

```cpp
auto x = 42;   // compiler deduces type
```

## Control Flow

If / Else
```cpp
if (a > 5) {
    std::cout << "Greater\n";
} else {
    std::cout << "Smaller\n";
}
```

Switch
```cpp
switch(a) {
    case 1: break;
    case 2: break;
    default: break;
}
```

Loops

```cpp
for (int i = 0; i < 5; i++) {
    std::cout << i << "\n";
}
while (a > 0) {
    a--;
}
```

Range-based loop (modern C++):

```cpp
for (auto v : {1, 2, 3}) {
    std::cout << v << "\n";
}
```

## Functions

```cpp
int add(int x, int y) {
    return x + y;
}
```

Inline / modern style:

```cpp
auto add(int x, int y) -> int {
    return x + y;
}
```

## Arrays & Vectors

C-style array

```cpp
int arr[3] = {1, 2, 3};
```

Preferred: `std::vector`

```cpp
#include <vector>
std::vector<int> v = {1, 2, 3};
v.push_back(4);
std::cout << v[0];
```

## Pointers (important for performance work)

```cpp
int x = 10;
int* p = &x;   // pointer to x
std::cout << *p;  // dereference
```

## References (very important in modern C++)

```cpp
int x = 10;
int& ref = x;  // reference
ref = 20;      // modifies x
```

## Classes (OOP basics)

```cpp
class MyClass {
public:
    int value;
    MyClass(int v) {
        value = v;
    }
    int getValue() {
        return value;
    }
};
```

Usage:
```cpp
MyClass obj(10);
std::cout << obj.getValue();
```

## Namespaces

```cpp
std::cout << "Hello";
```

Avoid:
```cpp
using namespace std; // not recommended in large systems
```

## Header Files

Split code:
`math_utils.h`

```cpp
#pragma once
int add(int a, int b);
```

`math_utils.cpp`

```cpp
#include "math_utils.h"
int add(int a, int b) {
    return a + b;
}
```


## Compile & Run

```
g++ main.cpp -o app
./app
```

## Key Modern C++ Features (you should prioritize)

* `auto`
* `std::vector`, `std::array`
* `references (&)`
* const correctness
* smart pointers:
```cpp
#include <memory>
std::unique_ptr<int> p = std::make_unique<int>(10);
```

* range-based loops
* RAII (resource management pattern)

## Very Important Mindset Shift (from Python → C++)

* Memory is explicit
* Types matter (a lot)
* Performance is controllable
* Compilation errors are your friend

## RAII

## Pointer vs reference

Pointers and references in C++ both let you work with existing variables without copying them — but they behave quite differently.

### Core Idea
* Pointer (T*) → a variable that stores an address
* Reference (T&) → an alias to an existing variable

Mental model:
* Pointer = “I can move around memory”
* Reference = “This IS that variable”

Practical advise:
* Prefer references by default
* Use const references for inputs:
```cpp
void fit(const Matrix& X);
```

References are often implemented under the hood as pointers, but: They behave like safer, restricted pointers at the language level.

### Basic comparison
Pointer:
```cpp
int x = 10;
int* p = &x;

std::cout << *p;  // 10
```

Reference:
```cpp
int x = 10;
int& r = x;

std::cout << r;  // 10
```

### Key differences

1. Initialization
* Pointer: can be uninitialized (dangerous)
* Reference: must be initialized
```cpp
int* p;        // OK (but unsafe)
int& r;        // ❌ ERROR
```

2. Nullability
* Pointer: can be `nullptr`
* Reference: cannot be `null`

```cpp
int* p = nullptr;  // valid
int& r = ???;      // must refer to valid object
```
This is why **references are safer**.

3. Reassignment
Pointer can point elsewhere

```cpp
int a = 1, b = 2;
int* p = &a;

p = &b;  // now points to b
```

Reference cannot be reassigned
```cpp
int a = 1, b = 2;
int& r = a;

r = b;  // assigns value, DOES NOT rebind
```
After this:
* `a == 2`
* `r` still refers to `a`

## RAII

Resource Acquisition Is Initialization

Resources are acquired in a constructor and released in a destructor.

So lifetime of a resource = lifetime of an object.

### Core Idea (Why it exists)

In C++ you manage resources like:
* memory (new)
* file handles
* sockets
* GPU buffers (important for ML)

RAII ensures:
- **Exception Safety**
No leaks even if things fail
- **No manual cleanup**
Cleaner code
- **Deterministic destruction**
Unlike garbage collection

### Mental model

If I acquire something, I must tie it to an object that will clean it up automatically.

### Basic example

Without RAII:
```cpp
void bad() {
    int* p = new int(10);

    // if something throws here → memory leak
    // throw std::runtime_error("error");

    delete p;
}
```
Problem: if exception happens -> `delete` never runs.

With RAII:
```cpp
void good() {
    std::unique_ptr<int> p = std::make_unique<int>(10);

    // if something throws here -> p is destroyed
    // throw std::runtime_error("error");
}
```
No manual delete needed.

### Golden rules 
* Never call new without a RAII wrapper
* **Prefer**:
    * `std::unique_ptr`
    * `std::vector`
    * `std::string`
* Avoid raw pointers unless necessary
