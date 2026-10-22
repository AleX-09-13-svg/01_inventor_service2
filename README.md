# inventor_service

Удобный Python-слой над Autodesk Inventor API.

Пакет собирает часто используемые операции Inventor в более короткий и понятный интерфейс: работа с активным документом, параметрами, телами детали, гранями, эскизами, отверстиями и конфигурациями детали.

## Установка

Проект рассчитан на Python 3.10+ и работу в Windows-среде с Autodesk Inventor.

```powershell
pip install -e .
```

Основная внешняя зависимость:

```text
pywin32
```

## Быстрый импорт

```python
from inventor_service import Inventor, get_inventor_service

inventor = get_inventor_service()
inventor.update()
```

Публичный импорт пакета находится в `inventor_service/__init__.py`.

## Что входит в ядро

Основное ядро библиотеки:

```text
inventor_service/
    inventor_api.py          # точка входа к Inventor
    general/                 # общие методы, свойства, типы и константы Inventor
    part/                    # методы работы с деталями
    assembly/                # методы работы со сборками
    drawing/                 # методы работы с чертежами
    config/                  # чтение и подготовка конфигураций
    settings.py              # настройки библиотеки
```

Прикладные сценарии под конкретный проект не должны лежать в корне библиотеки. Например, логика конфирматов была вынесена из ядра: такие workflow лучше хранить в отдельном проекте, в `workflows/`, `recipes/` или `scripts/`.

## Архитектура методов

Методы собираются через mixin-классы: каждый mixin отвечает за свою область, а итоговый класс только объединяет их в один публичный интерфейс.

Так проще понимать, где искать реализацию:

- сборочный файл показывает карту методов;
- тематический mixin содержит конкретную реализацию;
- публичное имя класса остается стабильным для внешних проектов.

### Общие методы Inventor

`InventorBaseMethods` собирает общий набор базовых методов Inventor.

`InventorMethods` оставлен как алиас для обратной совместимости:

```python
class InventorBaseMethods(
    # Активный документ: обновление и получение имени текущего документа/детали.
    InventorDocumentMethods,
    # Единицы измерения: перевод значений и формирование выражений вида "10 mm".
    InventorUnitMethods,
    # Направления и ориентации: строки "+", "-", "horizontal" -> константы Inventor.
    InventorDirectionMethods,
    # Общие утилиты: безопасный getattr и создание ObjectCollection.
    InventorUtilityMethods,
    # UI Inventor: выбор объекта через Pick и сообщения пользователю.
    InventorUIMethods,
    # Экран Inventor: временное отключение ScreenUpdating на время операции.
    InventorScreenMethods,
):
    """Базовый набор общих методов Inventor."""


InventorMethods = InventorBaseMethods
```

Реализация находится в:

```text
inventor_service/general/method_mixins/
```

### Методы детали

`PartMethods` собирает общий набор методов для работы с деталью:

```python
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
```

Сборочный файл:

```text
inventor_service/part/methods.py
```

### Методы эскизов

`PartSketchMethods` собирает общий набор методов для работы с эскизами детали:

```python
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
```

Реализация находится в:

```text
inventor_service/part/component_definition/sketches/method_mixins/
```

Константы сверления лежат рядом с логикой сверления:

```text
inventor_service/part/component_definition/sketches/drilling_constants.py
```

## Проверка после изменений

Быстрая проверка синтаксиса и импортов:

```powershell
python -m compileall inventor_service
python -c "import inventor_service; print('ok')"
```
