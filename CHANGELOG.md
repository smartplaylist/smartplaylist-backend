# Changelog

Sections by date, newest first. Entries above `### Internal` are what somebody
using smartplaylist.me can notice; everything below it is for whoever works on
the code.

## 2026-10-18

### Internal

- **Worker publish failures leave source messages retryable.** Broker errors
  escape the database error handler, and redeliveries retry downstream
  publishing when a database write succeeded before the first publish failed. (#40)

## 2026-10-17

- **A malformed search filter is answered with 400, not a server error.** The
  API validates every range, the key and the release date the website sends, and
  says which one it could not read. (#38)
- **Saving a playlist checks the request before calling Spotify.** An empty track
  list or a missing access token is refused with 422 instead of failing halfway.
  (#38)

### Internal

- **Followed artists are inserted in one statement.** `sync_followed_artists.py`
  queues only the artists that were actually new. (#38)
- **API validation has unit tests** that run inside the API image with the
  standard library: `pipenv run python -m unittest discover -s tests -t .` (#38)
- **Ruff configuration** in `.ruff.toml`. (#38)
- **Deployment README says where production runs** and how to check it. (#38)
