from presenters.main_presenter import MainPresenter
from views.main_view import MainView
import tkinter as tk


def main():
    root = tk.Tk()
    root.title("Video Cropper")
    root.configure(bg="#212023")

    presenter = MainPresenter(None) 
    view = MainView(root, presenter)
    presenter.view = view

    root.mainloop()

if __name__ == "__main__":
    main()
