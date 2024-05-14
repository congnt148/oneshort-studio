from tkinter import Tk, filedialog, Button, Label, Canvas
import cv2
from PIL import Image, ImageTk
import threading

class MainView:
    def __init__(self, root, presenter):
        self.root = root
        self.presenter = presenter

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"{screen_width}x{screen_height}")

        self.canvas = Canvas(root, width=screen_width, height=screen_height)
        self.canvas.pack()

        label = Label(root, text="Select a video file to crop:")
        label.pack(pady=10)

        browse_button = Button(root, text="Browse", command=self.presenter.select_file)
        browse_button.pack(pady=10)

        start_button = Button(root, text="Start", command=self.presenter.start_crop)
        start_button.pack(pady=10)

        self.input_video_path = ""
        self.playing = True

        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        def play_video():
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.canvas.winfo_width(), self.canvas.winfo_height()))
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
                self.root.update()

                if not self.playing:
                    break
        play_thread = threading.Thread(target=play_video)
        play_thread.start()

    def on_closing(self):
        self.playing = False
        self.root.destroy()
