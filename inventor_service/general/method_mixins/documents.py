class InventorDocumentMethods:
    def update(self):
        self.active_document.Update()

    def active_document_name(self):
        """Вернуть DisplayName активного документа."""
        return self.active_document.DisplayName

    def active_part_name(self):
        """Алиас для имени активной детали."""
        return self.active_document_name()
