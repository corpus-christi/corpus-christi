# Database

This document considers various DB issues for CC.

## CLI

CC extends the Flask command-line interface
with DB-specific commands.
All are subcommands of `data`
Use 
```bash
flask data
```
to show all subcommands.
Most `flask data` commands
use SQLAlchemy ORM methods to do their job.
1. `flask data clear`
   **deletes all data** in the database
   by dropping and then recreating
   all database tables.
1. `flask data create-all` creates all tables
   in the data model. If a table already exists,
   that table is skipped
1. `flask data drop-all` 
   **deletes all tables** from the database
1. `flask data seed`
   stores seed data gleaned from various tests
   into the database.
   Database tables must already exist.
