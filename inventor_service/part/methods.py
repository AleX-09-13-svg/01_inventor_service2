from .component_definition import PartCoreMethods
from .component_definition.features import PartConfiguredMethods, PartHoleMethods
from .component_definition.sketches import PartDrillingSketchMethods, PartSketchMethods
from .component_definition.surface_bodies import (
    PartFaceMethods,
    PartGeometryMethods,
    PartSurfaceBodiesMethods,
)


class PartMethods(
    # Методы создания детали по конфигурации.
    PartConfiguredMethods,
    # Базовые методы детали: обновление, сохранение, параметры, рабочая геометрия.
    PartCoreMethods,
    # Методы работы с телами детали.
    PartSurfaceBodiesMethods,
    # Геометрические методы для точек, граней и координат.
    PartGeometryMethods,
    # Методы поиска и выбора граней.
    PartFaceMethods,
    # Методы работы с эскизами.
    PartSketchMethods,
    # Методы создания эскизов для сверления.
    PartDrillingSketchMethods,
    # Методы создания и настройки отверстий.
    PartHoleMethods,
):
    """Общий набор методов для работы с деталью Inventor."""

    pass
