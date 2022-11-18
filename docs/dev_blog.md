# Smartplaylist dev log

## 2022-11-19

* Working on the fastapi `/tracks` endpoint
* Good article on working with fastapi, sqlalchemy, psycopg2, Pydantic and Alembic: <https://www.patrick-muehlbauer.com/articles/fastapi-with-sqlalchemy>
* I am working on [add_search_endpoint](<https://github.com/jkulak/smartplaylist-backend/tree/add_search_endpoint>) branch

## 2022-11-16

* I am trying to use Apache Ignite as database for selecting data, to make `SELECT` queries faster
* The idea is to have Apache Ignite as a layer on top od current Postgres only for selects and to sync date once a day
* I am working on [use_ignite](<https://github.com/jkulak/smartplaylist-backend/tree/use_ignite>) branch
* There is a Python client that seems to be up to date and actively developed: <https://github.com/apache/ignite-python-thin-client>
* There is a acively maintained Docker image: <https://hub.docker.com/r/apacheignite/ignite>
* I was able to start the Apache Ignite server, and load 1_000_000 rows quickly with `load_to_ignite.py`
* Selects where around 4-5s (with no indexes on the table)
* I watched some videos on Apache Ignite
  * <https://www.youtube.com/watch?v=uU3Vb8vZusA> "Apache Ignite w LPP"
  * <https://www.youtube.com/watch?v=fwMRFA7BWTk> "How to Migrate Your Data Schema to Apache Ignite"
* I gave up after not seeing below 1s results out of the box
* Indexes would speeds things up probably
* There is plenty room to improve, but I decided to try to get rid of postgrest - that is probably not optimal for my case
