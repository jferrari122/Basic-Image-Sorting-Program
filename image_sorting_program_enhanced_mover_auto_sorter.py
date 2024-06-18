import os
import shutil
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, Frame, Canvas, Toplevel
from PIL import Image, ImageTk

class ImageSorter:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Sorter")
        self.root.state('zoomed')  # Maximize window

        # Configure grid layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create frames
        self.top_frame = Frame(root)
        self.top_frame.grid(row=0, column=0, sticky='nsew')
        self.bottom_frame = Frame(root, height=100)
        self.bottom_frame.grid(row=1, column=0, sticky='ew')

        # Update canvas size to a higher resolution
        self.canvas_width = self.root.winfo_screenwidth()
        self.canvas_height = self.root.winfo_screenheight() - 150
        self.canvas = Canvas(self.top_frame, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(fill='both', expand=True)

        self.label = Label(self.bottom_frame, text="Enter folder name:", font=('Arial', 14))
        self.label.pack(side='left', padx=10, pady=10)

        self.entry = Entry(self.bottom_frame, font=('Arial', 14))
        self.entry.pack(side='left', padx=10, pady=10)

        self.sort_button = Button(self.bottom_frame, text="Sort Image", command=self.sort_image, font=('Arial', 14))
        self.sort_button.pack(side='left', padx=10, pady=10)

        self.prev_button = Button(self.bottom_frame, text="Previous Image", command=self.load_prev_image, font=('Arial', 14))
        self.prev_button.pack(side='left', padx=10, pady=10)

        self.next_button = Button(self.bottom_frame, text="Next Image", command=self.load_next_image, font=('Arial', 14))
        self.next_button.pack(side='left', padx=10, pady=10)

        self.change_output_button = Button(self.bottom_frame, text="Change Output Folder", command=self.change_output_folder, font=('Arial', 14))
        self.change_output_button.pack(side='left', padx=10, pady=10)

        self.image_paths = []
        self.current_image_index = -1
        self.current_image_path = ""
        self.destination_dirs = {}

        self.load_images()

    def load_images(self):
        folder_selected = filedialog.askdirectory(title="Select Image Directory")
        if folder_selected:
            self.image_paths = [os.path.join(folder_selected, f) for f in os.listdir(folder_selected) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]
            self.image_paths.sort()
            if self.image_paths:
                self.load_next_image()
            else:
                messagebox.showinfo("Info", "No images found in the selected directory")
        else:
            messagebox.showerror("Error", "No folder selected")

    def load_image(self, path):
        image = Image.open(path)
        image.thumbnail((self.canvas_width, self.canvas_height), Image.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        
        # Calculate position to center the image
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_width, image_height = image.size
        x = (canvas_width - image_width) // 2
        y = (canvas_height - image_height) // 2

        self.canvas.create_image(x, y, anchor='nw', image=self.photo_image)
        self.current_image_path = path

    def load_next_image(self):
        if self.image_paths:
            self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)
            self.load_image(self.image_paths[self.current_image_index])

    def load_prev_image(self):
        if self.image_paths:
            self.current_image_index = (self.current_image_index - 1) % len(self.image_paths)
            self.load_image(self.image_paths[self.current_image_index])

    def sort_image(self):
        folder_name = self.entry.get().strip()
        if folder_name:
            if folder_name in self.destination_dirs:
                destination_dir = self.destination_dirs[folder_name]
            else:
                destination_dir = filedialog.askdirectory(title="Select Destination Directory")
                if destination_dir:
                    new_folder_path = os.path.join(destination_dir, folder_name)
                    os.makedirs(new_folder_path, exist_ok=True)
                    self.destination_dirs[folder_name] = new_folder_path
                else:
                    messagebox.showerror("Error", "No destination directory selected")
                    return
            destination_path = os.path.join(self.destination_dirs[folder_name], os.path.basename(self.current_image_path))
            shutil.move(self.current_image_path, destination_path)  # Use move instead of copy
            self.show_success_banner(f"Image moved to {destination_path}")
            self.image_paths.pop(self.current_image_index)  # Remove the moved image from the list
            if self.image_paths:
                self.current_image_index = (self.current_image_index - 1) % len(self.image_paths)
                self.load_next_image()
            else:
                self.canvas.delete("all")
                messagebox.showinfo("Info", "All images sorted")
        else:
            messagebox.showerror("Error", "Folder name cannot be empty")

    def show_success_banner(self, message):
        banner = Toplevel(self.root)
        banner.overrideredirect(True)
        banner.geometry(f"400x50+{self.root.winfo_x() + self.root.winfo_width() // 2 - 200}+{self.root.winfo_y() + 50}")
        banner.configure(bg="green")
        label = Label(banner, text=message, font=('Arial', 14), bg="green", fg="white")
        label.pack(fill='both', expand=True)
        banner.after(3000, banner.destroy)

    def change_output_folder(self):
        self.destination_dirs.clear()
        messagebox.showinfo("Info", "Output folders cleared. Please select a new destination for the next image.")

if __name__ == "__main__":
    root = Tk()
    app = ImageSorter(root)
    root.mainloop()
