import customtkinter as ctk
from PIL import Image
from pathlib import Path


class MyWidget(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        # Create a label
        label = ctk.CTkLabel(self, text="Hello, CustomTkinter!", font=ctk.CTkFont("Roboto"))
        label.pack()

        # Load and display an image
        try:
            image_path = Path(__file__).resolve().parent.parent / "resources/images/image_1.jpeg"
            ctk_image = ctk.CTkImage(dark_image=Image.open(image_path),
                                     size=(200, 200))
            image_label = ctk.CTkLabel(self, image=ctk_image, text="MEME")
            image_label.image = ctk.CTkLabel(self, image=ctk_image)  # Keep a reference to prevent garbage collection
            image_label.pack()
        except Exception as e:
            print("Error loading image:", e)
