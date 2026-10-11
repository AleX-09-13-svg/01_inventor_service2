from inventor_service import Inventor


HOLE_DIAMETER = "5 mm"
HOLE_DEPTH = "10 mm"
HOLE_DIRECTION = "positive"
SKETCH_NAME = "Hole center"
FEATURE_NAME = "Center hole"


inventor = Inventor()

selected_faces = inventor.selected_faces()
if selected_faces:
    face = selected_faces[0]
else:
    face = inventor.pick_face("Select planar face for hole", planar=True)

sketch = inventor.get_or_create_sketch_on_face(
    face,
    name=SKETCH_NAME,
    prefix=SKETCH_NAME,
)
hole_center = inventor.add_face_center_point(face, sketch=sketch)

hole = inventor.add_holes(
    [hole_center],
    diameter=HOLE_DIAMETER,
    depth=HOLE_DEPTH,
    direction=HOLE_DIRECTION,
    name=FEATURE_NAME,
)

inventor.update_part()

print("Created hole:", hole.Name)
