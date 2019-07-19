Itinerum Database Migrations
############################

The directory inherits the state of the production database as of 2019-07-18. In lieu of any control system, this directory contains the PostgreSQL database as numbered .sql files to be run in order directly within psql.

## Setting up a new database
1. Create the new database
```bash
$ createdb itinerum
```

2. Perform migrations on the new database
```bash
$ psql itinerum
# \i up/1-itinerum.sql
  ...
# \i up/n-itinerum.sql
```
