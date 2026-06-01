## `useCallback`
The useCallback hook in React is used to memoize functions, preventing unnecessary re-creations of the same function on every render. This is particularly useful for optimizing performance in scenarios where functions are passed as props to child components or used as dependencies in other hooks like useEffect.
- When a function is defined inside a component, it is re-created on every render. This can cause performance issues if:
  - The function is passed as a prop to a child component, causing unnecessary re-renders.
  - The function is used as a dependency in useEffect, causing the effect to re-run unnecessarily.
- useCallback solves this by returning a memoized version of the function that only changes when its dependencies change.

```ts
const memoizedCallback = useCallback(callbackFunction, [dependencies]);
```
- `callbackFunction`: The function you want to memoize.
- `dependencies`: An array of values that the function depends on. The function will only be re-created if any of these values change.

## `useRef`

`useRef` is a hook that gives you a mutable object whose value persists across renders without causing re-renders when it changes.

Basic syntax:
```ts
const ref = useRef<T>(initialValue)
```

It returns
```ts
{
  current: initialValue
}
```

Use cases:
1. most common: access DOM elements
```tsx
import { useRef } from "react"

function App(): JSX.Element {
  const inputRef = useRef<HTMLInputElement | null>(null)

  function focusInput(): void {
    inputRef.current?.focus()
  }

  return (
    <>
      <input ref={inputRef} />
      <button onClick={focusInput}>
        Focus
      </button>
    </>
  )
}
```
* React attaches the DOM node to `inputRef.current`
* You can directly call DOM methods like:
  * `.focus()`
  * `.scrollIntoView()`
  * `.play()`

2. Store values without re-rendering
Unlike useState, changing a ref does not trigger a component re-render.
```ts
const countRef = useRef<number>(0)

function handleClick(): void {
  countRef.current += 1
  console.log(countRef.current)
}
```
Good for:
- timers
- websocket instances
- previous values
- cached objects
- mutable flags

3. Persisting objects between renders
Useful for expensive objects or connections.
```ts
const wsRef = useRef<WebSocket | null>(null)

useEffect(() => {
  wsRef.current = new WebSocket("ws://localhost:8080")

  return () => {
    wsRef.current?.close()
  }
}, [])
```

## `useState`

`useState` is a React Hook that lets a functional component store and update state.

Without state, a component only renders static data.
With useState, the component can:
* remember values
* react to user interactions
* trigger re-renders when data changes

Syntax
```ts
const [state, setState] = useState<T>(initialValue)
```
* state → current value
* setState → function to update it
* initialValue → starting value

Example:
```tsx
import { useState } from "react"

function Counter(): JSX.Element {
  const [count, setCount] = useState<number>(0)

  return (
    <div>
      <p>Count: {count}</p>

      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  )
}
```
What happens
1. initial render:
```ts
count = 0
```
2. user clicks button
```
setCount(count + 1)
```
3. react:
* updates the state
* **re-renders** the component
* UI shows new value

`useState` must:
* be called at the top level
* not inside loops or conditions
* only be used in React components or custom hooks

Typical flow
```
User action
   ↓
setState(...)
   ↓
React updates state
   ↓
Component re-renders
   ↓
UI updates
```

## Hooks

a Hook is a **special function** that lets functional components use React features like:
- state
- lifecycle logic
- context
- refs
- side effects
- reusable component logic

A Hook lets React components “hook into” React’s internal features.

## `useEffect`
`useEffect` is a React Hook used to run side effects in functional components.

A side effect is anything that happens outside rendering, such as:
* fetching data
* subscribing to events
* manually updating the DOM
* setting timers
* logging
* WebSocket connections

Basic syntax
```js
useEffect(() => {
  // side effect code
}, [dependencies]);
```
It takes two parts:
1. A function (the effect)
2. A dependency array (controls when it runs)

Example
```tsx
import { useEffect, useState } from "react";

function App() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    console.log("Count changed:", count);
  }, [count]);

  return (
    <button onClick={() => setCount(count + 1)}>
      {count}
    </button>
  );
}
```
What happens:
* component renders
* count changes
* `useEffect` runs again because `count` is in dependencies

When Does `useEffect` Run?
1. After every render (no dependency array)
```ts
useEffect(() => {
  console.log("Runs every render");
});
```
Runs:
- initial render
- every re-render

2. only once
```ts
useEffect(() => {
  console.log("Runs once");
}, []);
```
runs:
- only after first render 

3. when dependency changes
```ts
useEffect(() => {
  console.log("Runs when count changes");
}, [count]);
```
Runs:
- initial render
- every time `count` changes

clean up function
Some effects need cleanup (important for memory leaks).
Example: timer
```ts
useEffect(() => {
  const id = setInterval(() => {
    console.log("tick");
  }, 1000);

  return () => {
    clearInterval(id);
  };
}, []);
```
What happens:
* effect runs → interval starts
* component unmounts → cleanup runs → interval stops

Common use cases:
1. Fetch data
```ts
useEffect(() => {
  async function fetchData() {
    const res = await fetch("https://api.example.com/data");
    const data = await res.json();
    console.log(data);
  }

  fetchData();
}, []);
```

2. Event listeners
```ts
useEffect(() => {
  const handler = () => console.log("resize");

  window.addEventListener("resize", handler);

  return () => {
    window.removeEventListener("resize", handler);
  };
}, []);
```

3. Sync with external systems
Example: WebSocket
```ts
useEffect(() => {
  const ws = new WebSocket("ws://localhost:8080");

  ws.onmessage = (msg) => {
    console.log(msg.data);
  };

  return () => {
    ws.close();
  };
}, []);
```

## TanStack

`@tanstack/react-query`

## Three main x
