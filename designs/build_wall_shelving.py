"""Photo-inspired wood-frame shelving; run with FreeCAD's bundled Python."""

import hashlib
import json
import sys
import xml.etree.ElementTree as ET

import FreeCAD as App
import Part

from build_shelving import (
    COLORS, DOOR_Y, INCH, OUT, ROOT, box, feature, member, original_reference,
    overlap, polygon, save_model, slab, tote, wire_deck,
)


DEST = OUT / "wall_following"
LEVELS = (18 * INCH, 40 * INCH, 60 * INCH)
LEFT_NOSE = (
    (0, 160), (-145, 160), (-820, 560), (-820, 720),
    (-630, 720), (-570, 660), (-570, 640), (-55, 335), (0, 335),
)
RIGHT_RUN = (
    (0, 160), (145, 160), (810, 580), (810, 2700),
    (220, 2700), (220, 800), (60, 400), (0, 335),
)
LEFT_AFT = ((-820, 1780), (-470, 1780), (-470, 2700), (-820, 2700))
REGIONS = (LEFT_NOSE, RIGHT_RUN, LEFT_AFT)
POST_PAIRS = (
    ((-252, 440), (-520, 440)),
    ((-590, 680), (-790, 680)),
    ((110, 530), (650, 600)),
    ((238, 850), (780, 850)),
    ((238, 1900), (780, 1900)),
    ((238, 2660), (780, 2660)),
    ((-488, 1820), (-790, 1820)),
    ((-488, 2660), (-790, 2660)),
)
WHITE = (0.92, 0.94, 0.95)
AISLE = (-425, 800, 610, 2000)


def footprint(bottom=0, thickness=1):
    parts = [slab(points, bottom, thickness) for points in REGIONS]
    return parts[0].fuse(parts[1]).fuse(parts[2]).removeSplitter()


