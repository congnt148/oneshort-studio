import tkinter as tk
from tkinter import Frame, Label, Button, Scrollbar, HORIZONTAL
from PIL import Image, ImageTk
import cv2
import threading
import time

class MainView:
    def __init__(self, root):
        self.root = root
        self.presenter = None

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

        # Place the Browse button in header_frame
        # self.open_button = Button(header_frame, text="Open", command=self.select_file, bg="white", fg="black", borderwidth=0, relief="flat")
        # self.open_button.pack(side="right", padx=60, pady=5)
        
        self.open_button = Button(header_frame, text="Open", bg="white", fg="black", borderwidth=0, relief="flat")
        self.open_button["command"] = self.open_file_with_threading  # Gán hàm open_file_with_threading làm command cho nút Open
        self.open_button.pack(side="right", padx=60, pady=5)

        # Main canvas
        self.canvas = tk.Canvas(root, width=screen_width, height=screen_height - 44)
        self.canvas.pack(expand=True)

        # Set up column configuration for canvas
        self.canvas.grid_columnconfigure(0, weight=3) 
        self.canvas.grid_columnconfigure(1, weight=7)

        self.canvas.grid_rowconfigure(0, weight=7)
        self.canvas.grid_rowconfigure(1, weight=3) 

        # Create sub_dup_main
        self.sub_dup_main = Frame(self.canvas, bg="#212023", width=screen_width * 0.3, height=screen_height - 44, bd=1, relief="solid")
        self.sub_dup_main.grid(row=0, column=0, rowspan=2, sticky="nsew")

        # Create video_main
        self.video_main = Frame(self.canvas, bg="#212023", width=screen_width * 0.7, height=screen_height - 44, bd=1, relief="solid")
        self.video_main.grid(row=0, column=1, rowspan=2, sticky="nsew")

        # Create player_main
        self.player_main = Frame(self.video_main, bg="#212023", width=screen_width * 0.7, height= (screen_height - 44) * 0.7, bd=1, relief="solid")
        self.player_main.grid(row=0, column=0, sticky="nsew")

        # Create timeline_main
        self.timeline_main = Frame(self.video_main, bg="#212023", width= screen_width * 0.7, height=(screen_height - 44) * 0.3, bd=1, relief="solid")
        self.timeline_main.grid(row=1, column=0, sticky="nsew")
        
        # Add scrollbar to timeline_main
        self.scrollbar = Scrollbar(self.timeline_main, orient=HORIZONTAL, bg="#212023", highlightbackground="#212023")

        self.scrollbar.pack(side="top", fill="x")
        
        # Configure canvas to use scrollbar
        self.timeline_canvas = tk.Canvas(self.timeline_main, bg="#212023", bd=0, xscrollcommand=self.scrollbar.set)
        self.timeline_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.timeline_canvas.xview)
        
        # Prevent timeline_canvas from changing the size of timeline_main
        self.timeline_canvas.pack_propagate(0)
        
        self.timeline_main.bind("<MouseWheel>", self.on_mouse_scroll)
        
        self.is_playing = False
        # self.play_button = Button(self.player_main, text="Play", command=self.play_frames, bg="white", fg="black", borderwidth=0, relief="flat")
        # self.play_button.pack(side="left", padx=5, pady=5)
        # self.pause_button = Button(self.player_main, text="Pause", command=self.pause_frames, bg="white", fg="black", borderwidth=0, relief="flat")
        # self.pause_button.pack(side="left", padx=5, pady=5)
        # self.stop_button = Button(self.player_main, text="Stop", command=self.stop_frames, bg="white", fg="black", borderwidth=0, relief="flat")
        # self.stop_button.pack(side="left", padx=5, pady=5)

        self.input_video_path = ""

        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_mouse_scroll(self, event):
        if event.delta:
            # Xử lý sự kiện cuộn chuột ngang
            direction = 1 if event.delta > 0 else -1
            self.timeline_canvas.xview_scroll(direction, "units")
        
    def open_file_with_threading(self):
        # Khởi tạo một luồng mới để mở tệp
        threading.Thread(target=self.open_file).start()

    def open_file(self):
        if self.presenter:
            self.presenter.select_file()

    def set_presenter(self, presenter):
        self.presenter = presenter

    def select_file(self):
        if self.presenter:
            self.presenter.select_file()

    def display_frames_in_timeline(self, frame_items):
        # Tạo một frame để chứa danh sách hình
        frame_list_frame = Frame(self.timeline_canvas, bg="#212023")
        frame_list_frame.pack(fill="both", expand=True)

        # Thiết lập khả năng cuộn ngang cho frame_list_frame
        frame_list_frame.bind("<Configure>", lambda e: self.timeline_canvas.configure(scrollregion=self.timeline_canvas.bbox("all")))

        # Tính toán kích thước mới cho hình ảnh
        image_height = self.timeline_main.winfo_height() // 5
        if frame_items:
            image_width = int(frame_items[0].frame.shape[1] * (image_height / frame_items[0].frame.shape[0]))

            # Thêm từng hình vào frame_list_frame
            for frame_item in frame_items:
                frame = cv2.cvtColor(frame_item.frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (image_width, image_height))
                frame_image = ImageTk.PhotoImage(Image.fromarray(frame))
                
                frame_label = Label(frame_list_frame, image=frame_image)
                frame_label.image = frame_image
                frame_label.pack(side="left", padx=2, pady=2)

        # Đặt frame_list_frame vào timeline_canvas
        self.timeline_canvas.create_window((0, 0), window=frame_list_frame, anchor="nw")
        # Hiển thị timeline
        # self.display_timeline(frame_items)
        
    def display_timeline(self, frame_items):
        # Xóa timeline hiện có
        self.timeline_canvas.delete("timeline")

        if frame_items:
            # Tính toán số lượng giây tương ứng với số khung hình và chiều rộng của canvas
            num_frames = len(frame_items)
            video_duration_seconds = num_frames  # Giả sử mỗi khung hình tương ứng với một giây
            canvas_width = self.timeline_main.winfo_width()

            # Tính toán kích thước cho từng đoạn thời gian
            segment_width = canvas_width / video_duration_seconds

            # Vẽ dải thời gian trên canvas
            for second in range(video_duration_seconds):
                start_x = second * segment_width
                end_x = (second + 1) * segment_width
                self.timeline_canvas.create_line(start_x, 0, end_x, 0, fill="white", width=2, tags="timeline")

            # Thiết lập cuộn ngang cho canvas
            self.timeline_canvas.configure(scrollregion=(0, 0, canvas_width, self.timeline_canvas.winfo_height()))
            
    def display_frame_list(self, frame_items):
        self.frame_items = frame_items
        self.current_frame_index = 0
        if frame_items:
            self.display_current_frame()

    def display_current_frame(self):
        # Get the dimensions of player_main
        player_width = self.player_main.winfo_width()
        player_height = self.player_main.winfo_height()
        
        # Get the current frame
        frame_item = self.frame_items[self.current_frame_index]
        frame = cv2.cvtColor(frame_item.frame, cv2.COLOR_BGR2RGB)

        # Calculate the scaling factor
        frame_height, frame_width = frame.shape[:2]
        scale_w = player_width / frame_width
        scale_h = player_height / frame_height
        scale = min(scale_w, scale_h)

        # Calculate the new size
        new_width = int(frame_width * scale)
        new_height = int(frame_height * scale)

        # Resize the frame
        resized_frame = cv2.resize(frame, (new_width, new_height))
        frame_image = ImageTk.PhotoImage(Image.fromarray(resized_frame))

        # Display the frame
        if hasattr(self, 'video_label'):
            self.video_label.configure(image=frame_image)
            self.video_label.image = frame_image
        else:
            self.video_label = Label(self.player_main, image=frame_image, bg="#212023")
            self.video_label.pack(fill="both", expand=True)

        # Update player_main size to fit the resized frame
        self.player_main.update_idletasks()
            
    def play_frames(self):
        self.is_playing = True
        self.show_next_frame()

    def pause_frames(self):
        self.is_playing = False

    def stop_frames(self):
        self.is_playing = False
        self.current_frame_index = 0
        self.display_current_frame()

    def show_next_frame(self):
        if self.is_playing and self.current_frame_index < len(self.frame_items) - 1:
            self.current_frame_index += 1
            self.display_current_frame()
            self.root.after(1000 // 30, self.show_next_frame)
            
    def on_closing(self):
        self.root.quit()

# import tkinter as tk
# from tkinter import Frame
# from views.header import Header
# from views.player import Player
# from views.timeline import Timeline
# import threading

# class MainView:
#     def __init__(self, root):
#         self.root = root
#         self.presenter = None

#         screen_width = root.winfo_screenwidth()
#         screen_height = root.winfo_screenheight()
#         root.geometry(f"{screen_width}x{screen_height}")

#         self.header = Header(root, self.open_file_with_threading)
#         self.canvas = tk.Canvas(root, width=screen_width, height=screen_height - 44)
#         self.canvas.pack(expand=True)

#         self.canvas.grid_columnconfigure(0, weight=3) 
#         self.canvas.grid_columnconfigure(1, weight=7)
#         self.canvas.grid_rowconfigure(0, weight=7)
#         self.canvas.grid_rowconfigure(1, weight=3)

#         self.sub_dup_main = Frame(self.canvas, bg="#212023", width=screen_width * 0.3, height=screen_height - 44, bd=1, relief="solid")
#         self.sub_dup_main.grid(row=0, column=0, rowspan=2, sticky="nsew")

#         self.video_main = Frame(self.canvas, bg="#212023", width=screen_width * 0.7, height=screen_height - 44, bd=1, relief="solid")
#         self.video_main.grid(row=0, column=1, rowspan=2, sticky="nsew")

#         self.player = Player(self.video_main)
#         self.player.player_main.grid(row=0, column=0, sticky="nsew")

#         self.timeline = Timeline(self.video_main)
#         self.timeline.timeline_main.grid(row=1, column=0, sticky="nsew")

#         self.input_video_path = ""
#         root.protocol("WM_DELETE_WINDOW", self.on_closing)

#     def open_file_with_threading(self):
#         threading.Thread(target=self.open_file).start()

#     def open_file(self):
#         if self.presenter:
#             self.presenter.select_file()

#     def set_presenter(self, presenter):
#         self.presenter = presenter

#     def display_frames_in_timeline(self, frame_items):
#         self.timeline.display_frames_in_timeline(frame_items)

#     def display_frame_list(self, frame_items):
#         self.player.display_frame_list(frame_items)

#     def on_closing(self):
#         self.root.quit()
