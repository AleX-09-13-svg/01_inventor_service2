from contextlib import contextmanager


class PartSketchStateMethods:
    @staticmethod
    def solve_sketch(sketch, ignore_errors=True):
        """Выполнить Solve() для эскиза."""
        try:
            return sketch.Solve()
        except Exception:
            if not ignore_errors:
                raise

            return None

    @staticmethod
    def set_sketch_defer_updates(sketch, value):
        """Safely set sketch.DeferUpdates and return its previous value."""
        try:
            previous = sketch.DeferUpdates
            sketch.DeferUpdates = value
        except Exception:
            return None

        return previous

    @contextmanager
    def deferred_sketch_updates(self, sketch):
        """Temporarily enable DeferUpdates and restore the original value."""
        previous = self.set_sketch_defer_updates(sketch, True)
        try:
            yield sketch
        finally:
            if previous is not None:
                self.set_sketch_defer_updates(sketch, previous)

    @staticmethod
    def set_sketch_dimensions_visible(sketch, visible):
        """Safely set sketch.DimensionsVisible."""
        try:
            sketch.DimensionsVisible = visible
        except Exception:
            return None

        return sketch

    def hide_sketch_dimensions(self, sketch):
        return self.set_sketch_dimensions_visible(sketch, False)

    def show_sketch_dimensions(self, sketch):
        return self.set_sketch_dimensions_visible(sketch, True)

    @staticmethod
    def set_sketch_visible(sketch, visible):
        """Safely set sketch.Visible."""
        try:
            sketch.Visible = visible
        except Exception:
            return None

        return sketch

    @staticmethod
    def try_share_sketch(sketch):
        for attr in ("Shared", "Visible"):
            try:
                setattr(sketch, attr, True)
            except Exception:
                pass

        try:
            sketch.ShareSketch()
        except Exception:
            pass

        return sketch

    def solve_or_update_sketch(self, sketch):
        result = self.solve_sketch(sketch, ignore_errors=True)
        if result is not None:
            return result

        try:
            return sketch.Parent.Document.Update()
        except Exception:
            return self.update()
