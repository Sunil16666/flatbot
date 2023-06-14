import customtkinter as ctk
# from ..CTkRangeSlider import *

class MyWidget(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master, bg_color="#FFFFFF", fg_color="#1b1a1a")
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        # Create a label
        title = ctk.CTkLabel(self,
                             text="FlatBot | Unlocking Your Dream Home with Python Precision!",
                             font=ctk.CTkFont("Roboto", size=24, weight="bold"),
                             )

        title.pack(pady=20)

        label_price = ctk.CTkLabel(self,
                                   text="Price",
                                   font=ctk.CTkFont("Robot", size=18, weight="bold"),
                                   )
        label_price.pack(pady=20)

        label_rooms = ctk.CTkLabel(self,
                                   text="Rooms",
                                   font=ctk.CTkFont("Robot", size=18, weight="bold"),
                                   )
        label_rooms.pack(pady=20)

        label_area = ctk.CTkLabel(self,
                                  text="Area",
                                  font=ctk.CTkFont("Robot", size=18, weight="bold"),
                                  )

        label_area.pack(pady=20)

        button_start = ctk.CTkButton(self,
                                     text="START",
                                     font=ctk.CTkFont("Robot", size=18, weight="bold"),
                                     anchor='center'
                                     )
        button_start.pack(pady=10, side='bottom')

        self.pack(fill='both', expand=True)


