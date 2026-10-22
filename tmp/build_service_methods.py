import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from inventor_service import Inventor

# Группы и пояснения; параметры и ссылки берутся из действующего API.
CATALOG = '''
## Подключение, документы и общие утилиты
get_application|Подключиться к уже работающему Inventor; visible задаёт видимость, None сохраняет текущее значение. Приложение не запускает.
active_document_name|Вернуть DisplayName активного документа.
active_part_name|Вернуть имя активного документа; алиас active_document_name().
update|Обновить активный документ.
update_part|Обновить документ детали и вернуть его.
save_part|Сохранить документ детали и вернуть его.
save_part_as|Сохранить деталь в file_name; save_copy_as=True сохраняет копию.
screen_updates_suspended|Контекстный менеджер для with: временно отключить обновление экрана и восстановить исходное состояние.
safe_getattr|Прочитать атрибут attr; при ошибке вернуть default.
object_collection|Создать COM ObjectCollection из переданных объектов.
unique_collection_name|Подобрать свободное имя в COM-коллекции, добавляя separator и числовой суффикс.
show_message|Показать системное сообщение с заголовком, текстом и значком icon.
show_missing_parameters_message|Показать сообщение со списком отсутствующих параметров.
## Единицы, направления и ориентация
mm|Перевести миллиметры во внутренние единицы длины Inventor — сантиметры.
mm_text|Сформировать выражение размера с суффиксом mm.
hole_direction|Преобразовать название или значение направления в константу Inventor.
opposite_hole_direction|Вернуть противоположное направление отверстия.
dimension_orientation|Преобразовать horizontal, vertical или aligned в константу ориентации размера.
## Выбор объектов и выделенные грани
pick|Запросить выбор объекта по фильтру selection_filter с подсказкой prompt_text.
pick_part|Запросить выбор компонента детали в сборке.
pick_face|Запросить выбор грани; planar=True ограничивает выбор плоскими гранями.
pick_faces_until_cancel|Запрашивать грани до отмены и вернуть список без повторов.
selected_faces|Вернуть грани из текущего выделения; debug включает диагностический вывод.
require_selected_faces|Вернуть выделенные грани или вызвать RuntimeError, если их меньше min_count; planar фильтрует плоские.
selected_face|Вернуть первую выделенную плоскую грань; при отсутствии вызвать ошибку.
selected_planar_face|Вернуть выделенную грань с дополнительной проверкой плоской геометрии.
selected_faces_by_color|Вернуть выделенные грани заданного цвета; без color_name вернуть все выделенные грани.
selected_faces_grouped_by_plane|Сгруппировать выделенные грани по совпадающим плоскостям.
selected_faces_grouped_by_plane_and_appearance|Собрать группы выделенных граней по плоскости в словарь по внешнему виду первой грани группы.
face_from_selection_object|Извлечь грань из объекта выделения, включая NativeObject, ContainingFace и SourceObject; иначе вернуть None.
is_face_like|Проверить наличие геометрии, рёбер и вершин, характерных для грани.
is_planar_face|Проверить, что геометрия грани имеет нормаль и базовую точку плоскости.
selection_object_label|Сформировать диагностическую строку с типом и именем объекта выделения.
selected_face_vertex_points_xy|Создать новый эскиз на выделенной плоской грани и вернуть координаты её вершин как пары (x, y).
selected_face_vertex_report|Создать эскиз и вернуть словарь: имя документа, количество вершин и координаты вершин.
## Тела, грани, рёбра и вершины
all_surface_bodies|Вернуть тела детали в ObjectCollection.
surface_body|Вернуть тело по индексу; нумерация начинается с 1.
all_faces|Вернуть список граней всех тел детали.
unique_faces|Убрать повторяющиеся грани по ReferenceKey или идентичности объекта.
face_key|Вернуть ReferenceKey грани; при недоступности использовать id объекта.
face_vertices|Вернуть список вершин грани.
face_vertex_count|Вернуть количество вершин грани.
face_vertex_points|Вернуть 3D-точки вершин грани.
face_edges|Вернуть список рёбер грани.
edge_faces|Вернуть грани ребра через Faces или TangentiallyConnectedFaces; иначе пустой список.
shared_face_edge|Найти общее ребро двух граней; при отсутствии вернуть None.
adjacent_faces|Вернуть соседние грани, связанные общими рёбрами, без повторов.
adjacent_face_count|Посчитать грани из faces, имеющие общее ребро хотя бы с одной гранью из other_faces.
face_area|Прочитать площадь грани напрямую или через Evaluator; при недоступности вернуть None.
faces_area|Суммировать площади граней; недоступные площади считать нулевыми.
face_model_bounds|Вернуть границы по вершинам: (min_x, max_x, min_y, max_y, min_z, max_z).
point_inside_model_bounds|Проверить попадание 3D-точки в указанные границы с допуском tol.
candidate_faces_by_normal_axis|Найти плоские грани с нормалью вдоль x, y или z и заданной координатой плоскости.
## Плоскости и нормали
plane_geometry|Получить геометрию плоскости через Geometry или Plane.
plane_normal|Вернуть нормаль плоскости.
face_normal|Вернуть нормаль плоской грани.
plane_root_point|Вернуть базовую точку плоскости.
plane_key|Сформировать ключ плоскости из нормализованного направления нормали и расстояния с округлением по tol.
same_plane_entity|Проверить параллельность нормалей и допустимое расстояние между плоскостями; offsets=None означает нулевое смещение.
same_plane|Проверить совпадение плоскостей двух граней с допуском tol.
same_offset_plane_entity|Проверить параллельность и заданное абсолютное смещение плоскостей.
group_faces_by_plane|Сгруппировать грани по совпадающим плоскостям.
## Цвет и внешний вид
face_appearance_text|Собрать названия внешнего вида грани и её родителя в строку.
face_appearance_key|Вернуть распознанное имя цвета или нормализованный текст внешнего вида.
face_color|Получить COM-объект цвета грани или её родителя; при отсутствии вернуть None.
face_color_rgb|Вернуть RGB цвета грани; при недоступности вернуть None.
detected_face_rgb|Определить RGB напрямую или по распознанному имени цвета.
is_face_color|Проверить цвет грани по названию внешнего вида или RGB.
faces_by_color|Сгруппировать все грани детали в словарь по ключу внешнего вида.
colored_faces|Вернуть грани детали, соответствующие color_name.
reset_faces_to_feature_appearance|Сбросить ручное оформление граней к внешнему виду операции; вернуть число успешных сбросов.
set_sketch_color|Задать цвет эскиза по имени, RGB или COM-объекту; include_entities распространяет цвет на линии и точки.
set_sketch_color_rgb|Задать цвет эскиза через кортеж RGB.
set_sketch_color_from_face|Скопировать распознанный цвет грани в эскиз; при неизвестном цвете вернуть эскиз без изменения.
## Создание и поиск эскизов
add_sketch|Всегда создать новый эскиз на planar_entity; при наличии name назначить имя.
all_sketches|Вернуть список эскизов детали.
sketches_by_prefix|Вернуть эскизы, имена которых начинаются с prefix.
unique_sketch_name|Подобрать свободное имя эскиза с числовым суффиксом при необходимости.
sketch_on_face_plane|Найти эскиз на плоскости грани с учётом prefix и допустимых offsets; иначе None.
sketch_on_offset_face_plane|Найти эскиз с заданным префиксом на плоскости, смещённой относительно грани.
get_or_create_sketch_on_face|Найти подходящий эскиз на плоскости грани; при отсутствии создать новый с name.
## Координаты и точки
create_point2d|Создать Point2d через TransientGeometry.
create_point3d|Создать 3D Point через TransientGeometry.
model_to_sketch_point|Перевести 3D-точку модели в 2D-координаты эскиза.
model_to_sketch_points|Перевести список 3D-точек в координаты эскиза.
model_to_sketch_points_from_vertices|Перевести COM-коллекцию вершин в список 2D-точек эскиза.
face_vertex_points_in_sketch|Вернуть точки вершин грани в координатах эскиза.
face_bounds_in_sketch|Вернуть границы по вершинам в эскизе: (min_x, max_x, min_y, max_y).
face_center_in_sketch|Вычислить среднее арифметическое координат вершин грани; зависимостей не создаёт.
sketch_to_model_points|Перевести список SketchPoint в список 3D-точек модели.
sketch_points_to_model|Алиас преобразования списка SketchPoint в 3D-точки модели.
add_sketch_point|Добавить точку в эскиз; hole_center=True помечает её центром отверстия.
add_face_center_point|Создать центр прямоугольной грани или параллелограмма: проекции внешних рёбер, вспомогательная диагональ и зависимость середины. Без sketch всегда новый эскиз. prefix и offsets не используются.
sketch_points|Вернуть точки эскиза; hole_center=None отключает фильтр, True или False фильтруют по признаку центра отверстия.
sketch_point_count|Вернуть число точек эскиза.
set_point_hole_center|Установить признак центра отверстия; при ошибке вернуть None.
sketch_hole_center_points|Вернуть только точки, отмеченные центрами отверстий.
unique_points|Убрать повторяющиеся SketchPoint по координатам с округлением до 6 знаков.
mark_as_hole_centers|Пометить переданные точки центрами отверстий, пропуская ошибки записи.
point_inside_sketch_bounds|Проверить попадание точки или пары (x, y) в прямоугольные границы с допуском tol.
## Проекция геометрии
project_entity_to_sketch|Спроецировать объект в эскиз; construction задаёт вспомогательный тип, ignore_errors управляет обработкой ошибок.
project_face_edges|Спроецировать рёбра грани и вернуть число успешных проекций.
project_point_to_plane|Получить проекцию точки через доступный ProjectPoint или GetClosestPointTo; при отсутствии API вызвать ошибку.
project_points_to_plane|Спроецировать список точек на плоский объект.
offset_model_points_from_face|Сместить точки вдоль нормали грани на offset с множителем direction.
## Линии и расчёты в эскизе
add_sketch_line|Создать линию по двум Point2d или SketchPoint; construction=True делает её вспомогательной.
set_entity_construction|Установить вспомогательный тип объекта; при ошибке вернуть None.
sketch_lines|Вернуть линии эскиза; construction=None отключает фильтр по вспомогательному типу.
sketch_line_count|Вернуть число линий эскиза.
sketch_has_lines_or_points|Проверить наличие хотя бы одной линии или точки в эскизе.
sketch_has_geometry_for_face|Проверить наличие минимум двух линий в границах грани.
sketch_lines_for_face|Вернуть линии в границах вершин грани; first_new_line пропускает первые линии списка.
distance_2d|Вычислить расстояние между двумя 2D-точками.
line_length|Вычислить длину линии по координатам концов.
line_length_squared|Вычислить квадрат длины линии без извлечения корня.
line_midpoint|Вернуть Point2d середины линии.
line_midpoint_xy|Вернуть координаты середины линии как пару (x, y).
line_data|Вернуть начало, конец и компоненты вектора линии: (start, end, dx, dy).
vector_length2d|Вычислить длину 2D-вектора (dx, dy).
closest_point_on_line|Найти ближайшую точку на отрезке с ограничением параметра диапазоном от 0 до 1.
## Геометрические зависимости
add_ground_constraint|Зафиксировать объект эскиза; ignore_errors управляет подавлением ошибок.
fix_sketch_entity|Зафиксировать один объект, подавляя ошибки.
fix_sketch_points|Зафиксировать список точек, подавляя ошибки отдельных зависимостей.
add_midpoint_constraint|Привязать SketchPoint к середине линии.
add_coincident_constraint|Добавить зависимость совпадения объектов, например точки и линии.
add_parallel_constraint|Добавить параллельность двух линий.
add_perpendicular_constraint|Добавить перпендикулярность двух линий.
add_symmetry_constraint|Добавить симметрию двух объектов относительно symmetry_line.
## Размеры эскиза
add_two_point_dimension|Добавить размер между двумя точками с orientation; driven=True создаёт справочный размер, expression задаёт выражение.
add_aligned_dimension|Добавить выровненный размер между точками; text_point задаёт положение текста.
sketch_dimension_constraints|Вернуть список размерных зависимостей эскиза.
sketch_dimension_count|Вернуть количество размерных зависимостей.
## Видимость и пересчёт эскиза
solve_sketch|Выполнить Solve(); ignore_errors=False позволяет передать ошибку вызывающему коду.
solve_or_update_sketch|Попытаться решить эскиз; при отсутствии результата обновить документ.
set_sketch_defer_updates|Установить отложенное обновление и вернуть предыдущее значение; при ошибке None.
deferred_sketch_updates|Контекстный менеджер для with: включить отложенный пересчёт и восстановить исходное значение при выходе.
set_sketch_visible|Установить видимость эскиза; при ошибке вернуть None.
set_sketch_dimensions_visible|Установить видимость размеров эскиза.
hide_sketch_dimensions|Скрыть размеры эскиза.
show_sketch_dimensions|Показать размеры эскиза.
try_share_sketch|Попытаться включить общий доступ и видимость эскиза через доступные свойства и ShareSketch().
## Рабочие плоскости, оси и точки
work_plane|Получить рабочую плоскость по индексу или имени.
work_axis|Получить рабочую ось по индексу или имени.
work_point|Получить рабочую точку по индексу или имени.
unique_work_plane_name|Подобрать свободное имя рабочей плоскости.
create_work_plane_by_line_plane_angle|Создать рабочую плоскость по линии, плоскости и углу; construction задаёт вспомогательный тип.
add_offset_work_plane|Создать рабочую плоскость со смещением offset; при необходимости назначить имя и видимость.
## Параметры детали
parameter|Получить параметр по имени из общей коллекции Parameters.
user_parameter|Получить пользовательский параметр по имени.
model_parameter|Получить параметр модели по имени.
parameter_exists|Проверить наличие параметра по имени.
missing_parameters|Вернуть имена отсутствующих параметров из списка names.
parameter_value|Вернуть Value параметра во внутренних единицах; при ошибке default.
parameter_expression|Вернуть строку Expression параметра; при ошибке default.
parameter_expressions|Вернуть словарь выражений существующих параметров из names.
set_parameter|Назначить параметру выражение и вернуть объект параметра.
set_parameter_expression|Назначить выражение параметру по имени; можно указать component_definition.
add_user_parameter|Создать пользовательский параметр через AddByExpression с указанными units.
ensure_user_parameter|Вернуть существующий параметр или создать пользовательский; выражение существующего не меняет.
restore_missing_parameters|Восстановить отсутствующие параметры из словаря выражений; вернуть признак наличия восстановленных.
ensure_keep_parameter|Создать или обновить параметр с нулевыми ссылками на перечисленные параметры, чтобы сохранить зависимости.
unique_parameter_name|Подобрать свободное имя параметра с указанным separator.
set_parameter_name|Назначить имя параметру объекта parameter_owner.Parameter, например размерной зависимости.
## Операции и отверстия
feature|Получить операцию по имени.
unique_feature_name|Подобрать свободное имя операции; поддерживает также старый порядок аргументов (коллекция, имя).
set_all_bodies_affected|Попытаться распространить операцию на все тела многотельной детали.
add_holes|Создать отверстия по SketchPoint с диаметром diameter и глубиной depth; flat_bottom задаёт плоское дно.
add_counterbore_holes|Создать отверстия с цековкой по точкам; отдельно задать размеры отверстия и цековки.
add_hole_batch|Передать пакет точек в add_holes(); дополнительные настройки передаются через kwargs.
add_counterbore_batch|Передать пакет точек в add_counterbore_holes(); дополнительные настройки передаются через kwargs.
create_hole_batch_with_fallback|Попытаться создать общую операцию по точкам всех jobs; при ошибке создавать операции по заданиям отдельно.
## Эскизы для сверления
ensure_drilling_sketch_parameters|Проверить наличие параметров отступа рамки и ящика; вернуть bool, параметры не создаёт.
edge_offset_param_for_length|Выбрать имя параметра отступа по длине и порогу drawer_edge_max_cm из настроек.
create_construction_axes|Создать продольную и поперечную вспомогательные оси по серединам двух коротких рёбер; вернуть оси и расчётные данные.
create_drilling_points|Создать четыре точки сверления и центральную точку вдоль (ux, uy); вернуть точки и половину межосевого расстояния.
constrain_drilling_points|Привязать точки сверления к продольной оси и задать симметрию относительно поперечной.
add_side_plane_reference_line|Создать вспомогательную линию к одному из длинных рёбер и задать перпендикулярность продольной оси.
add_drilling_dimensions|Добавить размеры схемы сверления; задать межосевое выражение с шагом 32 mm и отступом edge_offset_param.
create_drilling_sketch|Заполнить переданный эскиз схемой сверления для грани: проекции, оси, точки, зависимости и размеры; вернуть bool.
create_drilling_sketches_for_faces|Обработать грани по группам плоскостей; reuse_existing управляет поиском эскизов. Вернуть счётчики и список эскизов.
create_drawer_drilling_sketches_for_faces|Выполнить создание эскизов сверления с префиксом и подписями для ящиков; остальные настройки через kwargs.
## Конфигурации и сценарии
load_part_config|Прочитать JSON-конфигурацию из path и вернуть словарь.
validate_linked_parameters|Проверить наличие параметров из names; при отсутствии вызвать ValueError, иначе True.
resolve_config_parameter_name|Разрешить имя параметра с учётом алиасов config и проверить наличие параметра в модели.
apply_part_config|Принять словарь или путь к JSON, проверить параметры, выполнить операции конфигурации и обновить деталь.
apply_part_operation|Выполнить операцию из словаря; сейчас поддерживается center_hole_on_selected_face, неизвестный тип вызывает ValueError.
'''

