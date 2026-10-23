# Harbor routing investigation

This is fabricated evidence for testing the sample workflow, not an inspection of a real server.

All addresses use reserved example names. All paths, releases, owners, and observations below are
fictional. These claims exercise the prototype's data model. They do not describe Clark's systems.

## Route

The sample public address `https://harbor.example.test` routes through the sample reverse proxy
on `web-01` to `127.0.0.1:4100`. The sample service is `harbor-web` and release identity is
`release-2026-10-21-a7c91e2`. The example observation time is October 21, 2026, 14:00 UTC.

The September preview observation refers to `https://preview.harbor.example.test` and deployment
`preview-2026-09-20-3f918aa`, on September 20, 2026, 14:00 UTC. It has not been checked again.

## Source

The production release metadata in this fictional scenario is:

```json
{
  "deployment": "release-2026-10-21-a7c91e2",
  "repository": "https://git.example.test/harbor/platform",
  "subdirectory": "apps/site",
  "revision": "a7c91e2d4b6f830159caee847d2f810b3e64f907"
}
```

The older preview uses the same monorepo/subdirectory at revision
`3f918aa674c2180dbb41d27e552c6ab809e0312f`. These are illustrative identifiers.

## Runtime

The sample `harbor-web` service launches `node server.js` from
`/srv/harbor/releases/a7c91e2/apps/site`. This runtime belongs to the same production release
identified in the route and source observations. Its example observation time is October 21,
2026, 14:00 UTC. The preview runtime was observed at `/srv/harbor/preview/3f918aa/apps/site` in September.

## Identity

`web-01` is the fictional runtime host. `harbor/platform` is the fictional active source repo.
The sample laptop checkout is `/workspace/harbor-platform`, and the active app is `apps/site`.
`/workspace/archive/harbor-website` is an earlier prototype; it has no serving relationship to
the public address. The archive is retained because its name caused confusion.

The operating notes in `/workspace/notes/` explain these choices. The map references them and
stores a condensed conclusion; it does not move those notes into itself. The sample observation
time for these identities is October 21, 2026, 14:00 UTC.

## Unknown job

The investigation mentions a nightly metrics job but provides no scheduler, runtime, command,
or deployment evidence. Its card must remain draft. It must not inherit certainty from the website.
