# Методы объекта service

`get_inventor_service()` возвращает объект `Inventor`. В текущей версии у него **186 публичных методов**, включая унаследованные. Каждый метод указан один раз с учётом порядка наследования.

```python
from inventor_service import get_inventor_service

service = get_inventor_service()
```

Вызов: `service.имя_метода(...)`. В таблицах параметр `self` опущен: передавать его не нужно. Параметры со значениями по умолчанию необязательны. Свойства (`app`, `doc`, `comp` и другие), константы и имена с начальным `_` в число методов не входят.

## Подключение сервиса

| Функция | Параметры | Назначение |
| --- | --- | --- |
| `get_inventor_service()` | `app=None, visible=True` | Создать сервис; app позволяет передать COM-приложение Inventor. Функция модуля, в 186 методов объекта не включена. |

## Общие параметры

| Параметр | Значение |
| --- | --- |
| `face`, `sketch`, `entity` | COM-объект грани, эскиза или другой геометрической сущности. |
| `component_definition=None` | Используется компонент активной детали. |
| `name`, `prefix` | Точное имя объекта и префикс для фильтрации по имени. |
| `tol` | Числовой допуск сравнения. |
| `ignore_errors=True` | Подавлять ошибки операции; False передаёт исключение вызывающему коду. |
| `construction=True` | Вспомогательная геометрия эскиза. |
| `hole_center=True` | Точка эскиза является центром отверстия. |
| `driven=True` | Справочный размер, который измеряет геометрию. |
| `expression` | Выражение Inventor, например `"32 mm"` или имя параметра. |
| `**kwargs` | Дополнительные именованные настройки вложенного метода. |

Числовые координаты и длины во внутренних единицах Inventor задаются в сантиметрах; `service.mm(10)` переводит 10 мм в 1 см. Для размерных выражений можно использовать строки с единицами. Значение направления `20993` в сигнатурах — `kPositiveExtentDirection`.

## Разделы

- Подключение, документы и общие утилиты — 13 методов.
- Единицы, направления и ориентация — 5 методов.
- Выбор объектов и выделенные грани — 17 методов.
- Тела, грани, рёбра и вершины — 18 методов.
- Плоскости и нормали — 9 методов.
- Цвет и внешний вид — 12 методов.
- Создание и поиск эскизов — 7 методов.
- Координаты и точки — 19 методов.
- Проекция геометрии — 5 методов.
- Линии и расчёты в эскизе — 15 методов.
- Геометрические зависимости — 8 методов.
- Размеры эскиза — 4 метода.
- Видимость и пересчёт эскиза — 9 методов.
- Рабочие плоскости, оси и точки — 6 методов.
- Параметры детали — 16 методов.
- Операции и отверстия — 8 методов.
- Эскизы для сверления — 10 методов.
- Конфигурации и сценарии — 5 методов.

