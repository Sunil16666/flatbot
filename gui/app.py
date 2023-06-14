import customtkinter as ctk
from components.widgets import MyWidget


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class App:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("FLATBOT")
        self.root.geometry("800x600")
        self.root.resizable(width=True, height=True)

        self.create_widgets()

    def create_widgets(self):
        # Create an instance of the custom widget
        my_widget = MyWidget(self.root)
        my_widget.pack()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
