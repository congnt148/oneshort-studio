from tkinter import Frame, Label, Button
from PIL import ImageTk
import threading

class Header:
    def __init__(self, root, open_file_callback):
        self.root = root
        self.open_file_callback = open_file_callback

        screen_width = root.winfo_screenwidth()
        header_frame = Frame(root, bg="#212023", height=44, width=screen_width)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(0)

        padding_frame = Frame(header_frame, bg="#212023", width=60)
        padding_frame.pack(side="left")

        self.logo = ImageTk.PhotoImage(file="assets/images/logo.png")
        logo_label = Label(header_frame, image=self.logo, background="#212023")
        logo_label.pack(side="left", padx=(0, 10), pady=5)

        self.open_button = Button(header_frame, text="Open", bg="white", fg="black", borderwidth=0, relief="flat")
        self.open_button["command"] = self.open_file_with_threading
        self.open_button.pack(side="right", padx=60, pady=5)

    def open_file_with_threading(self):
        threading.Thread(target=self.open_file_callback).start()
