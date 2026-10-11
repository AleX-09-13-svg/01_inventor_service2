from .general import (
    InventorMethods,
    InventorProperties,
    kAlignedDim,
    kAssemblyLeafOccurrenceFilter,
    kFeatureAppearance,
    kHorizontalDim,
    kNegativeExtentDirection,
    kPartDocumentObject,
    kPartFaceFilter,
    kPartFacePlanarFilter,
    kPositiveExtentDirection,
    kVerticalDim,
)
from .assembly import AssemblyMethods, AssemblyProperties
from .drawing import DrawingMethods, DrawingProperties
from .part import PartMethods, PartProperties


class Inventor(
    InventorProperties,
    InventorMethods,
    PartProperties,
    PartMethods,
    AssemblyProperties,
    AssemblyMethods,
    DrawingProperties,
    DrawingMethods,
):
    PART_DOCUMENT_OBJECT = kPartDocumentObject

    POSITIVE_EXTENT_DIRECTION = kPositiveExtentDirection
    NEGATIVE_EXTENT_DIRECTION = kNegativeExtentDirection

    HORIZONTAL_DIMENSION = kHorizontalDim
    VERTICAL_DIMENSION = kVerticalDim
    ALIGNED_DIMENSION = kAlignedDim

    PART_FACE_FILTER = kPartFaceFilter
    PART_FACE_PLANAR_FILTER = kPartFacePlanarFilter
    ASSEMBLY_LEAF_OCCURRENCE_FILTER = kAssemblyLeafOccurrenceFilter

    FEATURE_APPEARANCE = kFeatureAppearance
