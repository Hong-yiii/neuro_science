# Maze graph hash

Date: 2026-09-01  
Status: authoritative fine graph for exploratory graph/path audit

## Input

```text
docs/geometry/maze_mesh_centroids_1344.txt
geometry sha256: 479f0df501e92e167206248eff2d0a44ba5f26cd62cfcc879dcaad979d7a7e66
```

## Graph rule

```text
schema: maze_graph_1344_4neighbor_v1
node_id: 1-based line number in centroid file
invalid sentinel: 0 is not a node
edge rule: directed cardinal 4-neighbor edge when centroids differ by exactly 0.625 on one axis and 0 on the other
```

Counts:

| Quantity | Value |
| --- | ---: |
| nodes | 1,344 |
| undirected edges | 2,544 |
| directed edges | 5,088 |
| connected components | 1 |

## Hashes

Primary graph hash, including geometry-file path/hash, node coordinates, adjacency rule, and directed edges:

```text
1e7804c5d2167dcd8709a9760d8917034cb60e36e936229fad9056b1dae0f9ad
```

Edge-only hash, compatible with the existing `MazeGraph` contract style that hashes directed edges only:

```text
ab31ee91f615bd4165282e8dd9ab2c4298a4f5285cb76fd3c4aeea38096a4ebb
```

Use the primary graph hash in graph/path audit receipts. Use the edge-only hash only when plugging the edge list into `docs/cebra_pilot/implementation/contracts.py::MazeGraph`.

## Reproducibility note

The canonical primary payload is JSON with sorted keys and compact separators. It includes:

```text
schema, geometry_file, geometry_sha256, node_id, coordinate_units,
adjacency_rule, grid_step, nodes, directed_edges
```

Coordinates are read as decimal strings from the centroid file to avoid float-format drift.
