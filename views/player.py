import tkinter as tk
from tkinter import Frame, Label
from PIL import Image, ImageTk
import cv2

class Player:
    def __init__(self, parent):
        self.parent = parent
        self.frame_items = []
        self.current_frame_index = 0
        self.is_playing = False

        self.player_main = Frame(self.parent, bg="#212023")
        self.player_main.pack(fill="both", expand=True)

    def display_current_frame(self):
        player_width = self.player_main.winfo_width()
        player_height = self.player_main.winfo_height()

        frame_item = self.frame_items[self.current_frame_index]
        frame = cv2.cvtColor(frame_item.frame, cv2.COLOR_BGR2RGB)

        frame_height, frame_width = frame.shape[:2]
        scale = min(player_width / frame_width, player_height / frame_height)
        new_width = int(frame_width * scale)
        new_height = int(frame_height * scale)

        resized_frame = cv2.resize(frame, (new_width, new_height))
        frame_image = ImageTk.PhotoImage(Image.fromarray(resized_frame))

        if hasattr(self, 'video_label'):
            self.video_label.configure(image=frame_image)
            self.video_label.image = frame_image
        else:
            self.video_label = Label(self.player_main, image=frame_image, bg="#212023")
            self.video_label.pack(fill="both", expand=True)

    def display_frame_list(self, frame_items):
        self.frame_items = frame_items
        self.current_frame_index = 0
        if frame_items:
            self.display_current_frame()
