from contextlib import contextmanager


class InventorScreenMethods:
    @contextmanager
    def screen_updates_suspended(self):
        try:
            previous = self.app.ScreenUpdating
            self.app.ScreenUpdating = False
        except Exception:
            previous = None

        try:
            yield self
        finally:
            if previous is not None:
                try:
                    self.app.ScreenUpdating = previous
                except Exception:
                    pass
