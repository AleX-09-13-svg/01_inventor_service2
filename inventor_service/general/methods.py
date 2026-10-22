from .method_mixins import (
    InventorDirectionMethods,
    InventorDocumentMethods,
    InventorScreenMethods,
    InventorUIMethods,
    InventorUnitMethods,
    InventorUtilityMethods,
)


# InventorBaseMethods - это "сборщик" общих методов Inventor.
#
# Где искать реализацию:
# - InventorDocumentMethods: активный документ, имя документа, имя детали.
# - InventorUnitMethods: миллиметры и текстовые выражения с единицами.
# - InventorDirectionMethods: направления отверстий и ориентации размеров.
# - InventorUtilityMethods: безопасные утилиты и ObjectCollection.
# - InventorUIMethods: выбор объектов и сообщения пользователю.
# - InventorScreenMethods: временное отключение обновления экрана.
#
# Сам класс ниже не содержит новой логики. Он объединяет эти mixin-классы,
# чтобы остальные классы библиотеки могли наследовать один общий набор методов.
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
    """
    Базовый набор общих методов Inventor.

    Этот класс нужен как единая точка входа к общим методам:
    update(), active_document_name(), mm(), mm_text(), hole_direction(),
    object_collection(), pick(), screen_updates_suspended() и другим.

    Реализация методов разнесена по файлам в папке general/method_mixins.
    """

    pass


# Старое публичное имя оставлено для обратной совместимости.
InventorMethods = InventorBaseMethods