methods = {
    name: method
    for name, method in inspect.getmembers(Inventor, callable)
    if not name.startswith('_')
}
groups = []
seen = set()
for line in CATALOG.strip().splitlines():
    if line.startswith('## '):
        groups.append((line[3:], []))
        continue
    name, description = line.split('|', 1)
    assert name in methods, f'Unknown method: {name}'
    assert name not in seen, f'Duplicate: {name}'
    seen.add(name)
    groups[-1][1].append((name, description))
assert seen == set(methods), f'Missing: {sorted(set(methods) - seen)}'

def code(value):
    return '`' + value.replace('|', '&#124;') + '`'

lines = [
    '# Методы объекта service', '',
    '`get_inventor_service()` возвращает объект `Inventor`. В текущей версии у него '
    f'**{len(methods)} публичных методов**, включая унаследованные. '
    'Каждый метод указан один раз с учётом порядка наследования.', '',
    '```python', 'from inventor_service import get_inventor_service', '',
    'service = get_inventor_service()', '```', '',
    'Вызов: `service.имя_метода(...)`. В таблицах параметр `self` опущен: передавать его не нужно. '
    'Параметры со значениями по умолчанию необязательны. '
    'Свойства (`app`, `doc`, `comp` и другие), константы и имена с начальным `_` в число методов не входят.', '',
    '## Подключение сервиса', '',
    '| Функция | Параметры | Назначение |', '| --- | --- | --- |',
    '| `get_inventor_service()` | `app=None, visible=True` | Создать сервис; app позволяет передать COM-приложение Inventor. Функция модуля, в 186 методов объекта не включена. |', '',
    '## Общие параметры', '',
    '| Параметр | Значение |', '| --- | --- |',
    '| `face`, `sketch`, `entity` | COM-объект грани, эскиза или другой геометрической сущности. |',
    '| `component_definition=None` | Используется компонент активной детали. |',
    '| `name`, `prefix` | Точное имя объекта и префикс для фильтрации по имени. |',
    '| `tol` | Числовой допуск сравнения. |',
    '| `ignore_errors=True` | Подавлять ошибки операции; False передаёт исключение вызывающему коду. |',
    '| `construction=True` | Вспомогательная геометрия эскиза. |',
    '| `hole_center=True` | Точка эскиза является центром отверстия. |',
    '| `driven=True` | Справочный размер, который измеряет геометрию. |',
    '| `expression` | Выражение Inventor, например `"32 mm"` или имя параметра. |',
    '| `**kwargs` | Дополнительные именованные настройки вложенного метода. |', '',
    'Числовые координаты и длины во внутренних единицах Inventor задаются в сантиметрах; '
    '`service.mm(10)` переводит 10 мм в 1 см. Для размерных выражений можно использовать строки с единицами. '
    'Значение направления `20993` в сигнатурах — `kPositiveExtentDirection`.', '',
    '## Разделы', '',
]
for title, rows in groups:
    count = len(rows)
    word = 'методов' if 11 <= count % 100 <= 14 else {1: 'метод', 2: 'метода', 3: 'метода', 4: 'метода'}.get(count % 10, 'методов')
    lines.append(f'- {title} — {count} {word}.')
