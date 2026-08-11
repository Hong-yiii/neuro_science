# Spatial-Bin Ordering Verification

Verified: 2026-08-10

## Result

For the current `f1526be5` export, `bins[t][k]` is a **1-based Julia
`Meshes.jl` floor-mesh element index**, not a row-major flattened 40 × 40 grid
index.

The geometry still lies on 40 × 40 lattice centers:

- maze extent: `[-12.5, 12.5] × [-12.5, 12.5]`;
- lattice spacing: `0.625` Unity units;
- nominal full grid: 1,600 cells;
- four 8 × 8 pillar footprints remove 256 cells;
- navigable floor mesh: `1,600 - 256 = 1,344` elements.

The important distinction is ordering:

```text
full-grid ID: row-major position among all 1,600 cells
mesh ID:      Meshes.jl element position among 1,344 navigable patches
```

In the reconstruction, none of the 1,344 mesh IDs numerically equaled its
corresponding full-grid ID. Therefore `divmod(mesh_id - 1, 40)` is invalid.

## Code path

At export commit `38f1684a0bcd1a1a10f149b4a4524a914558a34b-dirty`:

1. `Hippocampus.jl/src/topology.jl::floor_topology3` manually constructs the
   navigable quadrilateral floor around four pillars.
2. It applies `Meshes.refine(..., QuadRefinement())` three times.
3. `Hippocampus.jl/src/replay.jl::JointOccupancy` creates
   `Shadow("xy")(floor_topology3(nrefinements=3))`.
4. `KNearestSearch` assigns each Unity position to a mesh element index.
5. `SpikeCountPerSpatialBin` exports the place component of that joint index.
6. Filtered/invalid samples are written as `0`.

`QuadRefinement` emits child elements grouped by parent element at each
refinement. It does not reorder the result as rows and columns.

## Executed reconstruction

Julia was run in a temporary Docker container using Julia 1.11 and Meshes.jl
0.57.25. The exact export-time `floor_topology3` source was extracted from Git
commit `38f1684`, then refined with `nrefinements=3`.

Observed:

```text
NELEMENTS = 1344
mesh 421  -> centroid ( 2.1875,  8.4375)
mesh 509  -> centroid ( 2.8125,  8.4375)
mesh 1092 -> centroid ( 1.5625,  7.1875)
mesh 1263 -> centroid (-3.4375, -0.3125)
mesh 1342 -> centroid ( 6.5625,  1.5625)
```

The first exported trial provides an independent continuity check:

```text
mesh-centroid transition distance:
  min    = 0.625
  median = 0.625
  max    = 1.3975

incorrect row-major divmod distance:
  min    = 0.625
  median = 1.875
  max    = 23.7582
```

The reconstructed mesh ordering turns almost every consecutive valid transition
into one adjacent 0.625-unit step. Treating the same IDs as row-major creates
implausible jumps across nearly the full 25-unit maze.

## Relationship to the previous student's 40 × 40 code

The previous repository `josephchengyx/Hippocampus_Decoding` used an older
`vmpv.mat` representation with literal row-major IDs from 1 to 1,600:

```python
h = (bin_id - 1) % 40
v = (bin_id - 1) // 40
```

That convention is valid for the older `vmpv.mat` input used in those notebooks.
It is **not** valid for the current `spike_count_per_spatial_bin_f1526be5.jld2`
export. The two formats share the same 40 × 40 geometry but use different ID
orderings.

## Correct conversion

For current mesh ID `i`:

```julia
m = Shadow("xy")(Hippocampus.floor_topology3(; nrefinements=3))
xy = centroid(m[i])
```

After obtaining centroid `(x, y)`, an optional full row-major grid ID is:

```text
column = floor((x + 12.5) / 0.625)
row    = floor((y + 12.5) / 0.625)
grid_id = row * 40 + column + 1
```

## Residual reproducibility caveat

The JLD2 records the Hippocampus commit and dirty patch but not a pinned
`Manifest.toml`, so the exact export-time Meshes.jl version is unknown. The
`floor_topology3` source is unchanged between the export commit and current
checkout, and the trajectory-continuity check strongly supports the reconstructed
ordering. For archival certainty, the lab should export the authoritative
`mesh_id, x, y` lookup or the generation environment's Julia manifest.
