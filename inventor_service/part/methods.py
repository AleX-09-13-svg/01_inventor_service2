from .component_definition import PartCoreMethods
from .component_definition.features import PartConfiguredMethods, PartHoleMethods
from .component_definition.sketches import PartDrillingSketchMethods, PartSketchMethods
from .component_definition.surface_bodies import (
    PartFaceMethods,
    PartGeometryMethods,
    PartSurfaceBodiesMethods,
)


class PartMethods(
    PartConfiguredMethods,
    PartCoreMethods,
    PartSurfaceBodiesMethods,
    PartGeometryMethods,
    PartFaceMethods,
    PartSketchMethods,
    PartDrillingSketchMethods,
    PartHoleMethods,
):
    pass
