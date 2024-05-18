from tkinter import Frame, Scrollbar, Canvas, Label
from PIL import Image, ImageTk
import cv2

class Timeline:
    def __init__(self, parent):
        self.timeline_main = Frame(parent, bg="#212023", bd=1, relief="solid")
        
        self.scrollbar = Scrollbar(self.timeline_main, orient="horizontal", bg="#212023", highlightbackground="#212023")
        self.scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.timeline_canvas = Canvas(self.timeline_main, bg="#212023", bd=0, xscrollcommand=self.scrollbar.set)
        self.timeline_canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.config(command=self.timeline_canvas.xview)
        
        self.timeline_main.grid_rowconfigure(0, weight=1)
        self.timeline_main.grid_columnconfigure(0, weight=1)

    def display_frames_in_timeline(self, frame_items):
        frame_list_frame = Frame(self.timeline_canvas, bg="#212023")
        frame_list_frame.pack(fill="both", expand=True)

        frame_list_frame.bind("<Configure>", lambda e: self.timeline_canvas.configure(scrollregion=self.timeline_canvas.bbox("all")))

        image_height = self.timeline_main.winfo_height() // 5
        if frame_items:
            image_width = int(frame_items[0].frame.shape[1] * (image_height / frame_items[0].frame.shape[0]))

            for frame_item in frame_items:
                frame = cv2.cvtColor(frame_item.frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (image_width, image_height))
                frame_image = ImageTk.PhotoImage(Image.fromarray(frame))
                
                frame_label = Label(frame_list_frame, image=frame_image)
                frame_label.image = frame_image
                frame_label.pack(side="left", padx=2, pady=2)

        self.timeline_canvas.create_window((0, 0), window=frame_list_frame, anchor="nw")
