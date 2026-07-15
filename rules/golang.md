# Golang project rules

> Opinionated defaults for my own Go stack (go-pkg-base, BetterStack, cobra, testify/go-cmp).
> These are not generic Go community best practices — they assume this specific toolchain.
> Fork or edit before using them in a project that doesn't share it.

## Project structure

- The project structure must respect the [project layout](https://github.com/golang-standards/project-layout) recommanded standards

## Imports

- In the code, imports must sorted this way: the standard library, an empty line, the local packages (from `internal`, or `pkg` for code meant to be shared/imported externally) if any, an empty line, the external packages
- This grouping is a review convention, not currently enforced by tooling (no `gci`/`goimports -local` config) — apply it by hand unless such a config is added to the project

Ex:
```go
import (
  "fmt"
  "strings"

  "myapp/internal/mypackage1"

  "github.com/org/repo1"
  "github.com/org/repo2"
)
```

## Dependencies restrictions

- All code must be done as much as possible with the standard library
- When a dependency is needed, ask me before and explain me why it is needed over the standard library
- Exception: libraries already named elsewhere in this document (go-pkg-base, cobra, testify, go-cmp) are pre-approved — the ask-first rule only applies to anything not already named here

## Command line arguments

- The standard `flag` package is always prefered when dealing with command line arguments
- Whenever it is required, for example when there are commands along side arguments, use https://github.com/spf13/cobra 

## Config management

- A collection of helpers from https://github.com/pierre-lecocq/go-pkg-base/config must be used to implement the config management
- A `.env` file based config is always prefered
- A `-env` flag must be passed to the binary with the path of the `.env file`. Fail to start if empty.
- Always validate the presence of keys used in the code via `os.Getenv()`. Fail to start if empty.

## Logging

- A collection of helpers from https://github.com/pierre-lecocq/go-pkg-base/logger must be used to implement the logger
- Whenever the BETTERSTACK env variables are set, prefer the BETTERSTACK logger, otherwise, stick to the slog implementation in the `go-pkg-base/logger` package
- Always include the `err` object when logging an error. Ex: `slog.Error("action that failed", "error", err)`

## REST API implementation

- HTTP layer implementation must rely on `net/http`
- A collection of helpers from https://github.com/pierre-lecocq/go-pkg-base/ must be used to implement the server, the response, ... etc
- Always prefer JSON responses, except when explicitely asked

- The architecture must rely on simple layers:
  - The router will call then handlers, implemented in `internal/handlers`
    - role: get parameters from URL/path/body, call services and send a valid or error JSON response to the client
    - handlers must remain as simple as possible
  - the handlers will call the services, implemented in `internal/services`
    - role: validate input, call models via a direct DB connection or a transaction when several models are involved and require data consistency
    - services must return [data, code, error] so the handler can answer with the most precise HTTP code and message
  - the services will call the models for direct database reading or writing operations
    - models return [data, error]. If data and error are nil, operation is a success and may result in a "No Content" response
  - the services will also manage cache access whenever it is implemented, along side database access

- REST API must always be documented in a `docs/openapi.yml` file generated from the code, respecting the latest OpenAPI spec

- The context from the http request must be propagated in all underlying layers (services, models, go routines, ... etc) so it can stop the action whever the request reaches a timeout or is stopped

## Database and models

- A collection of helpers from https://github.com/pierre-lecocq/go-pkg-base/database must be used to implement the database connection and transaction management
- A `DB_DSN` env variable must determine the database DSN. Use in-memory database during unit tests
- No ORM, data mapper, or any packages alike are allowed for model, data and database management
- Raw SQL is the only solution, nicely formatted on several lines
- Prepared statements are mandatory
- Do not use nullable SQL types (`sql.Null*`) or `NULL`-able database columns. Only use standard types with `NOT NULL` and a viable default, falling back to `COALESCE` in SQL queries when needed. This does not forbid Go-level pointer fields (e.g. `*time.Time`) used to represent "not provided" in partial-update payloads — that's a Go-side concern, not a database one.
- Table, column, and index naming conventions are covered separately in [`sql.md`](./sql.md)

### Examples

Collection:

```go
func List(ctx context.Context, conn *sql.DB) ([]*MyObject, error) {
	objs := []*MyObject{}

	fields := []string{
		"field1",
		"field2",
	}

	query := fmt.Sprintf(
		"SELECT %s FROM table_name ORDER BY field1 ASC",
		strings.Join(fields, ", "),
	)

	rows, err := conn.QueryContext(ctx, query)

	if err != nil {
		return nil, err
	}

	defer rows.Close() // nolint:errcheck

	for rows.Next() {
		var obj MyObject

		err := rows.Scan(
			&obj.Field1,
			&obj.Field2,
		)

		if err != nil {
			return nil, err
		}

		objs = append(objs, &obj)
	}

	if err := rows.Err(); err != nil {
		return nil, err
	}

	return objs, nil
}
```

Individual item:

```go
func FindByID(ctx context.Context, db *sql.DB, ID int) (*MyObject, error) {
	var obj MyObject

	fields := []string{
		"field1",
		"field2",
	}

	query := fmt.Sprintf(
		"SELECT %s FROM table_name WHERE id = ?",
		strings.Join(fields, ", "),
	)
	row := db.QueryRowContext(ctx, query, ID)

	if err := row.Scan(
		&obj.field1,
		&obj.field2,
	); err != nil {
		return nil, err
	}

	return &obj, nil
}
```

Create:

```go
func Create(ctx context.Context, db database.DBTx, obj *MyObject) (*MyObject, error) {
	fields := []string{
		"field1",
		"field2",
	}

	query := fmt.Sprintf(
		"INSERT INTO table_name (%s) VALUES (%s)",
		strings.Join(fields, ", "),
		strings.Join(slices.Repeat([]string{"?"}, len(fields)), ", "),
	)

	result, err := db.ExecContext(ctx, query,
		obj.field1,
		obj.field2,
	)
	if err != nil {
		return nil, err
	}

	lastInsertID, err := result.LastInsertId()
	if err != nil {
		return nil, err
	}

	obj.ID = int(lastInsertID)

	return obj, nil
}
```

Update:

```go
func (obj *MyObject) Update(ctx context.Context, db database.DBTx, data *MyObject) error {
	newObj := *obj

	var fields []string
	var values []any

	if data.Field1 != "" && data.Field1 != obj.Field1 {
		fields = append(fields, "field1=?")
		values = append(values, data.Field1)
		newObj.Field1 = data.Field1
	}

	if data.Field2 != "" && data.Field2 != obj.Field2 {
		fields = append(fields, "field2=?")
		values = append(values, data.Field2)
		newObj.Field2 = data.Field2
	}

	if len(fields) == 0 {
		return fmt.Errorf("no data to update")
	}

	values = append(values, obj.ID)

	query := fmt.Sprintf(
		"UPDATE table_name SET %s WHERE id = ?",
		strings.Join(fields, ", "),
	)

	_, err := db.ExecContext(ctx, query, values...)
	if err != nil {
		return err
	}

	*obj = newObj

	return nil
}
```

## Testing

- All code must be unit tested. Produce a coverage report with `go test -coverprofile=coverage.out ./...` followed by `go tool cover -func=coverage.out` (no fixed minimum percentage is mandated)
- Unit tests must be done with the standard library as much as possible. The only accepted dependencies for the moment are:
  - https://github.com/google/go-cmp
  - https://github.com/stretchr/testify
- Use table-driven subtests (a slice of cases run via `t.Run`) directly in the go test code
- When a database is required to unit test the code, use a SQLite in-memory database
- When shared code is needed in the tests, create a `internal/testing/` and put go files in it to be used in `_test.go` files.
  - Do not unit test code in `internal/testing/`
- Use `net/http/httptest` to test API endpoints

## Quality testing

- All code must be tested with `go test`
- All code format must be tested against `gofmt`
- All code must be linted via `golangci-lint`
- Vulnerabilities must be checked with `golang.org/x/vuln/cmd/govulncheck@latest`
- Deadcode must be spotted with `golang.org/x/tools/cmd/deadcode@latest`

## Development environment

- During development, use `https://github.com/air-verse/air` when needed
