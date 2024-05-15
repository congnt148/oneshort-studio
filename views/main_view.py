import tkinter as tk
from tkinter import filedialog
from tkinter import Frame, Canvas, Label, Button
from PIL import Image, ImageTk
import cv2
import threading

class MainView:
    def __init__(self, root, presenter):
        self.root = root
        self.presenter = presenter

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"{screen_width}x{screen_height}")

        # Header frame
        header_frame = Frame(root, bg="#212023", height=44, width=screen_width)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(0)

        # Add padding left 60px using an empty frame
        padding_frame = Frame(header_frame, bg="#212023", width=60)
        padding_frame.pack(side="left")

        # Load the PNG image
        self.logo = ImageTk.PhotoImage(file="assets/images/logo.png")
        logo_label = Label(header_frame, image=self.logo, background="#212023")
        logo_label.pack(side="left", padx=(0, 10), pady=5)

        # Place the Start button in header_frame and align it to the right
        self.export_button = Button(header_frame, text="Start", command=self.presenter.start_crop, bg="white", fg="black", borderwidth=0, relief="flat")
        self.export_button.pack(side="right", padx=60, pady=5)
        
        # Place the Browse button in player_main
        self.open_button = Button(header_frame, text="Open", command=self.select_video, bg="white", fg="black", borderwidth=0, relief="flat")
        self.open_button.pack(side="right", padx=60, pady=5)

        # Main canvas
        self.canvas = Canvas(root, width=screen_width, height=screen_height - 44)
        self.canvas.pack(expand=True)

        # Set up column configuration for canvas
        self.canvas.grid_columnconfigure(0, weight=3)  # 30% of width
        self.canvas.grid_columnconfigure(1, weight=7)  # 70% of width

        # Set up row configuration for video_main
        self.canvas.grid_rowconfigure(0, weight=6)  # 60% of height
        self.canvas.grid_rowconfigure(1, weight=4)  # 40% of height

        # Create sub_dup_main
        self.sub_dup_main = Frame(self.canvas, bg="#212023", width=screen_width * 0.3, height=screen_height - 44, bd=1, relief="solid")
        self.sub_dup_main.grid(row=0, column=0, rowspan=2, sticky="nsew")

        # Create video_main
        self.video_main = Frame(self.canvas, bg="#212023", width=screen_width * 0.7, height=screen_height - 44, bd=1, relief="solid")
        self.video_main.grid(row=0, column=1, rowspan=2, sticky="nsew")

        # Create player_main
        self.player_main = Frame(self.video_main, bg="#212023", width=screen_width * 0.7, height= (screen_height - 44) * 0.6, bd=1, relief="solid")
        self.player_main.grid(row=0, column=0, sticky="nsew")

        # Create timeline_main
        self.timeline_main = Frame(self.video_main, bg="#212023", width= screen_width * 0.7, height=(screen_height - 44) * 0.4, bd=1, relief="solid")
        self.timeline_main.grid(row=1, column=0, sticky="nsew")

        

        self.input_video_path = ""
        self.playing = True

        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def select_video(self):
        # Show video on canvas
        self.show_video()

    def show_video(self):
        
        # Replace this with your video loading code
        video_path = filedialog.askopenfilename()
        cap = cv2.VideoCapture(video_path)

        def play_video():
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Hide the browse button
                self.open_button.pack_forget()
                
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.player_main.winfo_width(), self.player_main.winfo_height()))
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(0, 0, anchor='nw', image=imgtk, tags="video_frame")
                self.root.update()

                if not self.playing:
                    break

        play_thread = threading.Thread(target=play_video)
        play_thread.start()

    def on_closing(self):
        self.playing = False
        self.root.destroy()
