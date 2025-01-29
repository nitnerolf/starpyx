import tkinter as tk
from tkinter import filedialog
import os
from PIL import Image, ImageTk
from PIL import Image

class FileLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Loader")
        
        # Set minimum window size
        self.root.minsize(800, 600)
        
        self.picture_files = []
        self.dark_files = []

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

        self.image_label = tk.Label(self.root)
        self.image_label.grid(row=0, column=2, rowspan=5, padx=10, pady=10, sticky="nsew")
        self.image_label.bind("<Configure>", self.resize_image)

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(3, weight=1)

    def load_pictures(self):
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

    def update_image(self):
        if not hasattr(self, 'file_path') or not os.path.exists(self.file_path):
            return

        image = Image.open(self.file_path)
        image.thumbnail((self.image_label.winfo_width(), self.image_label.winfo_height()))
        photo = ImageTk.PhotoImage(image)

        self.image_label.config(image=photo)
        self.image_label.image = photo  # Keep a reference to avoid garbage collection

    def resize_image(self, event):
        self.update_image()

    def update_picture_listbox(self):
        self.picture_listbox.delete(0, tk.END)
        for file in self.picture_files:
            self.picture_listbox.insert(tk.END, os.path.basename(file))

    def update_dark_listbox(self):
        self.dark_listbox.delete(0, tk.END)
        for file in self.dark_files:
            self.dark_listbox.insert(tk.END, os.path.basename(file))

if __name__ == "__main__":
    root = tk.Tk()
    app = FileLoaderApp(root)
    root.mainloop()