def build(wire):
    name = "Wall_Following_" + ("Wire" if wire else "Plywood")
    doc = App.newDocument(name)
    doc.Label = "Old trailer style - " + ("wood frame / white wire" if wire else "wood / plywood")
    for group in ("Reference", "Rack", "ToteEnvelopes", "ClearanceChecks"):
        doc.addObject("App::DocumentObjectGroup", group)
    original_reference(doc, doc.Reference)
    parameters = doc.addObject("App::FeaturePython", "DesignParameters")
    for prop, value in (
        ("Layout", "Wall-following V and side runs; open center; door opening unbridged"),
        ("ReferenceStyle", "Owner photos: wood posts, wall-side cleats, shallow white wire shelves"),
        ("Frame", "38 x 64 mm lumber, including aisle-side uprights and wall-side uprights"),
        ("Deck", "Custom white wire panels" if wire else "18 mm plywood"),
        ("SourceScale", "1000x source mesh; approximate width only confirmed"),
        ("Totes", "27/12/7 gallon targets; dimensions are allowances, NOT verified products"),
        ("Construction", "Concept only: no load rating; joints, anchors and gates unspecified"),
    ):
        parameters.addProperty("App::PropertyString", prop, "Design")
        setattr(parameters, prop, value)
    for prop, value in (
        ("ShallowDoorSideDepth", 250), ("LeftAftDepth", 350),
        ("RightRunDepth", 590), ("CheckedAisleWidth", 610),
        ("Shelf1Top", LEVELS[0]), ("Shelf2Top", LEVELS[1]), ("Shelf3Top", LEVELS[2]),
    ):
        parameters.addProperty("App::PropertyLength", prop, "Design")
        setattr(parameters, prop, value)

    all_posts = [p for pair in POST_PAIRS for p in pair] + [(0, 230)]
    for index, (x, y) in enumerate(all_posts, 1):
        feature(doc, doc.Rack, "Post%d" % index, "Wood upright %d" % index,
                box(x - 19, y - 32, 3, 38, 64, 1947), COLORS["wood"])
        feature(doc, doc.Rack, "Foot%d" % index, "Concept floor anchor %d" % index,
                box(x - 40, y - 40, 0, 80, 80, 3), COLORS["metal"])

    thickness = 8 if wire else 18
    for index, top in enumerate(LEVELS, 1):
        decks = [
            wire_deck(top, points) if wire else slab(points, top - thickness, thickness)
            for points in REGIONS
        ]
        feature(doc, doc.Rack, "Shelf%d" % index,
                ("White wire" if wire else "Plywood") + " wall-following decks %d" % index,
                Part.makeCompound(decks), WHITE if wire else COLORS["wood"])
        rail_z = top - thickness - 32
        for region_index, points in enumerate(REGIONS):
            for edge, (a, b) in enumerate(zip(points, points[1:] + points[:1])):
                if a[0] == b[0] == 0:
                    continue
                feature(doc, doc.Rack, "Bearer%d_%d_%d" % (index, region_index, edge),
                        "Aisle/wall perimeter support - level %d" % index,
                        member((*a, rail_z), (*b, rail_z), 38, 64), COLORS["wood"])
        for pair_index, (a, b) in enumerate(POST_PAIRS):
            feature(doc, doc.Rack, "Crossbeam%d_%d" % (index, pair_index),
                    "Aisle-to-wall crossbeam - level %d" % index,
                    member((*a, rail_z), (*b, rail_z), 38, 64), COLORS["wood"])
        for gate, (x, y, length) in enumerate(((228, 890, 960), (228, 1940, 660),
                                               (-478, 1860, 740))):
            shape = box(x - 4, y, top + 35, 8, length, 35)
            if wire:
                pieces = [
                    Part.makeCylinder(3, length, App.Vector(x, y, top + z),
                                      App.Vector(0, 1, 0)) for z in (12, 70)
                ]
                pieces.extend(
                    Part.makeCylinder(2, 58, App.Vector(x, yy, top + 12))
                    for yy in range(y, y + length + 1, 40)
                )
                shape = Part.makeCompound(pieces)
            feature(doc, doc.Rack, "TravelRestraint%d_%d" % (index, gate),
                    "REMOVABLE front rail - attachment/rating TBD", shape,
                    WHITE if wire else COLORS["wood"])

    for index, (a, b) in enumerate((((824, 870, 150), (824, 1850, 1890)),
                                  ((-805, 1840, 150), (-805, 2630, 1890))), 1):
        feature(doc, doc.Rack, "WallBrace%d" % index,
                "Wall-side wood diagonal %d - connect to verified framing" % index,
                member(a, b, 20, 12), COLORS["wood"])

    totes = [
        tote(doc, doc.ToteEnvelopes, "HDX_27gal_TARGET", (540, 800, 400),
             260, 1040, LEVELS[0]),
        tote(doc, doc.ToteEnvelopes, "HDX_12gal_TARGET", (450, 600, 355),
             300, 1120, LEVELS[1]),
        tote(doc, doc.ToteEnvelopes, "HDX_7gal_TARGET_Front", (400, 520, 305),
             300, 950, LEVELS[2]),
        tote(doc, doc.ToteEnvelopes, "HDX_7gal_TARGET_Aft", (400, 520, 305),
             300, 2000, LEVELS[2]),
    ]
    door = feature(doc, doc.ClearanceChecks, "SideDoorKeepout",
                   "Side-door opening + 610 mm inward entry depth; swing unverified",
                   box(-950, DOOR_Y, 0, 689, 922.087, 1971.1), (1.0, .15, .1), 85)
    x, y, width, length = AISLE
    aisle = feature(doc, doc.ClearanceChecks, "CentralAisle",
                    "610 mm continuous clear aisle from Y800 through shelf ends",
                    box(x, y, 0, width, length, 1971.1), (.1, .8, .3), 90)
    paths = []
    for index, obj in enumerate(totes, 1):
        bb = obj.Shape.BoundBox
        paths.append(feature(
            doc, doc.ClearanceChecks, "RemovalPath%d" % index,
            "Slide into aisle - remove front rail first",
            box(-400, bb.YMin, bb.ZMin, bb.XMax + 400, bb.YLength, bb.ZLength),
            (.1, .8, .3), 90,
        ))
    shell_plan = (
        (0, 0), (860.155, 550.482), (860.155, 2900),
        (-871.281, 2900), (-871.281, 526.978), (0, 0),
    )
    feature(doc, doc.Reference, "NoseOutline", "Trailer outline - local context",
            polygon(shell_plan), (.3, .3, .3))
    for obj in doc.ClearanceChecks.Group:
        if obj.ViewObject:
            obj.ViewObject.Visibility = False
    doc.recompute()
    report = validate(doc, totes, door, aisle, paths, thickness)
    save_model(doc, DEST / (name + ".FCStd"))
    report.update(file=name + ".FCStd", saved_and_reopened=True)
    return report


