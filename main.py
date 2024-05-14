from presenters.main_presenter import MainPresenter
from views.main_view import MainView
import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Video Cropper")
    root.configure(bg="#333333")

    view = MainView(root)  # Khởi tạo MainView trước
    presenter = MainPresenter(view)  # Truyền MainView vào MainPresenter

    import_button = tk.Button(root, text="Import Video", command=presenter.select_file)
    import_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
