import os
import shutil
import threading
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, Frame, Canvas, Toplevel, StringVar
from PIL import Image, ImageTk, ExifTags
from datetime import datetime

class ImageSorter:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Sorter")
        self.root.state('zoomed')
        
        # Set dark theme colors
        self.bg_color = "#2E2E2E"
        self.fg_color = "#FFFFFF"
        self.button_color = "#4A4A4A"
        self.entry_bg = "#3E3E3E"
        self.highlight_color = "#5294E2"
        
        self.root.configure(bg=self.bg_color)
        
        # Configure grid layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)

        # Create frames
        self.left_frame = Frame(root, bg=self.bg_color)
        self.left_frame.grid(row=0, column=0, sticky='nsew')
        self.right_frame = Frame(root, bg=self.bg_color, width=200)
        self.right_frame.grid(row=0, column=1, sticky='nsew')
        self.bottom_frame = Frame(root, height=100, bg=self.bg_color)
        self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky='ew')

        # Canvas setup
        self.canvas_width = self.root.winfo_screenwidth() - 200
        self.canvas_height = self.root.winfo_screenheight() - 150
        self.canvas = Canvas(self.left_frame, width=self.canvas_width, height=self.canvas_height, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        # EXIF data labels
        self.exif_labels = {}
        for i, label in enumerate(["File Name", "Date/Time", "Aperture", "Shutter Speed"]):
            self.exif_labels[label] = Label(self.right_frame, text="", font=('Arial', 12), bg=self.bg_color, fg=self.fg_color, anchor='w', justify='left')
            self.exif_labels[label].grid(row=i, column=0, sticky='w', padx=10, pady=5)

        # UI Elements
        self.label = Label(self.bottom_frame, text="Enter athlete numbers (comma-separated):", font=('Arial', 14), bg=self.bg_color, fg=self.fg_color)
        self.label.pack(side='left', padx=10, pady=10)

        self.entry_var = StringVar()
        self.entry = Entry(self.bottom_frame, textvariable=self.entry_var, font=('Arial', 14), bg=self.entry_bg, fg=self.fg_color, insertbackground=self.fg_color)
        self.entry.pack(side='left', padx=10, pady=10)
        self.entry.bind('<Return>', self.sort_image)

        self.prev_button = Button(self.bottom_frame, text="Previous Image", command=self.load_prev_image, font=('Arial', 14), bg=self.button_color, fg=self.fg_color, activebackground=self.highlight_color)
        self.prev_button.pack(side='left', padx=10, pady=10)

        self.next_button = Button(self.bottom_frame, text="Next Image", command=self.load_next_image, font=('Arial', 14), bg=self.button_color, fg=self.fg_color, activebackground=self.highlight_color)
        self.next_button.pack(side='left', padx=10, pady=10)

        self.image_paths = []
        self.current_image_index = -1
        self.current_image_path = ""
        self.source_folder = ""
        self.photo_image = None

        self.load_images()

    def load_images(self):
        self.source_folder = filedialog.askdirectory(title="Select Image Directory")
        if self.source_folder:
            self.image_paths = [f for f in os.listdir(self.source_folder) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]
            self.image_paths.sort()
            if self.image_paths:
                self.current_image_index = 0
                self.load_current_image()
            else:
                messagebox.showinfo("Info", "No images found in the selected directory")
        else:
            messagebox.showerror("Error", "No folder selected")

    def load_current_image(self):
        if 0 <= self.current_image_index < len(self.image_paths):
            path = os.path.join(self.source_folder, self.image_paths[self.current_image_index])
            self.load_image(path)

    def load_image(self, path):
        if self.photo_image:
            del self.photo_image
        image = Image.open(path)
        image.thumbnail((self.canvas_width, self.canvas_height), Image.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        
        x = (self.canvas_width - image.width) // 2
        y = (self.canvas_height - image.height) // 2

        self.canvas.create_image(x, y, anchor='nw', image=self.photo_image)
        self.current_image_path = path
        self.update_exif_data(image)

    def update_exif_data(self, image):
        exif_data = {}
        try:
            exif = {ExifTags.TAGS[k]: v for k, v in image._getexif().items() if k in ExifTags.TAGS}
            exif_data["File Name"] = os.path.basename(self.current_image_path)
            exif_data["Date/Time"] = exif.get('DateTime', 'Unknown')

            fnumber = exif.get('FNumber', None)
            if fnumber:
                exif_data["Aperture"] = f"f/{float(fnumber):.1f}"
            else:
                exif_data["Aperture"] = "Unknown"

            exposure_time = exif.get('ExposureTime', None)
            if exposure_time:
                exif_data["Shutter Speed"] = f"1/{1 / float(exposure_time):.0f}"
            else:
                exif_data["Shutter Speed"] = "Unknown"
        except AttributeError:
            exif_data = {"File Name": os.path.basename(self.current_image_path),
                         "Date/Time": "Unknown", "Aperture": "Unknown", "Shutter Speed": "Unknown"}

        for label, value in exif_data.items():
            self.exif_labels[label].config(text=f"{label}: {value}")

    def load_next_image(self):
        if self.image_paths:
            self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)
            self.load_current_image()

    def load_prev_image(self):
        if self.image_paths:
            self.current_image_index = (self.current_image_index - 1) % len(self.image_paths)
            self.load_current_image()

    def sort_image(self, event=None):
        athlete_numbers = [num.strip() for num in self.entry_var.get().split(',') if num.strip()]
        if athlete_numbers:
            for number in athlete_numbers:
                self.sort_for_athlete(number)
            self.show_success_banner(f"Image sorted for: {', '.join(athlete_numbers)}")
            self.image_paths.pop(self.current_image_index)
            if self.image_paths:
                self.current_image_index = self.current_image_index % len(self.image_paths)
                self.load_current_image()
            else:
                self.canvas.delete("all")
                messagebox.showinfo("Info", "All images sorted")
            self.entry_var.set("")  # Clear the entry after sorting
        else:
            messagebox.showerror("Error", "Please enter at least one athlete number")

    def sort_for_athlete(self, number):
        source_path = os.path.join(self.source_folder, self.image_paths[self.current_image_index])
        destination_dir = os.path.join(self.source_folder, number)
        os.makedirs(destination_dir, exist_ok=True)
        
        destination_path = os.path.join(destination_dir, self.image_paths[self.current_image_index])
        shutil.copy2(source_path, destination_path)  # Use copy2 to preserve metadata

    def show_success_banner(self, message):
        banner = Toplevel(self.root)
        banner.overrideredirect(True)
        banner.geometry(f"400x50+{self.root.winfo_x() + self.root.winfo_width() // 2 - 200}+{self.root.winfo_y() + 50}")
        banner.configure(bg=self.highlight_color)
        label = Label(banner, text=message, font=('Arial', 14), bg=self.highlight_color, fg=self.fg_color)
        label.pack(fill='both', expand=True)
        banner.after(3000, banner.destroy)

if __name__ == "__main__":
    root = Tk()
    app = ImageSorter(root)
    root.mainloop()