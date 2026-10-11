class InventorProperties:
    def __init__(self, app=None, visible=True):
        self.app = app or self.get_application(visible=visible)

    @classmethod
    def get_application(cls, visible=True):
        pythoncom = __import__("pythoncom")
        dynamic = __import__("win32com.client.dynamic", fromlist=["Dispatch"])

        inventor_unknown = pythoncom.GetActiveObject("Inventor.Application")
        inventor_dispatch = inventor_unknown.QueryInterface(pythoncom.IID_IDispatch)
        app = dynamic.Dispatch(inventor_dispatch)

        if visible is not None:
            app.Visible = visible

        return app

    @property
    def active_document(self):
        return self.app.ActiveDocument

    @property
    def doc(self):
        return self.active_document

    @property
    def component_definition(self):
        return self.active_document.ComponentDefinition

    @property
    def comp(self):
        return self.component_definition

    @property
    def transient_objects(self):
        return self.app.TransientObjects

    @property
    def transient_geometry(self):
        return self.app.TransientGeometry

    @property
    def select_set(self):
        return self.active_document.SelectSet
