class InventorUIMethods:
    def pick(self, selection_filter, prompt_text="Select object"):
        return self.app.CommandManager.Pick(selection_filter, prompt_text)

    @staticmethod
    def show_message(title, text, icon="info"):
        icons = {
            "info": 0x40,
            "warning": 0x30,
            "error": 0x10,
            "question": 0x20,
        }

        ctypes = __import__("ctypes")
        return ctypes.windll.user32.MessageBoxW(
            0,
            str(text),
            str(title),
            icons.get(icon, icons["info"]),
        )

    def show_missing_parameters_message(self, names, title="Missing parameters"):
        return self.show_message(title, "\n".join(names), icon="warning")
