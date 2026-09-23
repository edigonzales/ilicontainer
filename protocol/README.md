# IBX bridge protocol v1

> The QGIS plugin no longer uses this protocol. It reads containers in-process
> with the pure-Python reader (`qgis/ibx_browser/ibx/`). The Java bridge and its
> protocol remain in the repository for the Java API, the CLI tests and the
> `NavigationTest` acceptance.

Private POST `/v1` on loopback. Every request requires `X-IBX-Token`; the token and
random port are printed once as a JSON startup record by `BridgeMain`. They must
never be stored in QGIS projects. stdin EOF shuts the process down. Request bodies
are JSON, capped at 4 MiB. Errors use HTTP 400 with `error` and `code`; unauthorised
requests receive 403. Clients must not treat an error as a successful empty result.

All operations have `op`; session operations also have `session`. `requestId` is
optional and enables a separate `cancel` request (`target` = request ID). Operations:

| op | Input | Output |
|---|---|---|
| open | source; allowFullDownload=false; immutableUrl=false | session, state, description |
| describe | session | metadata, spatial manifest |
| catalog / baskets | after=null, limit=256 | items, next |
| object | fid **or** tid and optional bid | complete typed object, or null if missing |
| related | fid, after=null, limit=50 | indexed, items, next (only when indexed) |
| query | className, geometry=null, bids=[], optional fids/bbox/fields/noGeometry, limit=256 | items, cursor |
| next | cursor, limit=256 | items, cursor |
| closeCursor | cursor | ok |
| export | fids, target (new local XTF file) | count, target |
| metrics | session | ReadMetrics counters since source open |
| close | session | ok |
| cancel | target | ok |

`bbox` is `{minX,minY,maxX,maxY}` in the source CRS and returns conservative
candidates. The QGIS iterator performs exact filtering when requested. An explicit
empty `fids` list returns no features. `fields` projects transported attributes;
an empty list transports no attributes; absent transports all. `NoGeometry` is applied only after geometry-dependent filters.

Feature rows have `fid`, `tid`, `bid`, `attributes`, `wkb` (base64 ISO-WKB or null).
The full object has `className`, `fid`, `tid`, `bid`, `fields`. `fields` maps names to
ordered arrays of typed values. An absent key, empty array and scalar null remain
distinguishable. Values:

- scalar: `{kind:"scalar", type, value}`; exact lexical numbers stay strings.
- geometry: `{kind:"geometry", descriptor, wkb}`.
- structure: `{kind:"structure", className, tid, fields}`.
- reference: `{kind:"reference", className, tid, bid, order, fields}`. Nested fields
  preserve embedded association details. The reference target is not expanded.

The metadata defines cardinality, LIST/BAG ordering, concrete types, units,
relationships and display labels. Blackbox values are inert scalar text; their
property metadata distinguishes XML and binary content.

`related` retrieves incoming references. Outgoing references remain in the complete
object and are followed with `object(tid,bid)`. A related row carries `sourceFid`,
`path`, `targetTid`, `targetBid`, `order`, and the source `object`. `path` alternates
attribute names and zero-based value positions, e.g. `/Kontrollen/0/Kontrollstelle/0`.
As a result, repeated references are separate edges, not silently deduplicated.
Association sources expose their role links and own attributes as relationship
details, including associations without a TID.

Index cursors are base64url binary keys validated against the query prefix. Feature
cursors are opaque, per session, closed explicitly or expired after 60 seconds of
inactivity. Page size is limited to 256, with at most 128 feature cursors per session.
Access is serialized per session; different sessions can run concurrently. Cache
budget is 32 MiB per container. FIDs are only meaningful within the source and
`state` (writer-generated dataset UUID plus source revision/size). Remote readers additionally pin strong
ETags. Read failures never trigger implicit snapshot downloads or reference closure.

Export accepts 1..20'000 selected FIDs, deduplicates and orders them in container
order, preserves complete original objects and basket context, and atomically
publishes a new file. Existing targets are rejected.
