# SQL writing rules

Covers how the SQL itself must be named and formatted, independent of language.

## Naming

- Table names are singular, lowercase `snake_case` (`category`, `book`, `author`), even
  though they hold many rows — not `categories`/`books`/`authors`.
- Join/junction tables are named `<table1>_<table2>` (both singular), e.g. `category_book`.
- If a table name collides with a SQL keyword/operator (e.g. `match`), quote it with backticks
  everywhere it's used — in `CREATE TABLE`, `CREATE INDEX ... ON`, and every query — rather than
  renaming the table.
- The primary key column is always `<singular_table_name>_id` (`category_id`, `category_book_id`,
  `author_id`) — never a bare `id`.
- A foreign key column has the exact same name as the primary key it references (`book.author_id`
  references `author.author_id`), so the referenced table is always obvious from the column name
  alone.
- Indexes are named `idx__<table>__<column>` (double underscores as separators), one index per
  indexed column.

## Tables

- Always use `CREATE TABLE IF NOT EXISTS <name>` instead of `CREATE TABLE <name>`

## Columns

- Primary key: `<table>_id INTEGER PRIMARY KEY AUTOINCREMENT`, always the first column.
- Every table has `created_at DATETIME DEFAULT (datetime('now'))` as its last real column, before
  any table-level constraints. Don't add an `updated_at` column to a table unless the feature
  actually needs update tracking.
- A public/external identifier, when a table needs one, is `<table>_uuid TEXT NOT NULL` (e.g.
  `book_uuid`, `author_uuid`) — only add this to tables that are referenced externally (via
  the API); internal-only tables (`category_book`) don't get one.
- Numeric columns that default to zero when absent are declared `INTEGER DEFAULT 0`, not nullable
  with an app-level default.

## Indexes

- Index every foreign key column — every `REFERENCES` column gets a matching
  `idx__<table>__<column>` index, no exceptions.
- Also index any column that queries filter or sort on directly, even if it's not a foreign key
  (e.g. `end_at`, used for "not yet ended" filtering).
- Always `CREATE INDEX IF NOT EXISTS`, matching `CREATE TABLE IF NOT EXISTS` — every DDL
  statement in this schema is idempotent/rerunnable.

## Formatting

- `CREATE TABLE IF NOT EXISTS <name> (` / one column definition per line, 4-space indented /
  trailing comma on every line except the last / closing `);` on its own line aligned with
  `CREATE TABLE`. Never inline multiple columns on one line.
