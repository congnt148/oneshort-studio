# from presenters.main_presenter import MainPresenter
# from views.main_view import MainView
# import tkinter as tk


# def main():
#     root = tk.Tk()
#     root.title("Video Cropper")
#     root.configure(bg="#212023")

#     presenter = MainPresenter(None) 
#     view = MainView(root, presenter)
#     presenter.view = view

#     root.mainloop()

# if __name__ == "__main__":
#     main()



# import tkinter as tk
# from presenters.main_presenter import MainPresenter
# from views.main_view import MainView

# def main():
#     root = tk.Tk()
#     main_view = MainView(root)
#     main_presenter = MainPresenter(main_view)
#     main_view.set_presenter(main_presenter)
#     root.mainloop()

# if __name__ == "__main__":
#     main()


import tkinter as tk
from presenters.main_presenter import MainPresenter
from views.main_view import MainView


def main():
    root = tk.Tk()
    main_view = MainView(root)
    main_presenter = MainPresenter(main_view)
    main_view.set_presenter(main_presenter)
    
    # # Sử dụng threading để xử lý video và frame
    # threading.Thread(target=main_presenter.select_file).start()
    
    root.mainloop()

if __name__ == "__main__":
    main()
