# Common PostgreSQL commands

## Connection and session

```bash
psql -U username -d dbname          # connect to database
psql database_url                  # connect to database using URL
```

```sql
\conninfo                          # show current connection info
\c dbname                          # switch database
\q                                 # quit psql
```

## Database operations
```sql
\l
```

## Tables & schema
```sql
\dt                                -- list tables
\d tablename                       -- describe table
\d+ tablename                      -- detailed table info
\dn                                -- list schemas
\df                                -- list functions
```

## Handy shortcuts
```sql
\?
\h
```