def validate(doc, totes, door, aisle, paths, thickness):
    supported_region = footprint()
    shallow_slice = slab(LEFT_NOSE, 0, 1).common(box(-1000, 640, 0, 1000, 20, 1))
    right_slice = supported_region.common(box(0, 1800, 0, 1000, 50, 1))
    left_slice = supported_region.common(box(-1000, 1800, 0, 1000, 50, 1))
    shallow_depth = shallow_slice.BoundBox.XLength
    right_depth = right_slice.BoundBox.XLength
    left_depth = left_slice.BoundBox.XLength
    assert abs(shallow_depth - 250) < .01
    assert abs(left_depth - 350) < .01
    assert abs(right_depth - 590) < .01
    for obj in doc.Rack.Group:
        assert obj.Shape.isValid() and obj.Shape.Volume > 0, obj.Name
        assert obj.Shape.BoundBox.ZMin >= -0.01, "Below floor: " + obj.Name
        for volume in (door, aisle):
            assert overlap(obj.Shape, volume.Shape) < .01, (
                "Walking interference: " + obj.Name + " / " + volume.Name)
    for obj in list(doc.Rack.Group) + totes:
        for vertex in obj.Shape.Vertexes:
            x, y = vertex.Point.x, vertex.Point.y
            assert y >= .604834 * (-x) + 25, "Left nose wall: " + obj.Name
            assert y >= .639962 * x + 25, "Right nose wall: " + obj.Name
            assert -846.281 <= x <= 835.155, "Side wall: " + obj.Name
        assert obj.Shape.BoundBox.ZMax < 2037.6, "Ceiling: " + obj.Name
    for index, obj in enumerate(totes):
        bb = obj.Shape.BoundBox
        base = box(bb.XMin, bb.YMin, 0, bb.XLength, bb.YLength, 1)
        assert abs(base.common(supported_region).Volume - base.Volume) < .01, "Tote off shelf"
        for zone in (door, aisle):
            assert overlap(obj.Shape, zone.Shape) < .01, "Tote blocks walking zone"
        for part in doc.Rack.Group:
            assert overlap(obj.Shape, part.Shape) < .01, (
                "Tote interference: " + obj.Name + " / " + part.Name)
            if not part.Name.startswith("TravelRestraint"):
                assert overlap(paths[index].Shape, part.Shape) < .01, (
                    "Removal interference: " + obj.Name + " / " + part.Name)
        for other_index, other in enumerate(totes):
            if index != other_index:
                assert overlap(obj.Shape, other.Shape) < .01, "Totes overlap"
                assert overlap(paths[index].Shape, other.Shape) < .01, "Removal hits tote"
    assert shallow_depth < left_depth < right_depth
    assert 720 + 19 < DOOR_Y
    assert min((LEVELS[1] - thickness - 64) - (LEVELS[0] + 400),
               (LEVELS[2] - thickness - 64) - (LEVELS[1] + 355)) >= 50
    assert overlap(door.Shape, aisle.Shape) > 0, "Entry and aisle must connect"
    return {
        "rack_components": len(doc.Rack.Group),
        "shelf_top_heights_mm": list(LEVELS),
        "door_side_shelf_max_depth_mm": shallow_depth,
        "door_side_chamfered_tip_depth_mm": 190,
        "left_aft_shelf_depth_mm": left_depth,
        "right_shelf_depth_mm": right_depth,
        "clear_height_below_lowest_bearers_mm": LEVELS[0] - thickness - 64,
        "continuous_checked_aisle_width_mm": 610,
        "checked_aisle_y_range_mm": [800, 2800],
        "door_entry_depth_mm": 610,
        "tote_envelopes": 4,
        "invalid_shapes": 0,
        "tote_rack_interferences": 0,
        "walking_zone_interferences": 0,
        "removal_interferences_with_front_rails_released": 0,
        "limitations": [
            "Unverified actual tote dimensions and trailer dimensions",
            "No structural rating, joint design or approved anchorage",
            "No verification of door swing, egress compliance or tongue weight",
        ],
    }


