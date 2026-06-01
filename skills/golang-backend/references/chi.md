## Notes for the chi router

### CORS

`github.com/go-chi/cors`

```go
package main

import (
    "net/http"

    "github.com/go-chi/chi/v5"
    "github.com/go-chi/cors"
)

func main() {
    r := chi.NewRouter()

    r.Use(cors.Handler(cors.Options{
        AllowedOrigins: []string{
            "http://localhost:3000",
        },

        AllowedMethods: []string{
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "OPTIONS",
        },

        AllowedHeaders: []string{
            "Accept",
            "Authorization",
            "Content-Type",
        },

        ExposedHeaders: []string{
            "Link",
        },

        AllowCredentials: true,
        MaxAge:           300,
    }))

    r.Get("/", func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte("hello"))
    })

    http.ListenAndServe(":8080", r)
}
```
