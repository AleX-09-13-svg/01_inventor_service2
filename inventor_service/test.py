from inventor_service import Inventor

if __name__ == "__main__":
    # Шаг 1. Подключаемся к уже запущенному Inventor.
    # Шаг 1. Подключаемся к уже запущенному Inventor.
    inventor = Inventor()
    print("Активный документ:", inventor.active_document_name())

    # Шаг 2. Получаем заранее выделенную плоскую грань детали.
    face = inventor.selected_face()
    print("Плоская грань получена.")
