import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import os
from master_dark import MasterDark  # Importing the new master dark class
import cv2
PATH = cv2.__file__
print(PATH)

from PIL import Image, ImageTk
import rawpy
from PIL import ImageDraw

# Define the main application class
class FileLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Loader")

        # Set minimum window size
        self.root.minsize(800, 600)

        self.picture_files = []
        self.dark_files = []
        self.zoom_ratio = 1.0

        # Instantiate the MasterDark class
        self.master_dark = MasterDark()

        self.create_widgets()

    # Create and layout the widgets
    def create_widgets(self):
        # Load Pictures button
        self.load_pictures_button = tk.Button(self.root, text="Load Pictures", command=self.load_pictures)
        self.load_pictures_button.grid(row=0, column=0, padx=10, pady=10)

        # Clear Picture Files button
        self.clear_picture_files_button = tk.Button(self.root, text="Clear Picture Files", command=self.clear_picture_files)
        self.clear_picture_files_button.grid(row=0, column=1, padx=10, pady=10)

        # Listbox for picture files
        self.picture_listbox = tk.Listbox(self.root, height=10, bd=5, relief="solid")
        self.picture_listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.picture_listbox.bind("<<ListboxSelect>>", self.display_image)
        #self.picture_listbox.lift()  # Force it to the front
        #self.picture_listbox.update_idletasks()  # Force UI refresh

        # Load Dark Files button
        self.load_dark_files_button = tk.Button(self.root, text="Load Dark Files", command=self.load_dark_files)
        self.load_dark_files_button.grid(row=2, column=0, padx=10, pady=10)

        # Clear Dark Files button
        self.clear_dark_files_button = tk.Button(self.root, text="Clear Dark Files", command=self.clear_dark_files)
        self.clear_dark_files_button.grid(row=2, column=1, padx=10, pady=10)

        # Listbox for dark files
        self.dark_listbox = tk.Listbox(self.root, height=10, bd=5, relief="solid")
        self.dark_listbox.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.dark_listbox.bind("<<ListboxSelect>>", self.display_image)
        
        # Add Compute Master Dark button
        self.compute_master_dark_button = tk.Button(self.root, text="Compute Master Dark", command=self.compute_master_dark)
        self.compute_master_dark_button.grid(row=4, column=0, padx=10, pady=10)

        # Status label
        self.status_label = tk.Label(self.root, text="", fg="blue")
        self.status_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        
        

        # Frame for displaying images
        self.image_frame = ttk.Frame(self.root)
        self.image_frame.grid(row=0, column=2, rowspan=5, padx=10, pady=10, sticky="nsew")

        # Canvas for image display
        self.canvas = tk.Canvas(self.image_frame, cursor="hand2")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Scrollbars for the canvas
        self.v_scrollbar = ttk.Scrollbar(self.image_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")

        self.h_scrollbar = ttk.Scrollbar(self.image_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        self.canvas.bind("<Configure>", self.resize_image)
        self.canvas.bind("<MouseWheel>", self.scroll_image)
        self.canvas.bind("<Shift-MouseWheel>", self.scroll_image_horizontal)

        # Label for displaying the image
        self.image_label = tk.Label(self.canvas)
        self.canvas.create_window((0, 0), window=self.image_label, anchor="nw")
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag_image)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.canvas.bind("<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.bind("<Leave>", lambda e: self.canvas.config(cursor=""))

        # Frame for zoom controls
        self.zoom_frame = ttk.Frame(self.root)
        self.zoom_frame.grid(row=5, column=2, columnspan=3, padx=10, pady=10, sticky="ew")

        # Zoom buttons with text labels
        self.zoom_ratio_label = tk.Label(self.zoom_frame, text=f"Zoom: {self.zoom_ratio:.2f}x")
        self.zoom_ratio_label.grid(row=0, column=0, padx=5, pady=5)

        # Zoom in button
        self.zoom_in_button = tk.Button(self.zoom_frame, text="+", command=self.zoom_in)
        self.zoom_in_button.grid(row=0, column=1, padx=5, pady=5)

        # Zoom out button
        self.zoom_out_button = tk.Button(self.zoom_frame, text="-", command=self.zoom_out)
        self.zoom_out_button.grid(row=0, column=2, padx=5, pady=5)

        # Fit window button
        self.fit_window_button = tk.Button(self.zoom_frame, text="Fit", command=self.fit_window)
        self.fit_window_button.grid(row=0, column=3, padx=5, pady=5)

        # 100% zoom button
        self.zoom_100_button = tk.Button(self.zoom_frame, text="100%", command=self.zoom_100)
        self.zoom_100_button.grid(row=0, column=4, padx=5, pady=5)

        # Quit button
        self.quit_button = tk.Button(self.root, text="Quit", command=self.root.quit)
        self.quit_button.grid(row=5, column=4, padx=10, pady=10)

        # Configure grid weights for resizing
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.image_frame.grid_rowconfigure(0, weight=1)
        self.image_frame.grid_columnconfigure(0, weight=1)

    # Load picture files
    def load_pictures(self):
        self.root.after(100, self._load_pictures)

    def _load_pictures(self):
        files = filedialog.askopenfilenames(title="Select Picture Files", filetypes=[
        ("Image files", ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif", "*.nef"))
    ])
        print("Selected files:", files)  # Debugging line
        new_files = [file for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.nef')) and file not in self.picture_files]
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

    # Load dark files
    def load_dark_files(self):
        self.root.after(100, self._load_dark_files)

    def _load_dark_files(self):
        files = filedialog.askopenfilenames(title="Select Dark Files", filetypes=[
        ("Image files", ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif", "*.nef"))
    ])
        
        print("Selected files:", files)  # Debugging line
        new_files = [file for file in files if file not in self.dark_files]
        if new_files:
            self.dark_files.extend(new_files)
            self.dark_files.sort()  # Ensure ascending order
            self.update_dark_listbox()
            self.status_label.config(text=f"{len(new_files)} new dark files loaded.")

    # Compute the master dark from the loaded dark files
    def compute_master_dark(self):
        master_dark, status = self.master_dark.compute_master_dark(self.dark_files)
        if master_dark:
            self.status_label.config(text=status, fg="blue")
        else:
            self.status_label.config(text=status, fg="red")
            
    # Clear picture files
    def clear_picture_files(self):
        self.picture_files = []
        self.update_picture_listbox()
        self.status_label.config(text="Picture files cleared.", fg="blue")

    # Clear dark files
    def clear_dark_files(self):
        self.dark_files = []
        self.update_dark_listbox()
        self.status_label.config(text="Dark files cleared.", fg="blue")

    # Display selected image
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




    # Update the displayed image (with master dark subtraction if available)
    def update_image(self):
        if not hasattr(self, 'file_path') or not os.path.exists(self.file_path):
            return

        if self.file_path.lower().endswith('.nef'):
            with rawpy.imread(self.file_path) as raw:
                image = raw.postprocess()
            image = Image.fromarray(image)
        else:
            image = Image.open(self.file_path)

        # Subtract master dark if it exists
        corrected_image, status = self.master_dark.subtract_master_dark(image)
        if corrected_image:
            self.image = corrected_image
        self.status_label.config(text=status, fg="blue")
        self.display_resized_image()

    # Display the resized image
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

    # Resize the image when the canvas is resized
    def resize_image(self, event):
        self.display_resized_image()
        
    # Zoom in the image
    def zoom_in(self):
        # Get the center of the canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        current_center_x = self.canvas.canvasx(canvas_width / 2)
        current_center_y = self.canvas.canvasy(canvas_height / 2)

        # Zoom in
        self.zoom_ratio *= 2
        self.display_resized_image()

        # Re-center the zoom on the current canvas center
        self.center_image(current_center_x, current_center_y)

    def zoom_out(self):
        # Get the center of the canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        current_center_x = self.canvas.canvasx(canvas_width / 2)
        current_center_y = self.canvas.canvasy(canvas_height / 2)

        # Zoom out
        self.zoom_ratio /= 2
        self.display_resized_image()

        # Re-center the zoom on the current canvas center
        self.center_image(current_center_x, current_center_y)

    def center_image(self, current_center_x, current_center_y):
        # Calculate the width and height of the image after applying the zoom
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_width = int(self.image.width * self.zoom_ratio)
        image_height = int(self.image.height * self.zoom_ratio)

        # Calculate the position of the image's center
        new_center_x = image_width / 2
        new_center_y = image_height / 2

        # Calculate the difference between the current canvas center and the new image center
        offset_x = current_center_x - self.canvas.canvasx(canvas_width / 2)
        offset_y = current_center_y - self.canvas.canvasy(canvas_height / 2)

        # Adjust the view to maintain the center of the canvas as the zoom focus
        self.canvas.xview_moveto((offset_x + new_center_x) / image_width)
        self.canvas.yview_moveto((offset_y + new_center_y) / image_height)

    # Fit the image to the window
    def fit_window(self):
        # Fit the image to the window and center it
        if not hasattr(self, 'image'):
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_width, image_height = self.image.size

        width_ratio = canvas_width / image_width
        height_ratio = canvas_height / image_height
        self.zoom_ratio = min(width_ratio, height_ratio)
        self.display_resized_image()

    # Set zoom to 100%
    def zoom_100(self):
        self.zoom_ratio = 1.0
        self.display_resized_image()

    # Update the picture listbox
    def update_picture_listbox(self):
        self.picture_listbox.delete(0, tk.END)
        
        print("Updating Listbox with:", self.picture_files)  # Debugging line
        for file in self.picture_files:
            self.picture_listbox.insert(tk.END, os.path.basename(file))

    # Update the dark listbox
    def update_dark_listbox(self):
        self.dark_listbox.delete(0, tk.END)
        print("Updating Listbox with:", self.dark_files)  # Debugging line
        for file in self.dark_files:
            self.dark_listbox.insert(tk.END, os.path.basename(file))

    # Get the list of picture files
    def get_picture_files(self):
        return self.picture_files

    # Get the list of dark files
    def get_dark_files(self):
        return self.dark_files

    # Scroll the image with the mouse wheel
    def scroll_image(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        else:
            self.canvas.yview_scroll(1, "units")

    # Scroll the image horizontally
    def scroll_image_horizontal(self, event):
        if event.delta > 0:
            self.canvas.xview_scroll(-1, "units")
        else:
            self.canvas.xview_scroll(1, "units")

    # Start dragging the image
    def start_drag(self, event):
        self.canvas.scan_mark(event.x, event.y)
        self.canvas.config(cursor="fleur")  # Change cursor to fleur (hand)

    # Drag the image
    def drag_image(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    # Stop dragging the image
    def stop_drag(self, event):
        pass
    
# Run the application
def run_app():
    root = tk.Tk()
    app = FileLoaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()
