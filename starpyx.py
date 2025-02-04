import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import os

import cv2
PATH = cv2.__file__
print(PATH)

from PIL import Image, ImageTk
import rawpy
from PIL import ImageDraw

class FileLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Loader")
        
        # Set minimum window size
        self.root.minsize(800, 600)
        
        self.picture_files = []
        self.dark_files = []
        self.zoom_ratio = 1.0

        self.create_widgets()

    def create_widgets(self):
        self.load_pictures_button = tk.Button(self.root, text="Load Pictures", command=self.load_pictures)
        self.load_pictures_button.grid(row=0, column=0, padx=10, pady=10)

        self.clear_picture_files_button = tk.Button(self.root, text="Clear Picture Files", command=self.clear_picture_files)
        self.clear_picture_files_button.grid(row=0, column=1, padx=10, pady=10)

        self.picture_listbox = tk.Listbox(self.root)
        self.picture_listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.picture_listbox.bind("<<ListboxSelect>>", self.display_image)

        self.load_dark_files_button = tk.Button(self.root, text="Load Dark Files", command=self.load_dark_files)
        self.load_dark_files_button.grid(row=2, column=0, padx=10, pady=10)

        self.clear_dark_files_button = tk.Button(self.root, text="Clear Dark Files", command=self.clear_dark_files)
        self.clear_dark_files_button.grid(row=2, column=1, padx=10, pady=10)

        self.dark_listbox = tk.Listbox(self.root)
        self.dark_listbox.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.dark_listbox.bind("<<ListboxSelect>>", self.display_image)

        self.status_label = tk.Label(self.root, text="", fg="blue")
        self.status_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.image_frame = ttk.Frame(self.root)
        self.image_frame.grid(row=0, column=2, rowspan=5, padx=10, pady=10, sticky="nsew")

        self.canvas = tk.Canvas(self.image_frame)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.v_scrollbar = ttk.Scrollbar(self.image_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")

        self.h_scrollbar = ttk.Scrollbar(self.image_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        self.canvas.bind("<Configure>", self.resize_image)

        self.image_label = tk.Label(self.canvas)
        self.canvas.create_window((0, 0), window=self.image_label, anchor="nw")

        # Frame for zoom controls
        self.zoom_frame = ttk.Frame(self.root)
        self.zoom_frame.grid(row=5, column=2, columnspan=3, padx=10, pady=10, sticky="ew")

        # Zoom buttons with text labels
        self.zoom_in_button = tk.Button(self.zoom_frame, text="Zoom In", command=self.zoom_in)
        self.zoom_in_button.grid(row=0, column=0, padx=5, pady=5)

        self.zoom_out_button = tk.Button(self.zoom_frame, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_button.grid(row=0, column=1, padx=5, pady=5)

        self.fit_window_button = tk.Button(self.zoom_frame, text="Fit Window", command=self.fit_window)
        self.fit_window_button.grid(row=0, column=2, padx=5, pady=5)

        self.zoom_ratio_label = tk.Label(self.zoom_frame, text=f"Zoom: {self.zoom_ratio:.2f}x")
        self.zoom_ratio_label.grid(row=0, column=3, padx=5, pady=5)

        self.quit_button = tk.Button(self.root, text="Quit", command=self.root.quit)
        self.quit_button.grid(row=5, column=4, padx=10, pady=10)

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.image_frame.grid_rowconfigure(0, weight=1)
        self.image_frame.grid_columnconfigure(0, weight=1)

    def load_pictures(self):
        self.root.after(100, self._load_pictures)

    def _load_pictures(self):
        files = filedialog.askopenfilenames(title="Select Picture Files", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.nef")])
        new_files = [file for file in files if file not in self.picture_files]
        if new_files:
            def get_exif_date_or_filename(path):
                try:
                    with Image.open(path) as img:
                        exif = img.getexif()
                        date_taken = exif.get(36867)  # 36867 is DateTimeOriginal
                        if date_taken:
                            return date_taken
                except:
                    pass
                return os.path.basename(path)

            self.picture_files.extend(new_files)
            self.picture_files.sort(key=get_exif_date_or_filename)
            self.update_picture_listbox()
            self.status_label.config(text=f"{len(new_files)} new picture files loaded.")

    def load_dark_files(self):
        self.root.after(100, self._load_dark_files)

    def _load_dark_files(self):
        files = filedialog.askopenfilenames(title="Select Dark Files", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.nef")])
        new_files = [file for file in files if file not in self.dark_files]
        if new_files:
            self.dark_files.extend(new_files)
            self.dark_files.sort()  # Ensure ascending order
            self.update_dark_listbox()
            self.status_label.config(text=f"{len(new_files)} new dark files loaded.")

    def clear_picture_files(self):
        self.picture_files = []
        self.update_picture_listbox()
        self.status_label.config(text="Picture files cleared.", fg="blue")

    def clear_dark_files(self):
        self.dark_files = []
        self.update_dark_listbox()
        self.status_label.config(text="Dark files cleared.", fg="blue")

    def display_image(self, event=None):
        selected_listbox = event.widget
        if selected_listbox == self.picture_listbox:
            selected_files = self.picture_files
        elif selected_listbox == self.dark_listbox:
            selected_files = self.dark_files
        else:
            self.status_label.config(text="No file selected.", fg="red")
            return

        try:
            index = selected_listbox.curselection()[0]
            self.file_path = selected_files[index]
        except IndexError:
            self.status_label.config(text="No file selected.", fg="red")
            return

        if not os.path.exists(self.file_path):
            self.status_label.config(text="File does not exist.", fg="red")
            return

        self.update_image()
        self.fit_window()  # Trigger the fit window method
        self.status_label.config(text=f"Displaying: {os.path.basename(self.file_path)}", fg="blue")

    def update_image(self):
        if not hasattr(self, 'file_path') or not os.path.exists(self.file_path):
            return

        if self.file_path.lower().endswith('.nef'):
            with rawpy.imread(self.file_path) as raw:
                image = raw.postprocess()
            image = Image.fromarray(image)
        else:
            image = Image.open(self.file_path)

        self.image = image
        self.display_resized_image()

    def display_resized_image(self):
        if not hasattr(self, 'image'):
            return

        width, height = self.image.size
        new_width = int(width * self.zoom_ratio)
        new_height = int(height * self.zoom_ratio)
        resized_image = self.image.resize((new_width, new_height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized_image)

        self.image_label.config(image=photo)
        self.image_label.image = photo  # Keep a reference to avoid garbage collection

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.zoom_ratio_label.config(text=f"Zoom: {self.zoom_ratio:.2f}x")

    def resize_image(self, event):
        self.display_resized_image()

    def zoom_in(self):
        self.zoom_ratio *= 2
        self.display_resized_image()

    def zoom_out(self):
        self.zoom_ratio /= 2
        self.display_resized_image()

    def fit_window(self):
        if not hasattr(self, 'image'):
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_width, image_height = self.image.size

        width_ratio = canvas_width / image_width
        height_ratio = canvas_height / image_height
        self.zoom_ratio = min(width_ratio, height_ratio)
        self.display_resized_image()

    def update_picture_listbox(self):
        self.picture_listbox.delete(0, tk.END)
        for file in self.picture_files:
            self.picture_listbox.insert(tk.END, os.path.basename(file))

    def update_dark_listbox(self):
        self.dark_listbox.delete(0, tk.END)
        for file in self.dark_files:
            self.dark_listbox.insert(tk.END, os.path.basename(file))

    def get_picture_files(self):
        return self.picture_files

    def get_dark_files(self):
        return self.dark_files

if __name__ == "__main__":
    root = tk.Tk()
    app = FileLoaderApp(root)
    root.mainloop()
