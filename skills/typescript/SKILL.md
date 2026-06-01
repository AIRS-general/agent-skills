## `Record<string, any>`

`Record<K, T>` is a utility type used to define an object type with specific key and value types.

`Record<Keys, ValueType>`
- `Keys` -> the type of the object keys
- `ValueType` -> the type of the values

```ts
type UserRoles = Record<string, string>;

const roles: UserRoles = {
  alice: "admin",
  bob: "user",
};
```

## `as`

mainly used for type assertions.

It changes the compile-time type only. It does not change the runtime value.

`value as Type`

### Use cases:
1. DOM Elements
Very common in React/frontend.
```ts
const canvas = document.getElementById("canvas") as HTMLCanvasElement;
```

2. Narrowing unknown
```ts
function handle(data: unknown) {
  const str = data as string;

  console.log(str.toUpperCase());
}
```

3. API response
```ts
type User = {
  id: number;
  name: string;
};

const user = response.data as User;
```