def drawing():
    ns = "http://www.w3.org/2000/svg"
    ET.register_namespace("", ns)
    root = ET.Element("{" + ns + "}svg", {
        "width": "1100", "height": "1100", "viewBox": "0 0 1100 1100",
        "role": "img", "aria-label": "Wall-following shelves with shallow door-side nose shelf",
    })

    def item(tag, **attrs):
        return ET.SubElement(root, "{" + ns + "}" + tag, {k: str(v) for k, v in attrs.items()})

    def text(x, y, value, size=18):
        node = item("text", x=x, y=y, fill="#18232c",
                    **{"font-family": "sans-serif", "font-size": size})
        node.text = value

    def points(outline):
        return " ".join("%.1f,%.1f" % (370 + x * .27, 130 + y * .27)
                        for x, y in outline)

    item("rect", x=0, y=0, width=1100, height=1100, fill="white")
    text(35, 42, "OLD-TRAILER STYLE - WOOD FRAME / WIRE OR PLYWOOD", 23)
    text(35, 76, "Same layout for both versions. Plan view; nose at top. Dimensions in mm.", 17)
    shell = ((0, 0), (860, 550), (860, 2900), (-871, 2900), (-871, 527), (0, 0))
    item("polyline", points=points(shell), fill="none", stroke="#333",
         **{"stroke-width": 3})
    for region in REGIONS:
        item("polygon", points=points(region), fill="#d4b18a", stroke="#654628",
             **{"stroke-width": 2})
    for x, y in (p for pair in POST_PAIRS for p in pair):
        item("rect", x=370 + x * .27 - 4, y=130 + y * .27 - 4, width=8, height=8,
             fill="#603e24")
    item("rect", x=370 - 950 * .27, y=130 + DOOR_Y * .27,
         width=689 * .27, height=922.087 * .27, fill="#fdd",
         **{"fill-opacity": .7, "stroke": "#b33", "stroke-dasharray": "5 4"})
    item("rect", x=370 - 425 * .27, y=130 + 800 * .27, width=610 * .27,
         height=2000 * .27, fill="#d9f1dc", stroke="#398052",
         **{"fill-opacity": .7, "stroke-dasharray": "5 4"})
    item("rect", x=370 + 260 * .27, y=130 + 1040 * .27,
         width=540 * .27, height=800 * .27, fill="#f3d254", stroke="#665417")
    text(449, 535, "27 gal", 16)
    text(288, 710, "610 clear", 15)
    text(665, 180, "Three shelves:", 19)
    text(665, 212, '18", 40", 60" above floor', 18)
    text(665, 270, "Near-door V shelf:", 19)
    text(665, 302, "250 max depth; tip 190", 18)
    text(665, 334, "Ends before door opening", 17)
    text(665, 400, "Other side:", 19)
    text(665, 432, "590 deep for large totes", 18)
    text(665, 494, "After-door left shelves:", 19)
    text(665, 526, "350 deep for small gear", 18)
    text(665, 590, "Green: checked center aisle", 17)
    text(665, 622, "Red: door-entry keepout", 17)
    text(665, 686, "Yellow: large-tote allowance", 17)
    text(665, 718, "Not verified HDX dimensions", 17)
    text(35, 986, "Wire option: white wire decks and removable front rails on wooden uprights and bearers.", 17)
    text(35, 1018, "Plywood option: 18 mm decks on the same 38 x 64 mm wood frame.", 17)
    text(35, 1062, "CONCEPT ONLY: verify measurements, totes, joints, anchors, load capacity and door swing.", 17)
    ET.ElementTree(root).write(DEST / "Wall_Following_Comparison.svg",
                               encoding="utf-8", xml_declaration=True)


def main():
    DEST.mkdir(exist_ok=True)
    protected = [ROOT / "Trailer.FCStd", OUT / "Front_V_Wire_Shelves.FCStd",
                 OUT / "Front_V_Wood.FCStd"]
    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected}
    reports = [build(True), build(False)]
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected}
    assert before == after, "Original models changed"
    drawing()
    result = {"existing_models_unchanged": True, "existing_model_sha256": before,
              "designs": reports}
    (DEST / "validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if "--gui" in sys.argv:
        import FreeCADGui as Gui

        Gui.showMainWindow()
        Gui.activateWorkbench("PartWorkbench")
    main()
