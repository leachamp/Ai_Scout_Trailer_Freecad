"""Run with the Python executable bundled with FreeCAD 1.1."""

import hashlib
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import FreeCAD as App
import Mesh
import Part


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "designs"
INCH = 25.4
LEVELS = (4 * INCH, 26 * INCH, 46 * INCH)
OUTLINE = (
    (-145, 160), (145, 160), (810, 580), (810, 1080),
    (-230, 1080), (-230, 720), (-820, 720), (-820, 560),
)
POSTS = ((-480, 420), (480, 420), (-210, 1040), (760, 1040))
NOSE = ((0, 0), (860.155, 550.482), (860.155, 1300),
        (-871.281, 1300), (-871.281, 526.978), (0, 0))
DOOR_Y = 771.777
COLORS = {
    "wood": (0.72, 0.49, 0.25),
    "metal": (0.62, 0.66, 0.70),
    "tote": (0.18, 0.21, 0.25),
    "lid": (0.95, 0.78, 0.08),
}


def polygon(points, z=0):
    vertices = [App.Vector(x, y, z) for x, y in points]
    return Part.makePolygon(vertices + [vertices[0]])


def slab(points, bottom, thickness):
    return Part.Face(polygon(points, bottom)).extrude(App.Vector(0, 0, thickness))


def box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, App.Vector(x, y, z))


def member(start, end, width, height, hollow=False):
    length = (App.Vector(*end) - App.Vector(*start)).Length
    shape = Part.makeBox(length, width, height, App.Vector(0, -width / 2, -height / 2))
    if hollow:
        wall = 1.6
        bore = Part.makeBox(length + 2, width - 2 * wall, height - 2 * wall,
                            App.Vector(-1, -width / 2 + wall, -height / 2 + wall))
        shape = shape.cut(bore)
    direction = App.Vector(*end) - App.Vector(*start)
    shape.Placement = App.Placement(
        App.Vector(*start), App.Rotation(App.Vector(1, 0, 0), direction)
    )
    return shape


def feature(doc, group, name, label, shape, color, transparency=0):
    obj = doc.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "DesignStatus", "Design")
    obj.DesignStatus = "Concept only; no load rating or construction approval"
    if obj.ViewObject:
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.LineColor = (0.15, 0.15, 0.15)
        obj.ViewObject.Transparency = transparency
    group.addObject(obj)
    return obj


def original_reference(doc, group):
    source = App.openDocument(str(ROOT / "Trailer.FCStd"))
    mesh = Mesh.Mesh(source.Objects[0].Mesh)
    App.closeDocument(source.Name)
    # The source uses meter-sized numbers in a millimeter document, with Y up.
    transform = App.Matrix(
        0, 0, 1000, -3.760,
        1000, 0, 0, 2091.336,
        0, 1000, 0, -1.0,
        0, 0, 0, 1,
    )
    mesh.transform(transform)
    obj = doc.addObject("Mesh::Feature", "OriginalTrailerReference")
    obj.Label = "Original trailer - scaled 1000x, reoriented; hidden for access"
    obj.Mesh = mesh
    group.addObject(obj)
    if obj.ViewObject:
        obj.ViewObject.Transparency = 85
        obj.ViewObject.Visibility = False
    return obj


def wire_deck(top):
    bottom = top - 8
    rods = []
    for y in range(125, 1081, 40):
        rods.append(Part.makeCylinder(2, 1700, App.Vector(-850, y, bottom + 2),
                                      App.Vector(1, 0, 0)))
    for x in range(-800, 811, 40):
        rods.append(Part.makeCylinder(2, 1000, App.Vector(x, 100, bottom + 6),
                                      App.Vector(0, 1, 0)))
    return Part.makeCompound(rods).common(slab(OUTLINE, bottom, 8))


def tote(doc, group, name, size, x, y, level):
    dx, dy, dz = size
    obj = feature(doc, group, name, name.replace("_", " "),
                  box(x, y, level, dx, dy, dz), COLORS["tote"], 45)
    obj.addProperty("App::PropertyString", "EnvelopeNote", "Design")
    obj.EnvelopeNote = "Lid/handle-inclusive DESIGN ALLOWANCE, not verified HDX dimensions"
    for prop, value in zip(("EnvelopeWidth", "EnvelopeDepth", "EnvelopeHeight"), size):
        obj.addProperty("App::PropertyLength", prop, "Design")
        setattr(obj, prop, value)
    feature(doc, group, name + "_LidMarker", "Yellow lid marker - inside clearance envelope",
            box(x, y, level + dz - 12, dx, dy, 12), COLORS["lid"], 20)
    return obj


