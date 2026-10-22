class InventorUnitMethods:
    @staticmethod
    def mm(value):
        return value / 10

    @staticmethod
    def mm_text(value):
        if isinstance(value, str):
            return value

        return f"{value} mm"