## Подключение, документы и общие утилиты

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`get_application()`](inventor_service/general/properties.py#L5) | `visible=True` | Подключиться к уже работающему Inventor; visible задаёт видимость, None сохраняет текущее значение. Приложение не запускает. |
| [`active_document_name()`](inventor_service/general/method_mixins/documents.py#L5) | — | Вернуть DisplayName активного документа. |
| [`active_part_name()`](inventor_service/general/method_mixins/documents.py#L9) | — | Вернуть имя активного документа; алиас active_document_name(). |
| [`update()`](inventor_service/general/method_mixins/documents.py#L2) | — | Обновить активный документ. |
| [`update_part()`](inventor_service/part/component_definition/core.py#L30) | — | Обновить документ детали и вернуть его. |
| [`save_part()`](inventor_service/part/component_definition/core.py#L34) | — | Сохранить документ детали и вернуть его. |
| [`save_part_as()`](inventor_service/part/component_definition/core.py#L38) | `file_name, save_copy_as=False` | Сохранить деталь в file_name; save_copy_as=True сохраняет копию. |
| [`screen_updates_suspended()`](inventor_service/general/method_mixins/screen.py#L5) | — | Контекстный менеджер для with: временно отключить обновление экрана и восстановить исходное состояние. |
| [`safe_getattr()`](inventor_service/general/method_mixins/utils.py#L2) | `obj, attr, default=None` | Прочитать атрибут attr; при ошибке вернуть default. |
| [`object_collection()`](inventor_service/general/method_mixins/utils.py#L9) | `objects` | Создать COM ObjectCollection из переданных объектов. |
| [`unique_collection_name()`](inventor_service/part/component_definition/core.py#L2) | `collection, base, separator='_'` | Подобрать свободное имя в COM-коллекции, добавляя separator и числовой суффикс. |
| [`show_message()`](inventor_service/general/method_mixins/ui.py#L5) | `title, text, icon='info'` | Показать системное сообщение с заголовком, текстом и значком icon. |
| [`show_missing_parameters_message()`](inventor_service/general/method_mixins/ui.py#L22) | `names, title='Missing parameters'` | Показать сообщение со списком отсутствующих параметров. |

## Единицы, направления и ориентация

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`mm()`](inventor_service/general/method_mixins/units.py#L2) | `value` | Перевести миллиметры во внутренние единицы длины Inventor — сантиметры. |
| [`mm_text()`](inventor_service/general/method_mixins/units.py#L6) | `value` | Сформировать выражение размера с суффиксом mm. |
| [`hole_direction()`](inventor_service/general/method_mixins/directions.py#L2) | `name` | Преобразовать название или значение направления в константу Inventor. |
| [`opposite_hole_direction()`](inventor_service/general/method_mixins/directions.py#L20) | `direction` | Вернуть противоположное направление отверстия. |
| [`dimension_orientation()`](inventor_service/general/method_mixins/directions.py#L31) | `name` | Преобразовать horizontal, vertical или aligned в константу ориентации размера. |

## Выбор объектов и выделенные грани

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`pick()`](inventor_service/general/method_mixins/ui.py#L2) | `selection_filter, prompt_text='Select object'` | Запросить выбор объекта по фильтру selection_filter с подсказкой prompt_text. |
| [`pick_part()`](inventor_service/assembly/methods.py#L2) | `prompt_text='Select part'` | Запросить выбор компонента детали в сборке. |
| [`pick_face()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L318) | `prompt_text='Select face', planar=True` | Запросить выбор грани; planar=True ограничивает выбор плоскими гранями. |
| [`pick_faces_until_cancel()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L324) | `prompt_text='Select face', planar=True` | Запрашивать грани до отмены и вернуть список без повторов. |
| [`selected_faces()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L234) | `debug=False` | Вернуть грани из текущего выделения; debug включает диагностический вывод. |
| [`require_selected_faces()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L268) | `min_count=1, planar=True, debug=False` | Вернуть выделенные грани или вызвать RuntimeError, если их меньше min_count; planar фильтрует плоские. |
| [`selected_face()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L301) | `debug=False` | Вернуть первую выделенную плоскую грань; при отсутствии вызвать ошибку. |
| [`selected_planar_face()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L305) | `debug=False` | Вернуть выделенную грань с дополнительной проверкой плоской геометрии. |
| [`selected_faces_by_color()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L282) | `color_name=None` | Вернуть выделенные грани заданного цвета; без color_name вернуть все выделенные грани. |
| [`selected_faces_grouped_by_plane()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L289) | — | Сгруппировать выделенные грани по совпадающим плоскостям. |
| [`selected_faces_grouped_by_plane_and_appearance()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L292) | — | Собрать группы выделенных граней по плоскости в словарь по внешнему виду первой грани группы. |
| [`face_from_selection_object()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L205) | `obj` | Извлечь грань из объекта выделения, включая NativeObject, ContainingFace и SourceObject; иначе вернуть None. |
| [`is_face_like()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L194) | `obj` | Проверить наличие геометрии, рёбер и вершин, характерных для грани. |
| [`is_planar_face()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L340) | `face` | Проверить, что геометрия грани имеет нормаль и базовую точку плоскости. |
| [`selection_object_label()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L217) | `obj` | Сформировать диагностическую строку с типом и именем объекта выделения. |
| [`selected_face_vertex_points_xy()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L358) | `sketch_name='Face vertices', debug=False` | Создать новый эскиз на выделенной плоской грани и вернуть координаты её вершин как пары (x, y). |
| [`selected_face_vertex_report()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L375) | `sketch_name='Face vertices', debug=False` | Создать эскиз и вернуть словарь: имя документа, количество вершин и координаты вершин. |

## Тела, грани, рёбра и вершины

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`all_surface_bodies()`](inventor_service/part/component_definition/surface_bodies/methods.py#L5) | `component_definition=None` | Вернуть тела детали в ObjectCollection. |
| [`surface_body()`](inventor_service/part/component_definition/surface_bodies/methods.py#L2) | `index=1` | Вернуть тело по индексу; нумерация начинается с 1. |
| [`all_faces()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L39) | `component_definition=None` | Вернуть список граней всех тел детали. |
| [`unique_faces()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L20) | `faces` | Убрать повторяющиеся грани по ReferenceKey или идентичности объекта. |
| [`face_key()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L48) | `face` | Вернуть ReferenceKey грани; при недоступности использовать id объекта. |
| [`face_vertices()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L350) | `face` | Вернуть список вершин грани. |
| [`face_vertex_count()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L392) | `face` | Вернуть количество вершин грани. |
| [`face_vertex_points()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L354) | `face` | Вернуть 3D-точки вершин грани. |
| [`face_edges()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L397) | `face` | Вернуть список рёбер грани. |
| [`edge_faces()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L401) | `edge` | Вернуть грани ребра через Faces или TangentiallyConnectedFaces; иначе пустой список. |
| [`shared_face_edge()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L409) | `face1, face2` | Найти общее ребро двух граней; при отсутствии вернуть None. |
| [`adjacent_faces()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L418) | `face` | Вернуть соседние грани, связанные общими рёбрами, без повторов. |
| [`adjacent_face_count()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L428) | `faces, other_faces` | Посчитать грани из faces, имеющие общее ребро хотя бы с одной гранью из other_faces. |
| [`face_area()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L439) | `face` | Прочитать площадь грани напрямую или через Evaluator; при недоступности вернуть None. |
| [`faces_area()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L453) | `faces` | Суммировать площади граней; недоступные площади считать нулевыми. |
| [`face_model_bounds()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L456) | `face` | Вернуть границы по вершинам: (min_x, max_x, min_y, max_y, min_z, max_z). |
| [`point_inside_model_bounds()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L463) | `point, bounds, tol=0.01` | Проверить попадание 3D-точки в указанные границы с допуском tol. |
| [`candidate_faces_by_normal_axis()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L472) | `axis, coordinate, tol=0.001, component_definition=None` | Найти плоские грани с нормалью вдоль x, y или z и заданной координатой плоскости. |

## Плоскости и нормали

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`plane_geometry()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/geometry.py#L2) | `entity` | Получить геометрию плоскости через Geometry или Plane. |
| [`plane_normal()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/geometry.py#L95) | `entity` | Вернуть нормаль плоскости. |
| [`face_normal()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/geometry.py#L99) | `face` | Вернуть нормаль плоской грани. |
| [`plane_root_point()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/geometry.py#L103) | `entity` | Вернуть базовую точку плоскости. |
| [`plane_key()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/geometry.py#L44) | `entity, tol=0.001` | Сформировать ключ плоскости из нормализованного направления нормали и расстояния с округлением по tol. |
| [`same_plane_entity()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/geometry.py#L9) | `entity1, entity2, offsets=None, tol=0.001` | Проверить параллельность нормалей и допустимое расстояние между плоскостями; offsets=None означает нулевое смещение. |
| [`same_plane()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/geometry.py#L36) | `face1, face2, tol=0.001` | Проверить совпадение плоскостей двух граней с допуском tol. |
| [`same_offset_plane_entity()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/geometry.py#L40) | `entity, face, offset_value, tol=0.001` | Проверить параллельность и заданное абсолютное смещение плоскостей. |
| [`group_faces_by_plane()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/geometry.py#L69) | `faces` | Сгруппировать грани по совпадающим плоскостям. |

## Цвет и внешний вид

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`face_appearance_text()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L55) | `face` | Собрать названия внешнего вида грани и её родителя в строку. |
| [`face_appearance_key()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L72) | `face` | Вернуть распознанное имя цвета или нормализованный текст внешнего вида. |
| [`face_color()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L95) | `face` | Получить COM-объект цвета грани или её родителя; при отсутствии вернуть None. |
| [`face_color_rgb()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L111) | `face` | Вернуть RGB цвета грани; при недоступности вернуть None. |
| [`detected_face_rgb()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L115) | `face` | Определить RGB напрямую или по распознанному имени цвета. |
| [`is_face_color()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L123) | `face, color_name` | Проверить цвет грани по названию внешнего вида или RGB. |
| [`faces_by_color()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L135) | `component_definition=None` | Сгруппировать все грани детали в словарь по ключу внешнего вида. |
| [`colored_faces()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L144) | `color_name, component_definition=None` | Вернуть грани детали, соответствующие color_name. |
| [`reset_faces_to_feature_appearance()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L499) | `faces` | Сбросить ручное оформление граней к внешнему виду операции; вернуть число успешных сбросов. |
| [`set_sketch_color()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L172) | `sketch, color, include_entities=True` | Задать цвет эскиза по имени, RGB или COM-объекту; include_entities распространяет цвет на линии и точки. |
| [`set_sketch_color_rgb()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L184) | `sketch, rgb, include_entities=True` | Задать цвет эскиза через кортеж RGB. |
| [`set_sketch_color_from_face()`](inventor_service/part/component_definition/surface_bodies/surface_body/faces/methods.py#L187) | `sketch, face, include_entities=True` | Скопировать распознанный цвет грани в эскиз; при неизвестном цвете вернуть эскиз без изменения. |

## Создание и поиск эскизов

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`add_sketch()`](inventor_service/part/component_definition/sketches/method_mixins/core.py#L2) | `planar_entity, name=None` | Всегда создать новый эскиз на planar_entity; при наличии name назначить имя. |
| [`all_sketches()`](inventor_service/part/component_definition/sketches/method_mixins/core.py#L10) | `component_definition=None` | Вернуть список эскизов детали. |
| [`sketches_by_prefix()`](inventor_service/part/component_definition/sketches/method_mixins/core.py#L17) | `prefix, component_definition=None` | Вернуть эскизы, имена которых начинаются с prefix. |
| [`unique_sketch_name()`](inventor_service/part/component_definition/sketches/method_mixins/core.py#L25) | `base, sketches=None` | Подобрать свободное имя эскиза с числовым суффиксом при необходимости. |
| [`sketch_on_face_plane()`](inventor_service/part/component_definition/sketches/method_mixins/core.py#L43) | `face, prefix=None, offsets=None, sketches=None` | Найти эскиз на плоскости грани с учётом prefix и допустимых offsets; иначе None. |
| [`sketch_on_offset_face_plane()`](inventor_service/part/component_definition/sketches/method_mixins/core.py#L59) | `face, prefix, offset_value, sketches=None` | Найти эскиз с заданным префиксом на плоскости, смещённой относительно грани. |
| [`get_or_create_sketch_on_face()`](inventor_service/part/component_definition/sketches/method_mixins/core.py#L67) | `face, name=None, prefix=None, offsets=None` | Найти подходящий эскиз на плоскости грани; при отсутствии создать новый с name. |

## Координаты и точки

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`create_point2d()`](inventor_service/part/component_definition/sketches/method_mixins/coordinates.py#L95) | `x, y` | Создать Point2d через TransientGeometry. |
| [`create_point3d()`](inventor_service/part/component_definition/sketches/method_mixins/coordinates.py#L99) | `x, y, z` | Создать 3D Point через TransientGeometry. |
| [`model_to_sketch_point()`](inventor_service/part/component_definition/sketches/method_mixins/coordinates.py#L2) | `sketch, point_3d` | Перевести 3D-точку модели в 2D-координаты эскиза. |
| [`model_to_sketch_points()`](inventor_service/part/component_definition/sketches/method_mixins/coordinates.py#L7) | `sketch, points_3d` | Перевести список 3D-точек в координаты эскиза. |
| [`model_to_sketch_points_from_vertices()`](inventor_service/part/component_definition/sketches/method_mixins/coordinates.py#L44) | `sketch, vertices` | Перевести COM-коллекцию вершин в список 2D-точек эскиза. |
| [`face_vertex_points_in_sketch()`](inventor_service/part/component_definition/sketches/method_mixins/coordinates.py#L11) | `face, sketch` | Вернуть точки вершин грани в координатах эскиза. |
| [`face_bounds_in_sketch()`](inventor_service/part/component_definition/sketches/method_mixins/coordinates.py#L67) | `face, sketch` | Вернуть границы по вершинам в эскизе: (min_x, max_x, min_y, max_y). |
| [`face_center_in_sketch()`](inventor_service/part/component_definition/sketches/method_mixins/coordinates.py#L82) | `face, sketch` | Вычислить среднее арифметическое координат вершин грани; зависимостей не создаёт. |
| [`sketch_to_model_points()`](inventor_service/part/component_definition/sketches/method_mixins/coordinates.py#L51) | `sketch, sketch_points` | Перевести список SketchPoint в список 3D-точек модели. |
| [`sketch_points_to_model()`](inventor_service/part/component_definition/sketches/method_mixins/coordinates.py#L59) | `sketch, sketch_points` | Алиас преобразования списка SketchPoint в 3D-точки модели. |
| [`add_sketch_point()`](inventor_service/part/component_definition/sketches/method_mixins/points.py#L5) | `sketch, point_2d, hole_center=False` | Добавить точку в эскиз; hole_center=True помечает её центром отверстия. |
| [`add_face_center_point()`](inventor_service/part/component_definition/sketches/method_mixins/points.py#L52) | `face, sketch=None, hole_center=True, sketch_name=None, prefix=None, offsets=None` | Создать центр прямоугольной грани или параллелограмма: проекции внешних рёбер, вспомогательная диагональ и зависимость середины. Без sketch всегда новый эскиз. prefix и offsets не используются. |
| [`sketch_points()`](inventor_service/part/component_definition/sketches/method_mixins/points.py#L18) | `sketch, hole_center=None` | Вернуть точки эскиза; hole_center=None отключает фильтр, True или False фильтруют по признаку центра отверстия. |
| [`sketch_point_count()`](inventor_service/part/component_definition/sketches/method_mixins/points.py#L34) | `sketch` | Вернуть число точек эскиза. |
| [`set_point_hole_center()`](inventor_service/part/component_definition/sketches/method_mixins/points.py#L39) | `point, hole_center=True` | Установить признак центра отверстия; при ошибке вернуть None. |
| [`sketch_hole_center_points()`](inventor_service/part/component_definition/sketches/method_mixins/points.py#L49) | `sketch` | Вернуть только точки, отмеченные центрами отверстий. |
| [`unique_points()`](inventor_service/part/component_definition/sketches/method_mixins/points.py#L141) | `points` | Убрать повторяющиеся SketchPoint по координатам с округлением до 6 знаков. |
| [`mark_as_hole_centers()`](inventor_service/part/component_definition/sketches/method_mixins/points.py#L157) | `points` | Пометить переданные точки центрами отверстий, пропуская ошибки записи. |
| [`point_inside_sketch_bounds()`](inventor_service/part/component_definition/sketches/method_mixins/lines.py#L126) | `point_or_x_y, bounds, tol=0.01` | Проверить попадание точки или пары (x, y) в прямоугольные границы с допуском tol. |

## Проекция геометрии

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`project_entity_to_sketch()`](inventor_service/part/component_definition/sketches/method_mixins/projections.py#L51) | `sketch, entity, construction=None, ignore_errors=False` | Спроецировать объект в эскиз; construction задаёт вспомогательный тип, ignore_errors управляет обработкой ошибок. |
| [`project_face_edges()`](inventor_service/part/component_definition/sketches/method_mixins/projections.py#L37) | `sketch, face, ignore_errors=True` | Спроецировать рёбра грани и вернуть число успешных проекций. |
| [`project_point_to_plane()`](inventor_service/part/component_definition/sketches/method_mixins/projections.py#L2) | `point, planar_entity` | Получить проекцию точки через доступный ProjectPoint или GetClosestPointTo; при отсутствии API вызвать ошибку. |
| [`project_points_to_plane()`](inventor_service/part/component_definition/sketches/method_mixins/projections.py#L21) | `points, planar_entity` | Спроецировать список точек на плоский объект. |
| [`offset_model_points_from_face()`](inventor_service/part/component_definition/sketches/method_mixins/projections.py#L24) | `face, points, offset, direction=-1` | Сместить точки вдоль нормали грани на offset с множителем direction. |

## Линии и расчёты в эскизе

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`add_sketch_line()`](inventor_service/part/component_definition/sketches/method_mixins/lines.py#L39) | `sketch, start_point, end_point, construction=False` | Создать линию по двум Point2d или SketchPoint; construction=True делает её вспомогательной. |
| [`set_entity_construction()`](inventor_service/part/component_definition/sketches/method_mixins/lines.py#L45) | `entity, construction=True` | Установить вспомогательный тип объекта; при ошибке вернуть None. |
| [`sketch_lines()`](inventor_service/part/component_definition/sketches/method_mixins/lines.py#L18) | `sketch, construction=None` | Вернуть линии эскиза; construction=None отключает фильтр по вспомогательному типу. |
| [`sketch_line_count()`](inventor_service/part/component_definition/sketches/method_mixins/lines.py#L5) | `sketch` | Вернуть число линий эскиза. |
| [`sketch_has_lines_or_points()`](inventor_service/part/component_definition/sketches/method_mixins/lines.py#L10) | `sketch` | Проверить наличие хотя бы одной линии или точки в эскизе. |
| [`sketch_has_geometry_for_face()`](inventor_service/part/component_definition/sketches/method_mixins/lines.py#L15) | `sketch, face, tol=0.01` | Проверить наличие минимум двух линий в границах грани. |
| [`sketch_lines_for_face()`](inventor_service/part/component_definition/sketches/method_mixins/lines.py#L55) | `sketch, face, first_new_line=0, tol=0.01` | Вернуть линии в границах вершин грани; first_new_line пропускает первые линии списка. |
| [`distance_2d()`](inventor_service/part/component_definition/sketches/method_mixins/lines.py#L79) | `point1, point2` | Вычислить расстояние между двумя 2D-точками. |
| [`line_length()`](inventor_service/part/component_definition/sketches/method_mixins/lines.py#L84) | `line` | Вычислить длину линии по координатам концов. |
| [`line_length_squared()`](inventor_service/part/component_definition/sketches/drilling.py#L166) | `line` | Вычислить квадрат длины линии без извлечения корня. |
| [`line_midpoint()`](inventor_service/part/component_definition/sketches/method_mixins/lines.py#L91) | `line` | Вернуть Point2d середины линии. |
| [`line_midpoint_xy()`](inventor_service/part/component_definition/sketches/method_mixins/lines.py#L108) | `line` | Вернуть координаты середины линии как пару (x, y). |
| [`line_data()`](inventor_service/part/component_definition/sketches/method_mixins/lines.py#L102) | `line` | Вернуть начало, конец и компоненты вектора линии: (start, end, dx, dy). |
| [`vector_length2d()`](inventor_service/part/component_definition/sketches/method_mixins/lines.py#L98) | `dx, dy` | Вычислить длину 2D-вектора (dx, dy). |
| [`closest_point_on_line()`](inventor_service/part/component_definition/sketches/method_mixins/lines.py#L112) | `point, line` | Найти ближайшую точку на отрезке с ограничением параметра диапазоном от 0 до 1. |

## Геометрические зависимости

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`add_ground_constraint()`](inventor_service/part/component_definition/sketches/method_mixins/constraints.py#L24) | `sketch, entity, ignore_errors=True` | Зафиксировать объект эскиза; ignore_errors управляет подавлением ошибок. |
| [`fix_sketch_entity()`](inventor_service/part/component_definition/sketches/method_mixins/constraints.py#L2) | `sketch, entity` | Зафиксировать один объект, подавляя ошибки. |
| [`fix_sketch_points()`](inventor_service/part/component_definition/sketches/method_mixins/constraints.py#L5) | `sketch, points` | Зафиксировать список точек, подавляя ошибки отдельных зависимостей. |
| [`add_midpoint_constraint()`](inventor_service/part/component_definition/sketches/method_mixins/constraints.py#L33) | `sketch, point_or_line_point, line, ignore_errors=True` | Привязать SketchPoint к середине линии. |
| [`add_coincident_constraint()`](inventor_service/part/component_definition/sketches/method_mixins/constraints.py#L49) | `sketch, entity1, entity2, ignore_errors=True` | Добавить зависимость совпадения объектов, например точки и линии. |
| [`add_parallel_constraint()`](inventor_service/part/component_definition/sketches/method_mixins/constraints.py#L69) | `sketch, line1, line2, ignore_errors=True` | Добавить параллельность двух линий. |
| [`add_perpendicular_constraint()`](inventor_service/part/component_definition/sketches/method_mixins/constraints.py#L59) | `sketch, line1, line2, ignore_errors=True` | Добавить перпендикулярность двух линий. |
| [`add_symmetry_constraint()`](inventor_service/part/component_definition/sketches/method_mixins/constraints.py#L79) | `sketch, entity1, entity2, symmetry_line, ignore_errors=True` | Добавить симметрию двух объектов относительно symmetry_line. |

## Размеры эскиза

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`add_two_point_dimension()`](inventor_service/part/component_definition/sketches/method_mixins/dimensions.py#L26) | `sketch, point1, point2, orientation, text_point, driven=False, expression=None` | Добавить размер между двумя точками с orientation; driven=True создаёт справочный размер, expression задаёт выражение. |
| [`add_aligned_dimension()`](inventor_service/part/component_definition/sketches/method_mixins/dimensions.py#L2) | `sketch, point1, point2, text_point, driven=False` | Добавить выровненный размер между точками; text_point задаёт положение текста. |
| [`sketch_dimension_constraints()`](inventor_service/part/component_definition/sketches/method_mixins/dimensions.py#L13) | `sketch` | Вернуть список размерных зависимостей эскиза. |
| [`sketch_dimension_count()`](inventor_service/part/component_definition/sketches/method_mixins/dimensions.py#L21) | `sketch` | Вернуть количество размерных зависимостей. |

## Видимость и пересчёт эскиза

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`solve_sketch()`](inventor_service/part/component_definition/sketches/method_mixins/state.py#L5) | `sketch, ignore_errors=True` | Выполнить Solve(); ignore_errors=False позволяет передать ошибку вызывающему коду. |
| [`solve_or_update_sketch()`](inventor_service/part/component_definition/sketches/method_mixins/state.py#L78) | `sketch` | Попытаться решить эскиз; при отсутствии результата обновить документ. |
| [`set_sketch_defer_updates()`](inventor_service/part/component_definition/sketches/method_mixins/state.py#L16) | `sketch, value` | Установить отложенное обновление и вернуть предыдущее значение; при ошибке None. |
| [`deferred_sketch_updates()`](inventor_service/part/component_definition/sketches/method_mixins/state.py#L27) | `sketch` | Контекстный менеджер для with: включить отложенный пересчёт и восстановить исходное значение при выходе. |
| [`set_sketch_visible()`](inventor_service/part/component_definition/sketches/method_mixins/state.py#L53) | `sketch, visible` | Установить видимость эскиза; при ошибке вернуть None. |
| [`set_sketch_dimensions_visible()`](inventor_service/part/component_definition/sketches/method_mixins/state.py#L37) | `sketch, visible` | Установить видимость размеров эскиза. |
| [`hide_sketch_dimensions()`](inventor_service/part/component_definition/sketches/method_mixins/state.py#L47) | `sketch` | Скрыть размеры эскиза. |
| [`show_sketch_dimensions()`](inventor_service/part/component_definition/sketches/method_mixins/state.py#L50) | `sketch` | Показать размеры эскиза. |
| [`try_share_sketch()`](inventor_service/part/component_definition/sketches/method_mixins/state.py#L63) | `sketch` | Попытаться включить общий доступ и видимость эскиза через доступные свойства и ShareSketch(). |

## Рабочие плоскости, оси и точки

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`work_plane()`](inventor_service/part/component_definition/core.py#L169) | `index_or_name` | Получить рабочую плоскость по индексу или имени. |
| [`work_axis()`](inventor_service/part/component_definition/core.py#L183) | `index_or_name` | Получить рабочую ось по индексу или имени. |
| [`work_point()`](inventor_service/part/component_definition/core.py#L186) | `index_or_name` | Получить рабочую точку по индексу или имени. |
| [`unique_work_plane_name()`](inventor_service/part/component_definition/core.py#L179) | `base, work_planes=None` | Подобрать свободное имя рабочей плоскости. |
| [`create_work_plane_by_line_plane_angle()`](inventor_service/part/component_definition/sketches/method_mixins/work_planes.py#L2) | `line, plane, angle, construction=True, component_definition=None` | Создать рабочую плоскость по линии, плоскости и углу; construction задаёт вспомогательный тип. |
| [`add_offset_work_plane()`](inventor_service/part/component_definition/sketches/method_mixins/work_planes.py#L19) | `face_or_plane, offset, name=None, visible=False, component_definition=None` | Создать рабочую плоскость со смещением offset; при необходимости назначить имя и видимость. |

## Параметры детали

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`parameter()`](inventor_service/part/component_definition/core.py#L42) | `name` | Получить параметр по имени из общей коллекции Parameters. |
| [`user_parameter()`](inventor_service/part/component_definition/core.py#L87) | `name` | Получить пользовательский параметр по имени. |
| [`model_parameter()`](inventor_service/part/component_definition/core.py#L90) | `name` | Получить параметр модели по имени. |
| [`parameter_exists()`](inventor_service/part/component_definition/core.py#L49) | `name, component_definition=None` | Проверить наличие параметра по имени. |
| [`missing_parameters()`](inventor_service/part/component_definition/core.py#L58) | `names, component_definition=None` | Вернуть имена отсутствующих параметров из списка names. |
| [`parameter_value()`](inventor_service/part/component_definition/core.py#L65) | `name, default=None, component_definition=None` | Вернуть Value параметра во внутренних единицах; при ошибке default. |
| [`parameter_expression()`](inventor_service/part/component_definition/core.py#L73) | `name, default=None, component_definition=None` | Вернуть строку Expression параметра; при ошибке default. |
| [`parameter_expressions()`](inventor_service/part/component_definition/core.py#L116) | `names, component_definition=None` | Вернуть словарь выражений существующих параметров из names. |
| [`set_parameter()`](inventor_service/part/component_definition/core.py#L93) | `name, expression` | Назначить параметру выражение и вернуть объект параметра. |
| [`set_parameter_expression()`](inventor_service/part/component_definition/core.py#L81) | `name, expression, component_definition=None` | Назначить выражение параметру по имени; можно указать component_definition. |
| [`add_user_parameter()`](inventor_service/part/component_definition/core.py#L98) | `name, expression, units='mm'` | Создать пользовательский параметр через AddByExpression с указанными units. |
| [`ensure_user_parameter()`](inventor_service/part/component_definition/core.py#L101) | `name, expression, units='mm', component_definition=None` | Вернуть существующий параметр или создать пользовательский; выражение существующего не меняет. |
| [`restore_missing_parameters()`](inventor_service/part/component_definition/core.py#L123) | `expressions, units='mm', component_definition=None` | Восстановить отсутствующие параметры из словаря выражений; вернуть признак наличия восстановленных. |
| [`ensure_keep_parameter()`](inventor_service/part/component_definition/core.py#L145) | `name, referenced_parameter_names, units='mm', component_definition=None` | Создать или обновить параметр с нулевыми ссылками на перечисленные параметры, чтобы сохранить зависимости. |
| [`unique_parameter_name()`](inventor_service/part/component_definition/core.py#L45) | `base, parameters=None, separator='_'` | Подобрать свободное имя параметра с указанным separator. |
| [`set_parameter_name()`](inventor_service/part/component_definition/sketches/drilling.py#L109) | `parameter_owner, name` | Назначить имя параметру объекта parameter_owner.Parameter, например размерной зависимости. |

## Операции и отверстия

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`feature()`](inventor_service/part/component_definition/core.py#L166) | `name` | Получить операцию по имени. |
| [`unique_feature_name()`](inventor_service/part/component_definition/core.py#L172) | `base, features=None` | Подобрать свободное имя операции; поддерживает также старый порядок аргументов (коллекция, имя). |
| [`set_all_bodies_affected()`](inventor_service/part/component_definition/features/hole_features/methods.py#L5) | `feature, component_definition=None` | Попытаться распространить операцию на все тела многотельной детали. |
| [`add_holes()`](inventor_service/part/component_definition/features/hole_features/methods.py#L22) | `points, diameter, depth, direction=20993, name=None, flat_bottom=True, affect_all_bodies=True, component_definition=None` | Создать отверстия по SketchPoint с диаметром diameter и глубиной depth; flat_bottom задаёт плоское дно. |
| [`add_counterbore_holes()`](inventor_service/part/component_definition/features/hole_features/methods.py#L60) | `points, hole_diameter, hole_depth, direction, counterbore_diameter, counterbore_depth, name=None, affect_all_bodies=True, component_definition=None` | Создать отверстия с цековкой по точкам; отдельно задать размеры отверстия и цековки. |
| [`add_hole_batch()`](inventor_service/part/component_definition/features/hole_features/methods.py#L112) | `points, diameter, depth, direction=20993, name=None, **kwargs` | Передать пакет точек в add_holes(); дополнительные настройки передаются через kwargs. |
| [`add_counterbore_batch()`](inventor_service/part/component_definition/features/hole_features/methods.py#L130) | `points, hole_diameter, hole_depth, direction, counterbore_diameter, counterbore_depth, name=None, **kwargs` | Передать пакет точек в add_counterbore_holes(); дополнительные настройки передаются через kwargs. |
| [`create_hole_batch_with_fallback()`](inventor_service/part/component_definition/features/hole_features/methods.py#L152) | `jobs, points_key, settings, defaults=None, label='Hole'` | Попытаться создать общую операцию по точкам всех jobs; при ошибке создавать операции по заданиям отдельно. |

## Эскизы для сверления

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`ensure_drilling_sketch_parameters()`](inventor_service/part/component_definition/sketches/drilling.py#L16) | — | Проверить наличие параметров отступа рамки и ящика; вернуть bool, параметры не создаёт. |
| [`edge_offset_param_for_length()`](inventor_service/part/component_definition/sketches/drilling.py#L21) | `long_edge_length` | Выбрать имя параметра отступа по длине и порогу drawer_edge_max_cm из настроек. |
| [`create_construction_axes()`](inventor_service/part/component_definition/sketches/drilling.py#L28) | `sketch, short1, short2` | Создать продольную и поперечную вспомогательные оси по серединам двух коротких рёбер; вернуть оси и расчётные данные. |
| [`create_drilling_points()`](inventor_service/part/component_definition/sketches/drilling.py#L56) | `sketch, center, ux, uy, point_distance_value` | Создать четыре точки сверления и центральную точку вдоль (ux, uy); вернуть точки и половину межосевого расстояния. |
| [`constrain_drilling_points()`](inventor_service/part/component_definition/sketches/drilling.py#L80) | `sketch, axis, symmetry_axis, points` | Привязать точки сверления к продольной оси и задать симметрию относительно поперечной. |
| [`add_side_plane_reference_line()`](inventor_service/part/component_definition/sketches/drilling.py#L90) | `sketch, axis, lines` | Создать вспомогательную линию к одному из длинных рёбер и задать перпендикулярность продольной оси. |
| [`add_drilling_dimensions()`](inventor_service/part/component_definition/sketches/drilling.py#L119) | `sketch, axes, points, index, edge_offset_param` | Добавить размеры схемы сверления; задать межосевое выражение с шагом 32 mm и отступом edge_offset_param. |
| [`create_drilling_sketch()`](inventor_service/part/component_definition/sketches/drilling.py#L174) | `sketch, face, index, edge_offset_param='Edge_offset'` | Заполнить переданный эскиз схемой сверления для грани: проекции, оси, точки, зависимости и размеры; вернуть bool. |
| [`create_drilling_sketches_for_faces()`](inventor_service/part/component_definition/sketches/drilling.py#L216) | `faces, sketch_prefix='DrillingSketch', edge_offset_param=None, sketch_label='Drilling', face_label='Selected drilling', reuse_existing=True` | Обработать грани по группам плоскостей; reuse_existing управляет поиском эскизов. Вернуть счётчики и список эскизов. |
| [`create_drawer_drilling_sketches_for_faces()`](inventor_service/part/component_definition/sketches/drilling.py#L297) | `faces, **kwargs` | Выполнить создание эскизов сверления с префиксом и подписями для ящиков; остальные настройки через kwargs. |

## Конфигурации и сценарии

| Метод | Параметры | Краткое пояснение |
| --- | --- | --- |
| [`load_part_config()`](inventor_service/part/component_definition/features/configured.py#L12) | `path` | Прочитать JSON-конфигурацию из path и вернуть словарь. |
| [`validate_linked_parameters()`](inventor_service/part/component_definition/features/configured.py#L16) | `names` | Проверить наличие параметров из names; при отсутствии вызвать ValueError, иначе True. |
| [`resolve_config_parameter_name()`](inventor_service/part/component_definition/features/configured.py#L32) | `name, config` | Разрешить имя параметра с учётом алиасов config и проверить наличие параметра в модели. |
| [`apply_part_config()`](inventor_service/part/component_definition/features/configured.py#L37) | `config` | Принять словарь или путь к JSON, проверить параметры, выполнить операции конфигурации и обновить деталь. |
| [`apply_part_operation()`](inventor_service/part/component_definition/features/configured.py#L57) | `operation, config=None` | Выполнить операцию из словаря; сейчас поддерживается center_hole_on_selected_face, неизвестный тип вызывает ValueError. |

## Пример: центр предварительно выделенной грани

Выделите прямоугольную плоскую грань в Inventor и запустите:

```python
from inventor_service import get_inventor_service

service = get_inventor_service()
face = service.selected_planar_face()
point = service.add_face_center_point(face, hole_center=False)
service.update()
```

`add_face_center_point()` без `sketch` всегда создаёт новый эскиз. Метод проецирует четыре прямых ребра внешнего контура, создаёт вспомогательную диагональ и привязывает точку к её середине. Поддерживает прямоугольники и параллелограммы. Параметры `prefix` и `offsets` оставлены для совместимости и не используются. При явно переданном `sketch` работает в нём. При ошибке транзакция откатывается.

`face_center_in_sketch()` только вычисляет среднее координат вершин и возвращает Point2d; связь с рёбрами не создаёт. `get_or_create_sketch_on_face()` по-прежнему ищет существующий эскиз перед созданием нового.

Сигнатуры и ссылки на реализацию сверены с исходниками библиотеки. Для методов с одинаковым именем в разных миксинах приведён вариант, доступный через `Inventor`.
