# Mock data using `json-server`

UI teams may wish to simulate API calls that do not exist yet.  We accomplish this using `json-server`.

## Install `json-server`

```
$ yarn global add json-server
```

## Add or modify mock data

Modify or create the `ui/mocks/db.json` file with your simulated data.

Example:

```json
{
  "courses": [
    {
      "id": 1,
      "title": "Intro to New Testament",
      "description": "typicode",
      "active": true
    },
    // ...
  ]
}
```

Please do commit useful changes to this file, because the mock data might be useful to others.  On the other hand, please _do not_ commit superfluous changes such as those caused by testing CRUD operations.

## Make the desired API URL go to that JSON key

1. **Configure your dev server to selectively proxy to the `json-server`**.  Do this by making a `ui/mocks/proxy-config.js` file, which will be gitignored so it won't accidentally affect anyone else.

Example:

```js
module.exports = {
  // Map courses-related routes to json-server
  "/api/v1/courses": {
    target: "http://localhost:3000"
  },
  // Send everything else to the real API
  "/api": {
    target: "http://localhost:5000"
  }
};
```

2. **Configure `json-server` routing.**  By default, it will map top-level keys in `db.json` to top-level paths; eg, for the `db.json` above, the courses data would be located at `/courses`.  This doesn't match the routing used in the real API, so we need to change it.  Using the file `ui/mocks/routes.json`, map our URLs to `json-server`'s internal paths.

Example:

```json
{
  "/api/v1/courses/*": "/$1"
}
```

This effectively strips off the `/api/v1/courses/` part so that `json-server` will map those URLs to the correct JSON key.

## Run `json-server`

```
$ json-server db.json --watch --routes routes.json
```

### Optionally simulate latency

The `ui/mocks/latency.js` file is `json-server` middleware that will randomly make requests take longer so you can see how latency affects the UI.  To opt into this, use the `--middlewares` option:

```
$ json-server db.json --watch --routes routes.json --middlewares latency.js
```
