# Maze Geometry Metadata

Status: authoritative for the current graph/path formalization, per Hongyi 2026-09-01.

## Centroid map

```text
maze_mesh_centroids_1344.txt
sha256: 479f0df501e92e167206248eff2d0a44ba5f26cd62cfcc879dcaad979d7a7e66
```

Interpretation:

```text
line number 1..1344 = mesh node/bin id
line value          = Unity-space centroid `(axis1, axis2)`
0                   = invalid/unmapped sentinel, not a location
```

Observed structure:

| Quantity | Value |
| --- | ---: |
| nodes | 1,344 |
| unique coordinates | 1,344 |
| axis range | `-12.1875` to `12.1875` |
| grid step | `0.625` |
| missing cells from 40 x 40 | 256 = four 8 x 8 pillars |

Primary adjacency for path formalization is cardinal 4-neighbor adjacency between
centroids exactly one grid step apart. That gives one connected navigable graph
with 2,544 undirected edges, or 5,088 directed edges.

Primary graph hash, including node coordinates, geometry-file hash, construction
rule, and directed edges:

```text
1e7804c5d2167dcd8709a9760d8917034cb60e36e936229fad9056b1dae0f9ad
```

Edge-only `MazeGraph`-style hash:

```text
ab31ee91f615bd4165282e8dd9ab2c4298a4f5285cb76fd3c4aeea38096a4ebb
```

Receipt: `notes/data_inspection/maze_graph_hash_20260901.md`.

Do not use row-major `divmod(bin_id - 1, 40)` for these IDs. The IDs follow the
Meshes.jl element order verified in `notes/data_inspection/spatial_bin_ordering.md`.
