import os
import subprocess
from pathlib import Path
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, Canvas, Scrollbar, StringVar

from utils import create_output_folder, extract_frames, extract_images
from utils import create_thumbnail, create_video_output_folder, create_resize_output_folder
from utils import resize_image, process_images

import math
import warnings
import cv2
from PIL import Image, ImageTk

from rembg_processor import remove_background_rembg
from rm_bg import remove_background_briarmbg

# Define the ShowImagesSection class
class ShowImagesSection:
    def __init__(self, parent, show_image_callback, set_images_folder_callback):
        self.parent = parent
        self.show_image_callback = show_image_callback
        self.set_images_folder_callback = set_images_folder_callback
        self.loaded_image_paths = []
        self.configure_thumbnail_section()

    def configure_thumbnail_section(self):
        self.thumbnail_frame = ctk.CTkFrame(self.parent)
        self.thumbnail_frame.grid(row=0, column=0, rowspan=2, sticky="nswe", padx=10, pady=10)

        self.thumbnail_title_frame = ctk.CTkFrame(self.thumbnail_frame, height=50)
        self.thumbnail_title_frame.pack(fill="x", pady=5)
        self.thumbnail_title_frame.grid_propagate(False)
        self.thumbnail_title = ctk.CTkLabel(self.thumbnail_title_frame, text="Images", font=("Arial", 16))
        self.thumbnail_title.pack(pady=10)

        self.load_button = ctk.CTkButton(self.thumbnail_frame, text="Load Images", command=self.load_images)
        self.load_button.pack(pady=10)

        self.scrollable_frame = ctk.CTkScrollableFrame(self.thumbnail_frame, width=250, height=600, fg_color="white")
        self.scrollable_frame.pack(fill="both", expand=True, pady=10)
        self.scrollable_frame.configure(fg_color="#333333")

    def load_images(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.loaded_image_paths = extract_images(folder_selected)
            self.set_images_folder_callback(folder_selected)
            self.display_images(self.loaded_image_paths)

    def display_images(self, image_paths):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        max_thumbnail_width = 100
        max_columns = 5
        frame_width = self.scrollable_frame.winfo_width()
        max_columns = max(9, frame_width // (max_thumbnail_width + 10))

        row = 0
        col = 0

        for image_path in image_paths:
            thumbnail = create_thumbnail(image_path, (max_thumbnail_width, max_thumbnail_width))
            label = ctk.CTkLabel(self.scrollable_frame, image=thumbnail, text="")
            label.image = thumbnail
            label.bind("<Button-1>", lambda e, img=image_path: self.show_image_callback(img))
            label.grid(row=row, column=col, padx=5, pady=5)

            col += 1
            if col >= max_columns:
                col = 0
                row += 1

        self.scrollable_frame.update_idletasks()

# Define the ShowSingleImageSection class
class AutoScrollbar(ttk.Scrollbar):
    """ A scrollbar that hides itself if it's not needed. Works only for grid geometry manager """
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise ttk.TclError('Cannot use pack with the widget ' + self.__class__.__name__)

    def place(self, **kw):
        raise tk.TclError('Cannot use place with the widget ' + self.__class__.__name__)

class CanvasImage:
    """ Display and zoom image """
    def __init__(self, placeholder, path):
        """ Initialize the ImageFrame """
        self.imscale = 1.0  # scale for the canvas image zoom, public for outer classes
        self.__delta = 1.3  # zoom magnitude
        self.__filter = Image.LANCZOS  # could be: NEAREST, BILINEAR, BICUBIC and LANCZOS
        self.__previous_state = 0  # previous state of the keyboard
        self.path = path  # path to the image, should be public for outer classes
        # Create ImageFrame in placeholder widget
        self._imframe = tk.Frame(placeholder, bg='#333333')  # placeholder of the ImageFrame object
        self._imframe.grid(row=0, column=0, sticky="nswe")
        self._imframe.grid_propagate(False)
        self._imframe.update_idletasks()

        # Vertical and horizontal scrollbars for canvas
        hbar = AutoScrollbar(self._imframe, orient='horizontal')
        vbar = AutoScrollbar(self._imframe, orient='vertical')
        hbar.grid(row=1, column=0, sticky='we')
        vbar.grid(row=0, column=1, sticky='ns')
        # Create canvas and bind it with scrollbars. Public for outer classes
        self.canvas = tk.Canvas(self._imframe, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set, bg='#333333')
        self.canvas.grid(row=0, column=0, sticky='nswe')
        self._imframe.grid_rowconfigure(0, weight=1)
        self._imframe.grid_columnconfigure(0, weight=1)
        self.canvas.update()  # wait till canvas is created
        hbar.configure(command=self.__scroll_x)  # bind scrollbars to the canvas
        vbar.configure(command=self.__scroll_y)
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', lambda event: self.__show_image())  # canvas is resized
        self.canvas.bind('<ButtonPress-1>', self.__move_from)  # remember canvas position
        self.canvas.bind('<B1-Motion>', self.__move_to)  # move canvas to the new position
        self.canvas.bind('<MouseWheel>', self.__wheel)  # zoom for Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>', self.__wheel)  # zoom for Linux, wheel scroll down
        self.canvas.bind('<Button-4>', self.__wheel)  # zoom for Linux, wheel scroll up
        # Handle keystrokes in idle mode, because program slows down on a weak computers,
        # when too many key stroke events in the same time
        self.canvas.bind('<Key>', lambda event: self.canvas.after_idle(self.__keystroke, event))
        # Open image
        with warnings.catch_warnings():  # suppress DecompressionBombWarning
            warnings.simplefilter('ignore')
            self.__image = Image.open(self.path)  # open image, but don't load it
        self.imwidth, self.imheight = self.__image.size  # public for outer classes
        self.__min_side = min(self.imwidth, self.imheight)  # get the smaller image side
        self.__pyramid = [Image.open(self.path)]  # only original image in pyramid
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle((0, 0, self.imwidth, self.imheight), width=0)
        self.__show_image()  # show image on the canvas
        self.canvas.focus_set()  # set focus on the canvas

    def redraw_figures(self):
        """ Dummy function to redraw figures in the children classes """
        pass

    def grid(self, **kw):
        """ Put CanvasImage widget on the parent widget """
        self._imframe.grid(**kw)  # place CanvasImage widget on the grid
        self._imframe.grid(sticky='nswe')  # make frame container sticky
        self._imframe.rowconfigure(0, weight=1)  # make canvas expandable
        self._imframe.columnconfigure(0, weight=1)

    def pack(self, **kw):
        """ Exception: cannot use pack with this widget """
        raise Exception('Cannot use pack with the widget ' + self.__class__.__name__)

    def place(self, **kw):
        """ Exception: cannot use place with this widget """
        raise Exception('Cannot use place with the widget ' + self.__class__.__name__)

    # noinspection PyUnusedLocal
    def __scroll_x(self, *args, **kwargs):
        """ Scroll canvas horizontally and redraw the image """
        self.canvas.xview(*args)  # scroll horizontally
        self.__show_image()  # redraw the image

    # noinspection PyUnusedLocal
    def __scroll_y(self, *args, **kwargs):
        """ Scroll canvas vertically and redraw the image """
        self.canvas.yview(*args)  # scroll vertically
        self.__show_image()  # redraw the image

    def __show_image(self):
        """ Show image on the Canvas. Implements correct image zoom almost like in Google Maps """
        box_image = self.canvas.coords(self.container)  # get image area
        box_canvas = (self.canvas.canvasx(0),  # get visible area of the canvas
                      self.canvas.canvasy(0),
                      self.canvas.canvasx(self.canvas.winfo_width()),
                      self.canvas.canvasy(self.canvas.winfo_height()))
        box_img_int = tuple(map(int, box_image))  # convert to integer or it will not work properly
        # Get scroll region box
        box_scroll = [min(box_img_int[0], box_canvas[0]), min(box_img_int[1], box_canvas[1]),
                      max(box_img_int[2], box_canvas[2]), max(box_img_int[3], box_canvas[3])]
        # Horizontal part of the image is in the visible area
        if box_scroll[0] == box_canvas[0] and box_scroll[2] == box_canvas[2]:
            box_scroll[0] = box_img_int[0]
            box_scroll[2] = box_img_int[2]
        # Vertical part of the image is in the visible area
        if box_scroll[1] == box_canvas[1] and box_scroll[3] == box_canvas[3]:
            box_scroll[1] = box_img_int[1]
            box_scroll[3] = box_img_int[3]
        # Convert scroll region to tuple and to integer
        self.canvas.configure(scrollregion=tuple(map(int, box_scroll)))  # set scroll region
        x1 = max(box_canvas[0] - box_image[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(box_canvas[1] - box_image[1], 0)
        x2 = min(box_canvas[2], box_image[2]) - box_image[0]
        y2 = min(box_canvas[3], box_image[3]) - box_image[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            image = self.__pyramid[0].crop(  # crop current img from pyramid
                (int(x1 / self.imscale), int(y1 / self.imscale),
                 int(x2 / self.imscale), int(y2 / self.imscale)))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1)), self.__filter))
            imageid = self.canvas.create_image(max(box_canvas[0], box_img_int[0]),
                                               max(box_canvas[1], box_img_int[1]),
                                               anchor='nw', image=imagetk)
            self.canvas.lower(imageid)  # set image into background
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

    def __move_from(self, event):
        """ Remember previous coordinates for scrolling with the mouse """
        self.canvas.scan_mark(event.x, event.y)

    def __move_to(self, event):
        """ Drag (move) canvas to the new position """
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.__show_image()  # zoom tile and show it on the canvas

    def outside(self, x, y):
        """ Checks if the point (x,y) is outside the image area """
        bbox = self.canvas.coords(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            return False  # point (x,y) is inside the image area
        else:
            return True  # point (x,y) is outside the image area

    def __wheel(self, event):
        """ Zoom with mouse wheel """
        x = self.canvas.canvasx(event.x)  # get coordinates of the event on the canvas
        y = self.canvas.canvasy(event.y)
        if self.outside(x, y): return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down, smaller
            if round(self.__min_side * self.imscale) < 30: return  # image is less than 30 pixels
            self.imscale /= self.__delta
            scale /= self.__delta
        if event.num == 4 or event.delta == 120:  # scroll up, bigger
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height()) >> 1
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.__delta
            scale *= self.__delta
        self.canvas.scale('all', x, y, scale, scale)  # rescale all objects
        self.__show_image()  # redraw the image


class ShowSingleImageSection:
    def __init__(self, parent):
        self.parent = parent
        self.image_viewer_frame = None
        self.canvas_image = None
        self.configure_image_viewer_section()

    def configure_image_viewer_section(self):
        self.image_viewer_frame = tk.Frame(self.parent, width=700, height=600, bg='#2b2b2b')  # Dark background
        self.image_viewer_frame.grid(row=1, column=1, sticky="nswe", padx=10, pady=10)
        self.image_viewer_frame.grid_propagate(False)

        self.image_viewer_title_frame = tk.Frame(self.image_viewer_frame, height=50, bg='#2b2b2b')  # Dark background
        self.image_viewer_title_frame.pack(fill="x", pady=5)
        self.image_viewer_title_frame.grid_propagate(False)
        self.image_viewer_title = tk.Label(self.image_viewer_title_frame, text="Image Viewer Section", font=("Arial", 16), fg='white', bg='#2b2b2b')
        self.image_viewer_title.pack(pady=10)

        self.canvas_frame = tk.Frame(self.image_viewer_frame, width=680, height=550, bg='#2b2b2b')  # Dark background
        self.canvas_frame.pack(fill="both", expand=True)
        self.canvas_frame.grid_propagate(False)

    def show_image_in_viewer(self, image_path):
        if self.canvas_image:
            self.canvas_image._imframe.destroy()

        self.canvas_image = CanvasImage(self.canvas_frame, image_path)
        self.canvas_image.grid(row=0, column=0, sticky="nswe")
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
# End Show Single Image Section

# Define the FrameExtractionSection class
class FrameExtractionSection:
    def __init__(self, parent, get_video_path, get_output_path, display_images, set_images_path):
        self.parent = parent
        self.get_video_path = get_video_path
        self.get_output_path = get_output_path
        self.display_images = display_images
        self.set_images_path = set_images_path
        self.configure_extraction_section()

    def configure_extraction_section(self):
        extraction_frame = ctk.CTkFrame(self.parent)
        extraction_frame.pack(fill="x", pady=5)

        extraction_title = ctk.CTkLabel(extraction_frame, text="Frame Extraction", font=("Arial", 14))
        extraction_title.pack(pady=5)

        frame_rate_frame = ctk.CTkFrame(extraction_frame)
        frame_rate_frame.pack(fill="x", pady=5)

        self.frame_rate_slider = ctk.CTkSlider(frame_rate_frame, from_=1, to=30, number_of_steps=29, command=self.update_frame_rate_label)
        self.frame_rate_slider.set(6)
        self.frame_rate_slider.pack(side="left", pady=5)

        self.frame_rate_label = ctk.CTkLabel(frame_rate_frame, text="6 FPS", font=("Arial", 12))
        self.frame_rate_label.pack(side="left", padx=5)

        extract_button = ctk.CTkButton(extraction_frame, text="Extract Frames", command=self.extract_frames)
        extract_button.pack(pady=5)

    def update_frame_rate_label(self, value):
        self.frame_rate_label.configure(text=f"{int(value)} FPS")

    def extract_frames(self):
        frame_rate = int(self.frame_rate_slider.get())
        video_path = self.get_video_path()
        output_path = self.get_output_path()
        if not video_path or not output_path:
            messagebox.showwarning("Warning", "Please select both video and output path.")
            return

        try:
            output_folder = create_video_output_folder(output_path, video_path)
            loaded_image_paths = extract_frames(video_path, output_folder, frame_rate)
            self.set_images_path(output_folder)  # Mettre à jour le chemin des images ici
            self.display_images(loaded_image_paths)
            messagebox.showinfo("Success", f"Frames extracted successfully at {output_folder}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

# Define the ImageResizingSection class
class ImageResizingSection:
    def __init__(self, parent, get_images_path, display_images):
        self.parent = parent
        self.get_images_path = get_images_path
        self.display_images = display_images
        self.configure_resize_section()

    def configure_resize_section(self):
        resize_frame = ctk.CTkFrame(self.parent)
        resize_frame.pack(fill="x", pady=5)

        resize_title = ctk.CTkLabel(resize_frame, text="Resize Images", font=("Arial", 14))
        resize_title.pack(pady=5)

        resize_percent_frame = ctk.CTkFrame(resize_frame)
        resize_percent_frame.pack(fill="x", pady=5)

        self.resize_percent_slider = ctk.CTkSlider(resize_percent_frame, from_=10, to=200, number_of_steps=19, command=self.update_resize_percent_label)
        self.resize_percent_slider.set(100)
        self.resize_percent_slider.pack(side="left", pady=5)

        self.resize_percent_label = ctk.CTkLabel(resize_percent_frame, text="100%", font=("Arial", 12))
        self.resize_percent_label.pack(side="left", padx=5)

        resize_button = ctk.CTkButton(resize_frame, text="Resize Images", command=self.resize_images)
        resize_button.pack(pady=5)

    def update_resize_percent_label(self, value):
        self.resize_percent_label.configure(text=f"{int(value)}%")

    def resize_images(self):
        scale_percent = int(self.resize_percent_slider.get())
        images_path = self.get_images_path()
        if not images_path:
            messagebox.showwarning("Warning", "Please load images or extract frames first.")
            return

        try:
            image_paths = extract_images(images_path)
            resized_image_paths = process_images(image_paths, scale_percent)
            self.display_images(resized_image_paths)
            messagebox.showinfo("Success", "Images resized successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

# Define the BackgroundRemovalSection class
class BackgroundRemovalSection:
    def __init__(self, parent, get_images_path, display_images):
        self.parent = parent
        self.get_images_path = get_images_path
        self.display_images = display_images
        self.bg_removal_algorithm = "rembg"
        self.configure_background_removal_section()

    def configure_background_removal_section(self):
        background_removal_frame = ctk.CTkFrame(self.parent)
        background_removal_frame.pack(fill="x", pady=5)

        background_removal_title = ctk.CTkLabel(background_removal_frame, text="Background Removal", font=("Arial", 14))
        background_removal_title.pack(pady=5)

        self.algorithm_var = ctk.StringVar(value="rembg")
        self.algorithm_combobox = ctk.CTkComboBox(background_removal_frame, values=["rembg", "briarmbg"],
                                                  command=self.update_algorithm, variable=self.algorithm_var)
        self.algorithm_combobox.pack(pady=5)

        remove_background_button = ctk.CTkButton(background_removal_frame, text="Remove Background", command=self.remove_background)
        remove_background_button.pack(pady=5)

    def update_algorithm(self, choice):
        self.bg_removal_algorithm = choice

    def remove_background(self):
        images_path = self.get_images_path()
        if not images_path:
            messagebox.showwarning("Warning", "Please load images or extract frames first.")
            return

        try:
            if self.bg_removal_algorithm == "rembg":
                remove_background_rembg(images_path, images_path)
            else:
                remove_background_briarmbg(images_path, images_path)

            self.display_images(extract_images(images_path))
            messagebox.showinfo("Success", f"Background removed successfully with {self.bg_removal_algorithm}.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

# Define the PhotogrammetrySection class
class PhotogrammetrySection:
    def __init__(self, parent, get_images_path):
        self.parent = parent
        self.get_images_path = get_images_path
        self.processing_option = StringVar(value="point_cloud")
        self.texture_size_var = StringVar(value="2048")
        self.use_gpu_var = tk.BooleanVar(value=False)
        self.output_format_var = StringVar(value="obj")  # Default to obj format
        self.configure_photogrammetry_section()

    def configure_photogrammetry_section(self):
        photogrammetry_frame = ctk.CTkFrame(self.parent)
        photogrammetry_frame.pack(fill="x", pady=5)

        # Adding a scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(photogrammetry_frame, width=250, height=600)
        self.scrollable_frame.pack(fill="both", expand=True, pady=10)

        photogrammetry_title = ctk.CTkLabel(self.scrollable_frame, text="Photogrammetry", font=("Arial", 14))
        photogrammetry_title.grid(row=0, column=0, columnspan=2, pady=5)

        # Place Point Cloud and 3D Model options on the same line
        radio_point_cloud = ctk.CTkRadioButton(self.scrollable_frame, text="Point Cloud", variable=self.processing_option, value="point_cloud")
        radio_point_cloud.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        radio_3d_model = ctk.CTkRadioButton(self.scrollable_frame, text="3D Model", variable=self.processing_option, value="3d_model")
        radio_3d_model.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Align Texture Size label and combobox on the same line
        texture_size_label = ctk.CTkLabel(self.scrollable_frame, text="Texture Size", font=("Arial", 12))
        texture_size_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")

        texture_size_options = ["512", "1024", "2048", "4096", "8192"]
        self.texture_size_combobox = ctk.CTkComboBox(self.scrollable_frame, values=texture_size_options, variable=self.texture_size_var)
        self.texture_size_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        use_gpu_checkbutton = ctk.CTkCheckBox(self.scrollable_frame, text="Use GPU", variable=self.use_gpu_var)
        use_gpu_checkbutton.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        photogrammetry_process_button = ctk.CTkButton(self.scrollable_frame, text="Run Photogrammetry", command=self.run_photogrammetry)
        photogrammetry_process_button.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        # Configure columns to adjust the alignment
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

    def run_script(self, script_name, project_path, folder_name, texture_size, use_gpu, output_format):
        script_path = os.path.join(os.path.dirname(__file__), script_name)

        # Make sure the script is executable
        os.system(f"chmod +x {script_path}")
        
        # Construct the command
        command = f"{script_path} {project_path} {folder_name} {texture_size} {use_gpu}"
        
        # Execute the command
        result = os.system(command)
        
        # Check the result
        if result == 0:
            print(f"{script_name} executed successfully.")
        else:
            print(f"Error executing {script_name} with exit code: {result}")

    def run_photogrammetry(self):
        try:
            images_path = self.get_images_path()
            project_path, folder_name = os.path.split(images_path.rstrip("/"))
            texture_size = self.texture_size_var.get()
            use_gpu = -1 if self.use_gpu_var.get() else -2  # -1 for GPU, -2 for CPU
            output_format = self.output_format_var.get()

            if self.processing_option.get() == "point_cloud":
                self.run_script("colmap_demo.sh", project_path, folder_name, texture_size, use_gpu, output_format)
            else:
                self.run_script("colmap_openmvs.sh", project_path, folder_name, texture_size, use_gpu, output_format)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")



# Define the SidebarSection class
class SidebarSection:
    def __init__(self, parent, choose_output_path_callback):
        self.parent = parent
        self.choose_output_path_callback = choose_output_path_callback
        self.configure_sidebar_section()

    def configure_sidebar_section(self):
        self.sidebar_frame = ctk.CTkFrame(self.parent)
        self.sidebar_frame.grid(row=0, column=2, rowspan=2, sticky="nswe", padx=10, pady=10)

        self.sidebar_title_frame = ctk.CTkFrame(self.sidebar_frame, height=50)
        self.sidebar_title_frame.pack(fill="x", pady=10)  # Add padding between title and top of sidebar
        self.sidebar_title_frame.grid_propagate(False)
        self.sidebar_title = ctk.CTkLabel(self.sidebar_title_frame, text="Process", font=("Arial", 16))
        self.sidebar_title.pack(pady=10)  # Add padding inside the title frame

        self.sidebar_button = ctk.CTkButton(self.sidebar_frame, text="Output path", command=self.choose_output_path_callback)
        self.sidebar_button.pack(pady=20)  # Add vertical padding around the output path button

        self.output_path_label = ctk.CTkLabel(self.sidebar_frame, text="", font=("Arial", 12))
        self.output_path_label.pack(pady=10)  # Add padding between the button and the label

        # Add the Model Viewer Button at the bottom
        self.configure_model_viewer_button()

    def configure_model_viewer_button(self):
        # Create a frame for the Model Viewer Button
        model_viewer_frame = ctk.CTkFrame(self.sidebar_frame)
        model_viewer_frame.pack(side="bottom", fill="x", pady=20)  # Add padding at the bottom of the sidebar

        model_viewer_button = ctk.CTkButton(model_viewer_frame, text="Model Viewer", command=self.launch_model_viewer)
        model_viewer_button.pack(pady=10)  # Add padding around the Model Viewer button

    def launch_model_viewer(self):
        try:
            # Assuming run_viewer.sh is in the same directory as your Python script
            script_path = os.path.join(os.path.dirname(__file__), 'run_viewer.sh')
            
            # Make sure the script is executable
            subprocess.run(["chmod", "+x", script_path], check=True)
            
            # Run the script using subprocess
            subprocess.Popen([script_path])
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while launching the model viewer: {e}")



# Define the PhotogrammetryPage class
class PhotogrammetryPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.images_path = ""
        self.video_path = ""
        self.output_path = "" 
        self.loaded_image_paths = []
        self.input_images_folder = ""

        self.configure_main_layout()

        # Initialize sections
        self.show_images_section = ShowImagesSection(self, self.show_image_in_viewer, self.set_images_path)
        self.show_single_image_section = ShowSingleImageSection(self)
        self.sidebar_section = SidebarSection(self, self.choose_output_path)

        self.frame_extraction_section = FrameExtractionSection(self.sidebar_section.sidebar_frame, self.get_video_path, self.get_output_path, self.display_images, self.set_images_path)
        self.image_resizing_section = ImageResizingSection(self.sidebar_section.sidebar_frame, self.get_images_path, self.display_images)
        self.background_removal_section = BackgroundRemovalSection(self.sidebar_section.sidebar_frame, self.get_images_path, self.display_images)
        self.photogrammetry_section = PhotogrammetrySection(self.sidebar_section.sidebar_frame, self.get_images_path)

        self.configure_video_section()

    def configure_main_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)

    def set_images_path(self, path):
        self.images_path = path

    def choose_output_path(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_path = folder_selected
            self.sidebar_section.output_path_label.configure(text=self.output_path)

    def get_video_path(self):
        return self.video_path

    def get_images_path(self):
        return self.images_path
    
    def get_output_path(self):
       return self.output_path

    def get_loaded_image_paths(self):
        return self.loaded_image_paths

    def get_input_images_folder(self):
        return self.input_images_folder

    def show_image_in_viewer(self, image_path):
        self.show_single_image_section.show_image_in_viewer(image_path)

    def display_images(self, image_paths):
        self.loaded_image_paths = image_paths
        if self.loaded_image_paths:
            self.set_images_path(os.path.dirname(self.loaded_image_paths[0]))
        self.show_images_section.display_images(image_paths)

    def configure_video_section(self):
        self.video_section_frame = ctk.CTkFrame(self, width=700, height=150)
        self.video_section_frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        self.video_section_frame.grid_propagate(False)

        self.video_section_title_frame = ctk.CTkFrame(self.video_section_frame, height=50)
        self.video_section_title_frame.pack(fill="x", pady=5)
        self.video_section_title_frame.grid_propagate(False)
        self.video_section_title = ctk.CTkLabel(self.video_section_title_frame, text="Video Section", font=("Arial", 16))
        self.video_section_title.pack(pady=10)

        self.button_frame = ctk.CTkFrame(self.video_section_frame)
        self.button_frame.pack(fill="x", pady=5)

        self.load_video_button = ctk.CTkButton(self.button_frame, text="Load Videos", command=self.open_video)
        self.load_video_button.pack(side="left", padx=10)

        self.clear_video_button = ctk.CTkButton(self.button_frame, text="Clear", command=self.clear_video)
        self.clear_video_button.pack(side="left", padx=10)

        self.video_info_frame = ctk.CTkFrame(self.video_section_frame, width=680, height=100)
        self.video_info_frame.pack(fill="x", pady=5)

    def open_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[('Video', ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.gif']), ('All Files', '*.*')])
        if self.video_path:
            try:
                self.display_video_info(self.video_path)
            except Exception as e:
                print(f"Unable to load the file: {e}")

    def clear_video(self):
        try:
            self.clear_video_info()
            self.video_path = ""
            print("Video cleared successfully.")
        except Exception as e:
            print(f"Error clearing video: {e}")

    def display_video_info(self, video_path):
        video = cv2.VideoCapture(video_path)
        if video.isOpened():
            video_length = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) / video.get(cv2.CAP_PROP_FPS)
            video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video_info = {
                "Path": video_path,
                "Duration": f"{video_length:.2f} seconds",
                "Width": video_width,
                "Height": video_height
            }
            video.release()
        else:
            video_info = {
                "Error": "Could not open the video."
            }

        for widget in self.video_info_frame.winfo_children():
            widget.destroy()

        for key, value in video_info.items():
            label = ctk.CTkLabel(self.video_info_frame, text=f"{key}: {value}", font=("Arial", 18, "bold" if key != "Error" else "normal"))
            label.pack(pady=5, anchor="w")

    def clear_video_info(self):
        for widget in self.video_info_frame.winfo_children():
            widget.destroy()

# Define the main application
class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sylva3D Photogrammetry")
        self.geometry("1200x800")

        self.photogrammetry_page = PhotogrammetryPage(self)
        self.photogrammetry_page.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = Application()
    app.mainloop()
