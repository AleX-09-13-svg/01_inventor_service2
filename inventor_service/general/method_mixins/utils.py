class InventorUtilityMethods:
    @staticmethod
    def safe_getattr(obj, attr, default=None):
        try:
            return getattr(obj, attr)
        except Exception:
            return default

    def object_collection(self, objects):
        collection = self.transient_objects.CreateObjectCollection()

        for obj in objects:
            collection.Add(obj)

        return collection