def build(variant):
    wood = variant == "Wood"
    doc = App.newDocument("Front_V_" + variant)
    doc.Label = "Front V shelving - " + ("wood" if wood else "wire shelves")
    doc.addObject("App::DocumentObjectGroup", "Reference")
    doc.addObject("App::DocumentObjectGroup", "Rack")
    doc.addObject("App::DocumentObjectGroup", "ToteEnvelopes")
    doc.addObject("App::DocumentObjectGroup", "ClearanceChecks")
    original_reference(doc, doc.Reference)
    metadata = doc.addObject("App::FeaturePython", "DesignParameters")
    metadata.Label = "Design assumptions - read README before construction"
    for prop, value in (
        ("SourceScale", "1000; approximate 6 ft width confirmed, other dimensions unmeasured"),
        ("ProductStatus", "Unbranded custom wire-shelf or standard lumber/plywood concept"),
        ("ToteStatus", "HDX 27/12/7 gallon targets; envelopes are NOT product specifications"),
        ("RestraintStatus", "Yellow bars indicate removable travel restraints; hardware unspecified"),
        ("StructuralStatus", "No load rating; verify framing, joints, anchorage and tongue weight"),
        ("Axes", "X across trailer; Y from nose toward rear; Z above floor; units mm"),
    ):
        metadata.addProperty("App::PropertyString", prop, "Design")
        setattr(metadata, prop, value)
    for index, z in enumerate(LEVELS, 1):
        metadata.addProperty("App::PropertyLength", "Shelf%dTop" % index, "Design")
        setattr(metadata, "Shelf%dTop" % index, z)

    color = COLORS["wood" if wood else "metal"]
    post_width, post_depth = (38, 64) if wood else (25.4, 25.4)
    rail_width, rail_height = (38, 64) if wood else (25.4, 25.4)
    deck_thickness = 18 if wood else 8
    for index, (x, y) in enumerate(POSTS, 1):
        post = box(x - post_width / 2, y - post_depth / 2, 3,
                   post_width, post_depth, 1597)
        if not wood:
            post = post.cut(box(x - post_width / 2 + 1.6, y - post_depth / 2 + 1.6,
                                2, post_width - 3.2, post_depth - 3.2, 1599))
        feature(doc, doc.Rack, "Post%d" % index,
                ("Nose-side" if index <= 2 else "Loading-side") + " upright %d" % index,
                post, color)
        feature(doc, doc.Rack, "Foot%d" % index, "Concept floor anchor plate %d" % index,
                box(x - 40, y - 40, 0, 80, 80, 3), color)

    for index, level in enumerate(LEVELS, 1):
        deck = slab(OUTLINE, level - 18, 18) if wood else wire_deck(level)
        feature(doc, doc.Rack, "Shelf%d" % index,
                ("18 mm plywood deck " if wood else "Custom clipped wire deck ") + str(index),
                deck, color)
        rail_z = level - deck_thickness - rail_height / 2
        connections = (
            (POSTS[0], POSTS[1], "NoseCrossbeam"),
            (POSTS[2], POSTS[3], "LoadingCrossbeam"),
            (POSTS[0], (-210, 690), "LeftRailForward"),
            ((-210, 690), POSTS[2], "LeftRailAft"),
            (POSTS[1], POSTS[3], "RightRail"),
        )
        for a, b, title in connections:
            start = (*a, rail_z)
            end = (*b, rail_z)
            feature(doc, doc.Rack, title + str(index),
                    "%s - level %d" % (title, index),
                    member(start, end, rail_width, rail_height, not wood), color)
        # Perimeter bearers support the irregular notch and the nose overhang.
        for edge, (a, b) in enumerate(zip(OUTLINE, OUTLINE[1:] + OUTLINE[:1])):
            feature(doc, doc.Rack, "Edge%d_%d" % (index, edge),
                    "Perimeter bearer - shelf %d edge %d" % (index, edge),
                    member((*a, rail_z), (*b, rail_z), rail_width, rail_height, not wood),
                    color)
        feature(doc, doc.Rack, "TravelRestraint%d" % index,
                "REMOVABLE travel-restraint placeholder - level %d" % index,
                box(-185, 1026, level + 45, 920, 8, 25), COLORS["lid"])

    for index, (a, b) in enumerate((((-480, 400, 150), (480, 400, 1500)),
                                  ((480, 400, 150), (-480, 400, 1500))), 1):
        feature(doc, doc.Rack, "RearBrace%d" % index, "Nose-side X brace %d" % index,
                member(a, b, 20 if wood else 16, 12 if wood else 3), color)
    # Bracing is behind the totes; removable restraint bars remain on the loading face.
    totes = [
        tote(doc, doc.ToteEnvelopes, "HDX_27gal_TARGET", (800, 540, 400),
             -175, 475, LEVELS[0]),
        tote(doc, doc.ToteEnvelopes, "HDX_12gal_TARGET", (600, 450, 355),
             -75, 540, LEVELS[1]),
        tote(doc, doc.ToteEnvelopes, "HDX_7gal_TARGET_Left", (400, 520, 305),
             -170, 490, LEVELS[2]),
        tote(doc, doc.ToteEnvelopes, "HDX_7gal_TARGET_Right", (400, 520, 305),
             250, 490, LEVELS[2]),
    ]
    door = feature(doc, doc.ClearanceChecks, "SideDoorKeepout",
                   "Side-door entry zone - 610 mm deep; VERIFY door swing",
                   box(-950, DOOR_Y, 0, 689, 922.087, 1971.1), (1.0, 0.15, 0.1), 85)
    paths = []
    for index, obj in enumerate(totes, 1):
        bb = obj.Shape.BoundBox
        path = feature(doc, doc.ClearanceChecks, "RemovalPath%d" % index,
                       "Straight removal envelope %d - release restraint first" % index,
                       box(bb.XMin, bb.YMin, bb.ZMin, bb.XLength,
                           1800 - bb.YMin, bb.ZLength), (0.2, 0.8, 0.4), 90)
        paths.append(path)
    outline = feature(doc, doc.Reference, "NoseOutline", "Measured mesh nose outline",
                      polygon(NOSE), (0.3, 0.3, 0.3))
    if outline.ViewObject:
        outline.ViewObject.LineWidth = 3
    for obj in doc.ClearanceChecks.Group:
        if obj.ViewObject:
            obj.ViewObject.Visibility = False
    doc.recompute()
    report = validate(doc, totes, door, paths, deck_thickness, rail_height)
    filename = OUT / ("Front_V_Wood.FCStd" if wood else "Front_V_Wire_Shelves.FCStd")
    if App.GuiUp:
        import FreeCADGui as Gui

        App.setActiveDocument(doc.Name)
        from PySide import QtCore

        view = Gui.getDocument(doc.Name).activeView()
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(100, loop.quit)
        loop.exec()
        camera_z = App.Vector(1, 2, 1.2)
        camera_x = App.Vector(0, 0, 1).cross(camera_z)
        camera_y = camera_z.cross(camera_x)
        rotation = App.Rotation(camera_x, camera_y, camera_z, "ZXY")
        axis = rotation.Axis
        camera = re.sub(
            r"orientation\s+[^\n]+",
            "orientation %.12f %.12f %.12f %.12f"
            % (axis.x, axis.y, axis.z, rotation.Angle),
            view.getCamera(),
        )
        view.setCamera(camera)
        view.fitAll()
        Gui.updateGui()
        view.saveImage(str(filename.with_suffix(".png")), 1400, 1100, "White")
    doc.saveAs(str(filename))
    if App.GuiUp:
        with zipfile.ZipFile(filename) as archive:
            camera = ET.fromstring(archive.read("GuiDocument.xml")).find("Camera")
            orientation = re.search(r"orientation\s+([^\n]+)", camera.attrib["settings"])
            x, y, z, angle = map(float, orientation.group(1).split())
            rotation = App.Rotation(App.Vector(x, y, z), math.degrees(angle))
            assert rotation.multVec(App.Vector(0, 1, 0)).z > 0.65, "Tilted camera"
            assert 0.1 < abs(rotation.multVec(App.Vector(0, 0, 1)).z) < 0.8, "Top-down camera"
    count = len(doc.Objects)
    App.closeDocument(doc.Name)
    reopened = App.openDocument(str(filename))
    assert len(reopened.Objects) == count, "Object count changed after reopening"
    for obj in reopened.Rack.Group:
        assert obj.Shape.isValid(), "Invalid saved geometry: " + obj.Name
    if App.GuiUp:
        assert not reopened.OriginalTrailerReference.ViewObject.Visibility
        assert not reopened.SideDoorKeepout.ViewObject.Visibility
        assert reopened.Shelf1.ViewObject.Visibility
    App.closeDocument(reopened.Name)
    report["saved_and_reopened"] = True
    report["file"] = filename.name
    return report