lines.append('')
for title, rows in groups:
    lines += [f'## {title}', '', '| Метод | Параметры | Краткое пояснение |', '| --- | --- | --- |']
    for name, description in rows:
        method = methods[name]
        signature = inspect.signature(method)
        signature = signature.replace(parameters=[
            p for p in signature.parameters.values() if p.name not in ('self', 'cls')
        ])
        params = str(signature)[1:-1] or '—'
        source_method = inspect.unwrap(method)
        source = Path(inspect.getsourcefile(source_method)).relative_to(ROOT).as_posix()
        line_number = inspect.getsourcelines(source_method)[1]
        label = f'[{code(name + "()")}]({source}#L{line_number})'
        lines.append(f'| {label} | {code(params) if params != "—" else params} | {description} |')
    lines.append('')
lines += [
    '## Пример: центр предварительно выделенной грани', '',
    'Выделите прямоугольную плоскую грань в Inventor и запустите:', '',
    '```python', 'from inventor_service import get_inventor_service', '',
    'service = get_inventor_service()', 'face = service.selected_planar_face()',
    'point = service.add_face_center_point(face, hole_center=False)',
    'service.update()', '```', '',
    '`add_face_center_point()` без `sketch` всегда создаёт новый эскиз. '
    'Метод проецирует четыре прямых ребра внешнего контура, создаёт вспомогательную диагональ '
    'и привязывает точку к её середине. Поддерживает прямоугольники и параллелограммы. '
    'Параметры `prefix` и `offsets` оставлены для совместимости и не используются. '
    'При явно переданном `sketch` работает в нём. При ошибке транзакция откатывается.', '',
    '`face_center_in_sketch()` только вычисляет среднее координат вершин и возвращает Point2d; '
    'связь с рёбрами не создаёт. '
    '`get_or_create_sketch_on_face()` по-прежнему ищет существующий эскиз перед созданием нового.', '',
    'Сигнатуры и ссылки на реализацию сверены с исходниками библиотеки. '
    'Для методов с одинаковым именем в разных миксинах приведён вариант, доступный через `Inventor`.', '',
]
target = ROOT / 'service_methods.md'
target.write_text('\n'.join(lines), encoding='utf-8')
content = target.read_text(encoding='utf-8')
assert content.count('| [`') == len(methods)
print(f'Created service_methods.md: {len(methods)} methods, {len(groups)} groups, {len(lines)} lines')
