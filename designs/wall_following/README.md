# Wall-following shelving: old-trailer style

Two **additional** alternatives based on the owner's three old-trailer photos:
wooden uprights, wall-side and aisle-side bearers, long shelves following the
walls, a walk-in center, and shallower shelving immediately ahead of the door.
Both original compact V-rack CAD files remain unchanged.

| Version | FreeCAD model | Preview |
| --- | --- | --- |
| Wood frame with white wire shelves | [Wall_Following_Wire.FCStd](Wall_Following_Wire.FCStd) | [Wire preview](Wall_Following_Wire.png) |
| Wood frame with plywood shelves | [Wall_Following_Plywood.FCStd](Wall_Following_Plywood.FCStd) | [Plywood preview](Wall_Following_Plywood.png) |

[Plan drawing with entry and aisle clearances](Wall_Following_Comparison.svg)

These alternatives are together on `design/wall-following-shelving`. The owner's
local reference photos have not been added to the commit or uploaded.

## What changed from the first two designs

- **Wall-following layout:** the shelves follow both angled V walls and extend
  along the side walls, leaving the center open instead of filling the nose.
- **Shallow near-door shelf:** the door-side V shelf is at most **250 mm
  (9.8 inches) deep** in the straight section immediately ahead of the door.
  Its end is chamfered to **190 mm (7.5 inches)**. These are deck depths;
  bearers and uprights add to the overall frame envelope.
- **No bridge over the door:** the shallow shelf ends before the modeled opening;
  the left wall shelves resume beyond it.
- **Deeper shelves opposite the door:** **590 mm (23.2 inches)** deep, allowing
  the large tote to sit with its long direction along the trailer.
- **Left shelves after the door:** **350 mm (13.8 inches)** deep for smaller
  gear, leaving more aisle space than two full-depth runs.
- **Continuous center aisle:** a **610 mm (24 inch)** wide, 1971.1 mm high
  rectangular volume is checked clear from Y=800 to Y=2800 mm, including posts,
  feet, rails, restraints and braces. This is not an egress-code approval.
- **Floor storage beneath:** shelf top surfaces are now **18, 40, and 60 inches**
  above the floor, inspired by the reference photos, rather than the original
  4/26/46-inch rack. The space below the lowest bearers is approximately
  **14.8 inches with plywood** or **15.2 inches with wire**.
- Runs end **2700 mm (106.3 inches)** behind the inside nose tip; the complete
  trailer reference is available to inspect remaining rear loading space.

## Materials and support

Both alternatives use modeled **38 x 64 mm lumber** (approximately dressed
nominal 2x3), with uprights on the aisle and wall sides. Nose-side, wall-side
and aisle-side bearers plus crossbeams support each level. Wall-side diagonal
braces avoid the tote bays and removal paths.

- **Wire option:** white wire deck panels, modeled as two layers of 4 mm rods
  on 40 mm centers. White removable front-rail concepts echo the closet-style
  shelves in the photos.
- **Plywood option:** 18 mm plywood decks with wooden removable front-rail
  placeholders on the same supporting frame.

The irregular V panels are **custom fabrication concepts**, not a specified
off-the-shelf shelving system. Wire coating, cut edges, panel connections and
capacity need to be specified by a supplier/fabricator. Front rails indicate
restraint locations, not a rated transport restraint system.

The frame solids are layout representations. Intersecting bearers/posts still
need joinery, blocking, gussets or other appropriate connections; they are not
ready-cut joint drawings. Floor plates mark possible anchor locations only.

## Tote arrangement

The layout retains the requested large/middle/small ordering. Examples are on
the deeper side opposite the door; shallower shelves remain available for
general gear. These are **lid/handle-inclusive design allowances**, not verified
HDX product dimensions:

| Shelf | Target | Across trailer | Along trailer | Height | Quantity |
| --- | --- | ---: | ---: | ---: | ---: |
| Bottom | 27 gallon | 540 mm | 800 mm | 400 mm | 1 |
| Middle | 12 gallon | 450 mm | 600 mm | 355 mm | 1 |
| Top | 7 gallon | 400 mm | 520 mm | 305 mm | 2 |

The large and medium tote blocks are rotated relative to the first designs.
Top totes are in separate bays between uprights. The full blocks can slide
sideways into the center aisle after the relevant front rail is removed.
This check does not establish a complete handling route through the side door;
large totes may need to leave through the rear loading opening.

## Viewing in FreeCAD

Open either model to see a saved upright perspective with tote allowances.
The wire panels and plywood panels are grouped as three shelf features, with
individual frame components in **Rack**.

- **OriginalTrailerReference**, under **Reference**, contains the complete
  original trailer mesh, scaled/reoriented and hidden by default.
- **SideDoorKeepout**, **CentralAisle**, and **RemovalPath** objects under
  **ClearanceChecks** are hidden by default; toggle them to inspect the layout.
- **DesignParameters** records dimensions and assumptions. These are descriptive
  properties; edit the generator and rebuild to change the geometry.

The original imported mesh still uses the 1000x scale interpretation described
in the [original design guide](../README.md#model-scale-and-coordinates).
Only approximately 6 feet of inside width has been confirmed. Physical
measurement of the door, walls, roof and actual totes remains necessary.

## Regeneration and checks

From the repository root, using FreeCAD 1.1's bundled Python:

```powershell
& 'C:\Program Files\FreeCAD 1.1\bin\python.exe' .\designs\build_wall_shelving.py --gui
```

This regenerates only the two wall-following models, their previews, the plan
and [validation.json](validation.json). SHA-256 checks ensure that the source
trailer and the two original CAD alternatives are unchanged.

Validation checks actual geometric slices for the **250/350/590 mm shelf
depths**, valid rack solids, floor/roof and wall clearances, tote support
footprints, tote/frame and tote/tote intersections, connected door/aisle
keepouts, a clear 610 mm central aisle, and sideways removal paths with the
front rails released. Each CAD file is saved, reopened and checked again,
including presentation visibility and saved camera orientation.

## Before construction

**Concept only; no load rating or construction approval.** Verify the physical
dimensions, actual tote sizes, all joints, wire/plywood capacity, shelf spans,
framing and anchorage, removable restraints, door swing, headroom and walking
clearances. Secure the rack to verified structure, not just the wall lining.
Establish payload distribution and tongue weight with the trailer manufacturer
or a qualified professional. The fit checks are not a structural calculation
or an assessment of egress/accessibility compliance.
