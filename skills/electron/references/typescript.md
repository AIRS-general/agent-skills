## ES Modules

The official JavaScript standard for organizing and sharing code between files using import and export.

- A module system that allows for dynamic loading of modules at runtime.
- Enables code splitting and lazy loading of modules.
- Improves performance and user experience by reducing initial load times.

## process

`process` is a global object that represents **the current Node.js runtime instance**, exposing environment info, system details, and lifecycle controls.

No import needed — it’s globally available in Node environments (including Electron main/preload).

```ts
console.log(process.platform);
console.log(process.pid);
```

### What process gives you?

1. Environment variables
```ts
const env: string | undefined = process.env.NODE_ENV;
```

2. Platform info
```ts
if (process.platform === "darwin") {
  // macOS-specific logic
}
```
* "darwin" -> macOS
* "win32" -> Windows
* "linux" -> Linux

3. Current working directory
```ts
const cwd: string = process.cwd();
```

4. Process ID (PID)
```ts
const pid: number = process.pid;
```

5. Exit process
```ts
process.exit(0);
```

6. Events (lifecycle controls)
```ts
process.on("exit", (code: number) => {
  console.log("Exiting with code:", code);
});
```

## import

`import.meta.url` is a special property that gives you the URL of the current module (file). looks like this: `file:///Users/path/to/file.ts`
