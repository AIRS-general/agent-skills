## node:url

`node:url` provides utilities to handle URLs (like http://, file://) as structured objects instead of raw strings.

```ts
import { URL, fileURLToPath } from "node:url";
```

### Common uses

1. Parse a URL
```ts
const myUrl = new URL("https://example.com:8080/path?x=1");

console.log(myUrl.hostname); // "example.com"
console.log(myUrl.pathname); // "/path"
console.log(myUrl.searchParams.get("x")); // "1"
```

2. Modify query params
```ts
const url = new URL("https://example.com");

url.searchParams.set("q", "vite");
console.log(url.toString());
// https://example.com/?q=vite
```

3. Convert file URL to file path (important in Electron)
```ts
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
```

4. Recreate __dirname (ESM pattern)
```ts
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
```
This replaces CommonJS `__dirname`

With tools like Vite and ESM:
* `__dirname` is not available
* you must use `import.meta.url`

## node:path

`node:path` provides utilities to build, normalize, and manipulate file paths across different operating systems.

### Common methods

1. `path.join()` (most used)
```ts
const filePath = path.join("users", "data", "file.txt");
```
* macOS/Linux -> users/data/file.txt
* Windows -> users\data\file.txt

2. `path.resolve()`
```ts
const absPath = path.resolve("data", "file.txt");
```
converts relative paths to absolute paths.

3. `path.basename()`
```ts
const fileName = path.basename("data/file.txt"); // file.txt
```

4. `path.dirname()`
```ts
const dirName = path.dirname("data/file.txt"); // data
```

5. `path.extname()`
```ts
const extName = path.extname("data/file.txt"); // .txt
```
