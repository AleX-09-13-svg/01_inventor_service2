from .method_mixins import (
    PartSketchConstraintMethods,
    PartSketchCoordinateMethods,
    PartSketchCoreMethods,
    PartSketchDimensionMethods,
    PartSketchLineMethods,
    PartSketchPointMethods,
    PartSketchProjectionMethods,
    PartSketchStateMethods,
    PartSketchWorkPlaneMethods,
)


class PartSketchMethods(
    # Создание, поиск и переиспользование эскизов.
    PartSketchCoreMethods,
    # Преобразование координат модели и эскиза.
    PartSketchCoordinateMethods,
    # Точки эскиза и центры отверстий.
    PartSketchPointMethods,
    # Проекция точек, ребер и объектов в эскиз.
    PartSketchProjectionMethods,
    # Линии эскиза и геометрия линий.
    PartSketchLineMethods,
    # Размерные зависимости эскиза.
    PartSketchDimensionMethods,
    # Видимость, отложенное обновление и Solve.
    PartSketchStateMethods,
    # Геометрические зависимости эскиза.
    PartSketchConstraintMethods,
    # Рабочие плоскости, связанные с эскизами.
    PartSketchWorkPlaneMethods,
):
    """Общий набор методов для работы с эскизами детали."""

    pass
