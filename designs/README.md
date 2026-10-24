# Front V shelving alternatives

Two unbranded **concept designs**, sharing one footprint and tote arrangement:

| Version | FreeCAD model | Preview |
| --- | --- | --- |
| Wire shelves | [Front_V_Wire_Shelves.FCStd](Front_V_Wire_Shelves.FCStd) | [Wire preview](Front_V_Wire_Shelves.png) |
| Standard lumber and plywood | [Front_V_Wood.FCStd](Front_V_Wood.FCStd) | [Wood preview](Front_V_Wood.png) |

[Comparison drawing: plan and loading elevation](Shelving_Comparison.svg)

The original [Trailer.FCStd](../Trailer.FCStd) remains unchanged. Both alternatives
are together on `design/front-v-shelving-options`, rather than separate branches,
so they can be opened side by side.

## Layout

- Three shelf top surfaces: **4, 26, and 46 inches** above the floor.
- Four floor-supported uprights: two nose-side and two loading-side.
- Every shelf has nose-side and loading-side crossbeams, side rails and perimeter
  bearers. The door-side rail follows a dogleg instead of crossing the entry.
- X bracing is at the nose side, behind the totes, not across their loading path.
- Yellow bars on the loading side are **removable travel-restraint placeholders**.
  Release them to remove totes; actual latches, connections and restraint ratings
  have not been designed.
- Target arrangement: **one large tote below, one medium tote in the middle,
  two small totes above**.
- The shelves are V-shaped at the nose and notched beside the side door.
  The opposite side extends into the main trailer. The rear edge is 1080 mm
  (42.5 inches) behind the nose tip, approximately **21 inches beyond the V**.
  The large-tote envelope does not fit wholly inside this shallow V.
- A modeled keepout reserves 610 mm (24 inches) of entry depth from the inside
  door-side wall along the full modeled side-door opening. This is a layout
  allowance, not verification of door swing, egress compliance or accessibility.

### Tote allowances, not verified product dimensions

The requested HDX 27-, 12-, and 7-gallon sizes are targets only. Manufacturer
dimensions could not be verified. These rectangular blocks are deliberately
labeled as **design envelopes**, not accurate product models.

| Target | Across trailer | Fore/aft | Height | Quantity |
| --- | ---: | ---: | ---: | ---: |
| HDX 27-gallon | 800 mm / 31.5 in | 540 mm / 21.3 in | 400 mm / 15.7 in | 1 |
| HDX 12-gallon | 600 mm / 23.6 in | 450 mm / 17.7 in | 355 mm / 14.0 in | 1 |
| HDX 7-gallon | 400 mm / 15.7 in | 520 mm / 20.5 in | 305 mm / 12.0 in | 2 |

Small totes are rotated with their long direction fore/aft. Measure actual
lid/handle-inclusive dimensions before buying totes or cutting material.
The models check complete rectangular envelopes, not just tapered tote bases.

## Material alternatives

### Version 1: wire shelves

- Concept frame: 25.4 mm (1 inch) square steel tube, 1.6 mm wall.
- Custom wire decks: two layers of 4 mm diameter rods on 40 mm centers, clipped
  to the shelf outline, supported by the surrounding frame and crossbeams.
- This is a **custom fabrication concept**, not a ready-made commercial rack.
  Ordinary rectangular wire shelves will not match the nose and door notch.
  A fabricator must specify welds, wire-panel attachment, edge treatment and
  corrosion protection. Cutting an existing commercial shelf may invalidate
  its load rating and is not prescribed here.

### Version 2: standard boards and plywood

- Concept posts and bearers: **38 x 64 mm**, approximately actual dressed
  nominal 2x3 lumber. Verify local stock dimensions.
- Shelf decks: **18 mm plywood**, approximately nominal 3/4 inch; adjust for
  the actual panel thickness.
- Nose-side diagonal braces and concept floor anchor plates are shown.
  Plates indicate anchoring locations, not a specified fastening solution.
- Perimeter bearers and rails meet or overlap as layout solids. Joint cuts,
  brace laps, screws, bolts, gussets, blocking and floor connections still need
  detailing. These are not fabrication-ready joinery or cut-list drawings.

## Model scale and coordinates

The source is one imported mesh, not a dimensioned parametric trailer assembly.
Its coordinates span only about 4.3 document units along the trailer despite
the document using millimeters. The design assumes the imported numbers are
meters and scales them by **1000** into millimeters. Approximately 6 feet of
inside width was confirmed by the owner, but all other physical dimensions
remain unverified. The interpreted wall inner faces are about 1731 mm
(68.2 inches) apart, narrower than the floor mesh.

The normalized coordinates are:

- X: across the trailer, negative on the side-door side.
- Y: from the inside nose tip toward the rear.
- Z: height above the modeled floor.

The original mesh is included, scaled and reoriented, under **Reference** but
hidden to make the rack visible. Toggle **OriginalTrailerReference** to inspect
the complete trailer. The visible nose outline supplies local context.
**ClearanceChecks** contains hidden door-entry and straight-removal volumes.
Toggle individual objects to inspect them.

Shelf, frame, brace and tote features are individually selectable solids.
Parameters are in the generator; changing the descriptive **DesignParameters**
properties in FreeCAD does not automatically regenerate geometry.

## Rebuild and validation

Use the Python bundled with FreeCAD 1.1, not an unrelated Python installation.
From the repository root in PowerShell:

```powershell
& 'C:\Program Files\FreeCAD 1.1\bin\python.exe' .\designs\build_shelving.py --gui
```

The GUI option initializes a separate FreeCAD window to save colors,
visibility, camera views and PNG previews. It does not modify an existing
FreeCAD session. Omit `--gui` for geometry-only validation, but that regenerates
CAD files without the presentation setup.

The generator produces both CAD files, PNG previews, the SVG comparison and
[validation.json](validation.json). It fails on:

- invalid or below-floor rack solids;
- rack/tote intersections and tote/tote intersections;
- totes outside the shelf footprint;
- rack or totes intersecting the modeled door-entry keepout;
- straight tote-removal paths hitting the rack or other totes, with removable
  restraint bars excluded from those path checks;
- less than the nominal 25 mm angled-wall allowance or straight-wall clearance;
- insufficient vertical clearance between tote tops and next-level framing;
- invalid saved solids or changed object counts after saving and reopening;
- changes to the original CAD file, checked by SHA-256.

The complete rectangular tote envelopes can be removed straight toward the rear;
the concept does not depend on tipping totes around posts.

## Before construction

**No load rating or structural approval is claimed.** Verify actual trailer
dimensions, the door opening and swing, actual totes, available stock, joints,
wire deck capacity, local shelf spans, framing, fasteners and restraint hardware.
Floor plates must connect to suitable structure, not merely thin floor or wall
lining. Establish payload and loaded tongue weight with the trailer manufacturer
or a qualified professional: concentrating gear at the front changes tongue load.

The geometry checks are fit checks, not structural analysis. Neither version is
ready to build until these items are resolved.