def overlap(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    return a.common(b).Volume


def validate(doc, totes, door, paths, deck_thickness, rail_height):
    rack = doc.Rack.Group
    structural = [obj for obj in rack if not obj.Name.startswith("TravelRestraint")]
    for obj in rack:
        assert obj.Shape.isValid() and obj.Shape.Volume > 0, obj.Name
        assert obj.Shape.BoundBox.ZMin >= -0.01, "Below floor: " + obj.Name
        assert overlap(obj.Shape, door.Shape) < 0.01, "Door interference: " + obj.Name
    for i, tote_obj in enumerate(totes):
        for obj in rack:
            assert overlap(tote_obj.Shape, obj.Shape) < 0.01, (
                "Tote interference: " + tote_obj.Name + " / " + obj.Name)
        for other in totes[i + 1:]:
            assert overlap(tote_obj.Shape, other.Shape) < 0.01, "Totes overlap"
        assert overlap(tote_obj.Shape, door.Shape) < 0.01, "Tote blocks door"
        bb = tote_obj.Shape.BoundBox
        footprint = box(bb.XMin, bb.YMin, 0, bb.XLength, bb.YLength, 1)
        supported = footprint.common(slab(OUTLINE, 0, 1)).Volume
        assert abs(supported - footprint.Volume) < 0.01, "Tote outside deck footprint"
        for obj in structural:
            assert overlap(paths[i].Shape, obj.Shape) < 0.01, (
                "Removal interference: " + tote_obj.Name + " / " + obj.Name)
        for j, other in enumerate(totes):
            if i != j:
                assert overlap(paths[i].Shape, other.Shape) < 0.01, "Removal hits another tote"
    # A 25 mm margin inside both angled walls, continuing along the straight walls.
    for obj in list(rack) + totes:
        vertices = obj.Shape.Vertexes
        for vertex in vertices:
            x, y = vertex.Point.x, vertex.Point.y
            assert y >= 0.604834 * (-x) + 25, "Left nose wall: " + obj.Name
            assert y >= 0.639962 * x + 25, "Right nose wall: " + obj.Name
            assert -846.281 <= x <= 835.155, "Straight wall: " + obj.Name
    assert min((LEVELS[1] - deck_thickness - rail_height) - (LEVELS[0] + 400),
               (LEVELS[2] - deck_thickness - rail_height) - (LEVELS[1] + 355)) >= 50
    return {
        "rack_components": len(rack),
        "tote_envelopes": len(totes),
        "invalid_shapes": 0,
        "tote_rack_interferences": 0,
        "door_zone_interferences": 0,
        "removal_path_interferences_with_restraints_released": 0,
        "minimum_nominal_angled_wall_margin_mm": 25,
        "shelf_top_heights_mm": list(LEVELS),
        "door_entry_depth_mm": 610,
        "checks_do_not_establish": [
            "load rating", "actual HDX dimensions", "door swing",
            "anchor suitability", "tongue weight", "manufacturing joint design",
        ],
    }


def drawing():
    ns = "http://www.w3.org/2000/svg"
    ET.register_namespace("", ns)
    root = ET.Element("{" + ns + "}svg", {
        "width": "1200", "height": "980", "viewBox": "0 0 1200 980",
        "role": "img", "aria-label": "Front V shelving plan and loading elevation",
    })

    def element(tag, **attrs):
        return ET.SubElement(root, "{" + ns + "}" + tag, {k: str(v) for k, v in attrs.items()})

    def text(x, y, value, size=17):
        node = element("text", x=x, y=y, fill="#17212b",
                       **{"font-family": "sans-serif", "font-size": size})
        node.text = value

    def plan_points(points):
        return " ".join("%.1f,%.1f" % (300 + x * .26, 110 + y * .26) for x, y in points)

    element("rect", x=0, y=0, width=1200, height=980, fill="white")
    text(35, 38, "FRONT V SHELVING - TWO MATERIAL OPTIONS / SAME FIT", 24)
    text(35, 66, "CONCEPT ONLY - all dimensions in mm; tote envelopes are not product specifications", 15)
    text(35, 100, "PLAN - bottom tote shown; nose at top", 18)
    element("polyline", points=plan_points(NOSE), fill="none", stroke="#343f48",
            **{"stroke-width": 3})
    element("polygon", points=plan_points(OUTLINE), fill="#dce6ee", stroke="#355469",
            **{"stroke-width": 2})
    element("rect", x=300 - 175 * .26, y=110 + 475 * .26, width=800 * .26,
            height=540 * .26, fill="#f7db69", stroke="#655317")
    text(250, 315, "27-gal TARGET", 14)
    for x, y in POSTS:
        element("rect", x=300 + x * .26 - 5, y=110 + y * .26 - 5,
                width=10, height=10, fill="#30373b")
    element("rect", x=300 - 950 * .26, y=110 + DOOR_Y * .26,
            width=689 * .26, height=922.087 * .26, fill="#ffdddd",
            **{"fill-opacity": .6, "stroke": "#a33", "stroke-dasharray": "6 4"})
    text(35, 590, "Red zone: 610 mm entry depth inside side wall.", 15)
    text(35, 615, "Notch keeps rack, totes and removal paths out of this zone.", 15)
    text(35, 645, "Four black squares: two nose-side + two loading-side uprights.", 15)
    text(35, 675, "Shelf rear edge: 1080 mm from nose; extension beyond V ~530 mm.", 15)
    text(650, 100, "LOADING ELEVATION - looking toward nose", 18)
    sx, base, scale = 880, 550, .25
    element("line", x1=640, y1=base, x2=1150, y2=base, stroke="#444")
    for x, _ in POSTS:
        element("rect", x=sx + x * scale - 4, y=base - 1600 * scale,
                width=8, height=1600 * scale, fill="#8a9298")
    for level in LEVELS:
        element("rect", x=sx - 820 * scale, y=base - level * scale,
                width=1630 * scale, height=5, fill="#b88954")
    for x, width, height, level, label in (
        (-175, 800, 400, LEVELS[0], "27 gal"),
        (-75, 600, 355, LEVELS[1], "12 gal"),
        (-170, 400, 305, LEVELS[2], "7 gal"),
        (250, 400, 305, LEVELS[2], "7 gal"),
    ):
        element("rect", x=sx + x * scale, y=base - (level + height) * scale,
                width=width * scale, height=height * scale, fill="#414951", stroke="#222")
        element("rect", x=sx + x * scale, y=base - (level + height) * scale,
                width=width * scale, height=4, fill="#f1cf3d")
        text(sx + x * scale + 10, base - (level + height / 2) * scale, label, 14)
    text(650, 590, 'Shelf tops: 4", 26", 46" above floor.', 16)
    text(650, 615, "Elevation is schematic; plan notch is not visible here.", 14)
    text(35, 740, "VERSION 1 - WIRE SHELVES", 19)
    text(35, 770, "25.4 mm square tube concept; custom wire decks; front/rear bearers and rear X bracing.", 16)
    text(35, 795, "Unbranded concept. Custom wire decks follow the V and door notch; not an off-the-shelf rack.", 16)
    text(35, 845, "VERSION 2 - WOOD", 19)
    text(35, 875, "18 mm plywood decks; 38 x 64 mm posts/bearers; front/rear supports and rear X bracing.", 16)
    text(35, 920, "Yellow travel bars in CAD are removable restraint placeholders; joints and anchors need design.", 16)
    text(35, 947, "Physical measurements, actual tote fit and structural review are required before building.", 16)
    ET.ElementTree(root).write(OUT / "Shelving_Comparison.svg", encoding="utf-8",
                               xml_declaration=True)


def main():
    original_hash = hashlib.sha256((ROOT / "Trailer.FCStd").read_bytes()).hexdigest()
    results = [build("Metal"), build("Wood")]
    assert hashlib.sha256((ROOT / "Trailer.FCStd").read_bytes()).hexdigest() == original_hash
    drawing()
    report = {
        "source_sha256": original_hash,
        "source_unchanged": True,
        "designs": results,
    }
    (OUT / "validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="ascii")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    if "--gui" in sys.argv:
        import FreeCADGui as Gui

        Gui.showMainWindow()
        Gui.activateWorkbench("PartWorkbench")
    main()
