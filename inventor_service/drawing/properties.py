class DrawingProperties:
    @property
    def drawing_document(self):
        return self.active_document

    @property
    def sheets(self):
        return self.drawing_document.Sheets
