# Import required libraries for the application
import cv2  # Library for image processing operations
import tkinter as tk  # Library for creating the graphical user interface
from tkinter import filedialog, Scale, messagebox  # Tkinter modules for file selection, sliders, and dialog boxes
from PIL import Image, ImageTk  # PIL for image conversion and display in Tkinter

# Define the main application class using object-oriented principles
class PhotoEditorApp:
    def __init__(self, window):
        # Initialize the main application window
        self.window = window  # Store the Tkinter root window
        self.window.title("Photo Editor")  # Set the window title
        self.setup_window()  # Configure the window's appearance and size
        self.original_image = None  # Store the original loaded image
        self.edited_image = None  # Store the edited (cropped/resized) image
        self.base_edited_image = None  # Store the original cropped image before resizing
        self.history = []  # List to store states for undo functionality
        self.redo_history = []  # List to store states for redo functionality
        self.is_cropping = False  # Flag to track cropping mode
        self.crop_start_x = None  # X-coordinate for crop rectangle start
        self.crop_start_y = None  # Y-coordinate for crop rectangle start
        self.crop_end_x = None  # X-coordinate for crop rectangle end
        self.crop_end_y = None  # Y-coordinate for crop rectangle end
        self.initialize_ui()  # Set up the user interface components
        self.setup_shortcuts()  # Bind keyboard shortcuts to actions
        self.window.protocol("WM_DELETE_WINDOW", self.handle_exit)  # Handle window close event

    def setup_window(self):
        # Configure the main window's size and position
        screen_w = self.window.winfo_screenwidth()  # Get the screen width
        screen_h = self.window.winfo_screenheight()  # Get the screen height
        win_w = int(screen_w * 0.75)  # Set window width to 75% of screen width
        win_h = int(screen_h * 0.75)  # Set window height to 75% of screen height
        pos_x = (screen_w - win_w) // 2  # Calculate x position to center the window
        pos_y = (screen_h - win_h) // 2  # Calculate y position to center the window
        self.window.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")  # Set window size and position
        self.window.configure(bg="#F6F4E8")  # Set background color to light beige from palette

    def initialize_ui(self):
        # Create and arrange all UI components
        self.button_panel = tk.Frame(self.window, bg="#F6F4E8")  # Create a frame for buttons
        self.button_panel.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)  # Place the button panel at the top
        self.original_display = tk.Frame(self.window, bg="#F6F4E8")  # Create a frame for the original image
        self.original_display.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.BOTH)  # Place the original image frame
        self.edited_display = tk.Frame(self.window, bg="#F6F4E8")  # Create a frame for the edited image
        self.edited_display.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.BOTH)  # Place the edited image frame
        self.controls = tk.Frame(self.window, bg="#F6F4E8")  # Create a frame for control widgets
        self.controls.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)  # Place the controls frame on the right

        # Create canvases for displaying images
        self.original_canvas = tk.Canvas(self.original_display, width=450, height=450, bg="#BACEC1", highlightthickness=0)  # Canvas for original image with palette color
        self.original_canvas.pack(pady=10, expand=True, anchor=tk.CENTER)  # Center the original canvas
        self.edited_canvas = tk.Canvas(self.edited_display, width=450, height=450, bg="#BACEC1", highlightthickness=0)  # Canvas for edited image with palette color
        self.edited_canvas.pack(pady=10, expand=True, anchor=tk.CENTER)  # Center the edited canvas

        # Define button style using the color palette
        btn_style = {"bg": "#1D3124", "fg": "#F6F4E8", "padx": 8, "pady": 4}  # Dark green background, light beige text

        # Configure grid layout for buttons
        self.button_panel.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)  # Make columns expandable

        # Create and place buttons with the specified color palette
        self.btn_load = tk.Button(self.button_panel, text="Open Image", command=self.open_image, **btn_style)  # Button to load an image
        self.btn_load.grid(row=0, column=0, padx=5, sticky="ew")  # Place the load button
        self.btn_crop = tk.Button(self.button_panel, text="Crop Image", command=self.begin_crop, **btn_style)  # Button to start cropping
        self.btn_crop.grid(row=0, column=1, padx=5, sticky="ew")  # Place the crop button
        self.btn_grayscale = tk.Button(self.button_panel, text="To Grayscale", command=self.apply_grayscale, **btn_style)  # Button for grayscale conversion
        self.btn_grayscale.grid(row=0, column=2, padx=5, sticky="ew")  # Place the grayscale button
        self.btn_rotate = tk.Button(self.button_panel, text="Rotate 90°", command=self.apply_rotation, **btn_style)  # Button to rotate the image
        self.btn_rotate.grid(row=0, column=3, padx=5, sticky="ew")  # Place the rotate button
        self.btn_save = tk.Button(self.button_panel, text="Save Image", command=self.save_edited_image, **btn_style)  # Button to save the image
        self.btn_save.grid(row=0, column=4, padx=5, sticky="ew")  # Place the save button
        self.btn_undo = tk.Button(self.button_panel, text="Undo", command=self.perform_undo, **btn_style)  # Button for undo action
        self.btn_undo.grid(row=0, column=5, padx=5, sticky="ew")  # Place the undo button
        self.btn_redo = tk.Button(self.button_panel, text="Redo", command=self.perform_redo, **btn_style)  # Button for redo action
        self.btn_redo.grid(row=0, column=6, padx=5, sticky="ew")  # Place the redo button

        # Create a slider for resizing with palette colors
        self.size_slider = Scale(self.button_panel, from_=10, to=200, orient=tk.HORIZONTAL, label="Size (%)", command=self.adjust_size, bg="#F6F4E8", fg="#1D3124", highlightbackground="#E59560")  # Slider for resizing
        self.size_slider.grid(row=1, column=0, columnspan=7, padx=5, pady=10, sticky="ew")  # Place the slider across columns

        # Bind mouse events for cropping
        self.original_canvas.bind("<ButtonPress-1>", self.start_crop_selection)  # Bind left mouse click to start cropping
        self.original_canvas.bind("<B1-Motion>", self.update_crop_selection)  # Bind mouse drag to update crop rectangle
        self.original_canvas.bind("<ButtonRelease-1>", self.finish_crop_selection)  # Bind mouse release to complete cropping
        self.window.bind("<Configure>", self.handle_resize)  # Bind window resize event to update display

    def setup_shortcuts(self):
        # Assign keyboard shortcuts to various actions
        self.window.bind("<Control-o>", lambda e: self.open_image())  # Ctrl+O to open an image
        self.window.bind("<Control-s>", lambda e: self.save_edited_image())  # Ctrl+S to save the image
        self.window.bind("<Control-z>", lambda e: self.perform_undo())  # Ctrl+Z to undo
        self.window.bind("<Control-y>", lambda e: self.perform_redo())  # Ctrl+Y to redo
        self.window.bind("<Control-g>", lambda e: self.apply_grayscale())  # Ctrl+G for grayscale
        self.window.bind("<Control-r>", lambda e: self.apply_rotation())  # Ctrl+R to rotate

    def open_image(self):
        # Load an image from the local device
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])  # Open file dialog for image selection
        if file_path:  # Check if a file was selected
            self.original_image = cv2.imread(file_path)  # Load the image using OpenCV
            if self.original_image is not None:  # Verify the image loaded successfully
                self.show_image(self.original_image, self.original_canvas)  # Display the image on the original canvas
                self.edited_image = None  # Clear the edited image
                self.base_edited_image = None  # Clear the base edited image
                self.show_image(None, self.edited_canvas)  # Clear the edited canvas
                self.history = [{"original": self.original_image.copy()}]  # Initialize history with the loaded image
                self.redo_history.clear()  # Clear the redo history
            else:
                messagebox.showerror("Error", "Unable to load the image.")  # Show error if loading fails

    def show_image(self, image, canvas):
        # Display an image on the specified canvas
        if image is not None:  # Check if an image is provided
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert image from BGR to RGB for display
            pil_img = Image.fromarray(rgb_image)  # Convert to PIL image format
            canvas_w = canvas.winfo_width()  # Get the canvas width
            canvas_h = canvas.winfo_height()  # Get the canvas height
            if canvas_w <= 1 or canvas_h <= 1:  # Check for invalid canvas dimensions
                return  # Exit if canvas is not properly sized
            img_w, img_h = pil_img.size  # Get image dimensions
            scale = min(canvas_w / img_w, canvas_h / img_h)  # Calculate scaling factor to fit image
            new_w = int(img_w * scale)  # Compute new image width
            new_h = int(img_h * scale)  # Compute new image height
            resized_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)  # Resize image with high-quality interpolation
            tk_img = ImageTk.PhotoImage(resized_img)  # Convert to Tkinter-compatible image
            canvas.image_ref = tk_img  # Store image reference to prevent garbage collection
            x_pos = (canvas_w - new_w) // 2  # Calculate x position to center image
            y_pos = (canvas_h - new_h) // 2  # Calculate y position to center image
            canvas.delete("all")  # Clear existing content on the canvas
            canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=tk_img)  # Display the image
            canvas.config(width=canvas_w, height=canvas_h)  # Update canvas dimensions
        else:
            canvas.delete("all")  # Clear the canvas if no image is provided
            canvas.image_ref = None  # Remove image reference
            canvas.config(width=450, height=450)  # Reset canvas to default size

    def begin_crop(self):
        # Initiate the cropping process
        if self.original_image is not None:  # Check if an image is loaded
            self.is_cropping = True  # Enable cropping mode
            messagebox.showinfo("Crop Mode", "Click and drag on the original image to select a crop area.")  # Instruct user
        else:
            messagebox.showwarning("Warning", "Load an image before cropping.")  # Warn if no image is loaded

    def start_crop_selection(self, event):
        # Handle mouse press to start cropping
        if self.is_cropping and event.widget == self.original_canvas:  # Check if in cropping mode and on correct canvas
            self.crop_start_x, self.crop_start_y = event.x, event.y  # Record starting coordinates

    def update_crop_selection(self, event):
        # Update the crop rectangle while dragging
        if self.is_cropping and event.widget == self.original_canvas:  # Ensure in cropping mode
            self.original_canvas.delete("crop_rect")  # Remove previous rectangle
            self.original_canvas.create_rectangle(self.crop_start_x, self.crop_start_y, event.x, event.y, outline="#E59560", tags="crop_rect")  # Draw new rectangle with palette color

    def finish_crop_selection(self, event):
        # Complete the cropping process on mouse release
        if self.is_cropping and event.widget == self.original_canvas:  # Verify conditions
            self.crop_end_x, self.crop_end_y = event.x, event.y  # Record ending coordinates
            self.execute_crop()  # Perform the crop operation
            self.is_cropping = False  # Disable cropping mode
            self.original_canvas.delete("crop_rect")  # Remove the crop rectangle

    def execute_crop(self):
        # Crop the image based on selected coordinates
        if self.original_image is None:  # Check if an image is loaded
            return  # Exit if no image
        canvas_w = self.original_canvas.winfo_width()  # Get canvas width
        canvas_h = self.original_canvas.winfo_height()  # Get canvas height
        img_w, img_h = self.original_image.shape[1], self.original_image.shape[0]  # Get image dimensions
        scale_x = img_w / canvas_w  # Calculate x scaling factor
        scale_y = img_h / canvas_h  # Calculate y scaling factor
        x1 = int(min(self.crop_start_x, self.crop_end_x) * scale_x)  # Convert start x to image coordinates
        y1 = int(min(self.crop_start_y, self.crop_end_y) * scale_y)  # Convert start y to image coordinates
        x2 = int(max(self.crop_start_x, self.crop_end_x) * scale_x)  # Convert end x to image coordinates
        y2 = int(max(self.crop_start_y, self.crop_end_y) * scale_y)  # Convert end y to image coordinates
        x1 = max(0, min(x1, img_w - 1))  # Clamp x1 to valid range
        y1 = max(0, min(y1, img_h - 1))  # Clamp y1 to valid range
        x2 = max(0, min(x2, img_w - 1))  # Clamp x2 to valid range
        y2 = max(0, min(y2, img_h - 1))  # Clamp y2 to valid range
        if x1 >= x2 or y1 >= y2:  # Check for valid crop area
            messagebox.showwarning("Warning", "Invalid crop selection. Try again.")  # Warn if selection is invalid
            return
        self.edited_image = self.original_image[y1:y2, x1:x2]  # Crop the image
        self.base_edited_image = self.edited_image.copy()  # Store the cropped image as base for resizing
        self.show_image(self.edited_image, self.edited_canvas)  # Display the cropped image
        self.history.append({"original": self.original_image.copy(), "edited": self.edited_image.copy() if self.edited_image is not None else None, "base_edited": self.base_edited_image.copy() if self.base_edited_image is not None else None})  # Save state
        self.redo_history.clear()  # Clear redo history

    def adjust_size(self, value):
        # Resize the edited image based on slider value
        if self.base_edited_image is not None:  # Check if there is an image to resize
            scale_factor = int(value) / 100  # Convert slider value to scaling factor
            base_h, base_w = self.base_edited_image.shape[:2]  # Get base image dimensions
            new_w = int(base_w * scale_factor)  # Calculate new width
            new_h = int(base_h * scale_factor)  # Calculate new height
            if new_w < 1 or new_h < 1:  # Prevent resizing to invalid dimensions
                return
            self.edited_image = cv2.resize(self.base_edited_image, (new_w, new_h), interpolation=cv2.INTER_AREA)  # Resize image
            self.show_image(self.edited_image, self.edited_canvas)  # Display resized image
            self.history.append({"original": self.original_image.copy(), "edited": self.edited_image.copy(), "base_edited": self.base_edited_image.copy()})  # Save state
            self.redo_history.clear()  # Clear redo history

    def apply_grayscale(self):
        # Convert the edited image to grayscale
        if self.edited_image is not None:  # Check if there is an edited image
            gray_image = cv2.cvtColor(self.edited_image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
            self.edited_image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)  # Convert back to BGR for display
            self.show_image(self.edited_image, self.edited_canvas)  # Display grayscale image
            self.history.append({"original": self.original_image.copy(), "edited": self.edited_image.copy(), "base_edited": self.base_edited_image.copy()})  # Save state
            self.redo_history.clear()  # Clear redo history

    def apply_rotation(self):
        # Rotate the edited image by 90 degrees
        if self.edited_image is not None:  # Check if there is an edited image
            self.edited_image = cv2.rotate(self.edited_image, cv2.ROTATE_90_CLOCKWISE)  # Rotate clockwise
            self.show_image(self.edited_image, self.edited_canvas)  # Display rotated image
            self.history.append({"original": self.original_image.copy(), "edited": self.edited_image.copy(), "base_edited": self.base_edited_image.copy()})  # Save state
            self.redo_history.clear()  # Clear redo history

    def save_edited_image(self):
        # Save the edited image to a file
        if self.edited_image is not None:  # Check if there is an image to save
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])  # Open save dialog
            if save_path:  # Check if a path was selected
                cv2.imwrite(save_path, cv2.cvtColor(self.edited_image, cv2.COLOR_BGR2RGB))  # Save the image
                messagebox.showinfo("Success", "Image saved successfully.")  # Show success message
        else:
            messagebox.showwarning("Warning", "No edited image to save.")  # Warn if no image is available

    def perform_undo(self):
        # Undo the last action
        if len(self.history) > 1:  # Check if there are states to undo
            self.redo_history.append(self.history.pop())  # Move current state to redo history
            state = self.history[-1]  # Get the previous state
            self.original_image = state["original"].copy()  # Restore original image
            self.show_image(self.original_image, self.original_canvas)  # Display original image
            self.edited_image = state["edited"].copy() if state["edited"] is not None else None  # Restore edited image
            self.base_edited_image = state["base_edited"].copy() if state["base_edited"] is not None else None  # Restore base edited image
            self.show_image(self.edited_image, self.edited_canvas)  # Display edited image
        elif len(self.history) == 1:  # Handle initial state
            state = self.history[0]  # Get the initial state
            self.original_image = state["original"].copy()  # Restore initial image
            self.show_image(self.original_image, self.original_canvas)  # Display initial image
            self.edited_image = None  # Clear edited image
            self.base_edited_image = None  # Clear base edited image
            self.show_image(None, self.edited_canvas)  # Clear edited canvas
        else:
            messagebox.showinfo("Info", "No actions to undo.")  # Inform user if nothing to undo

    def perform_redo(self):
        # Redo the last undone action
        if self.redo_history:  # Check if there are states to redo
            state = self.redo_history.pop()  # Get the redo state
            self.history.append(state)  # Add to history
            self.original_image = state["original"].copy()  # Restore original image
            self.show_image(self.original_image, self.original_canvas)  # Display original image
            self.edited_image = state["edited"].copy() if state["edited"] is not None else None  # Restore edited image
            self.base_edited_image = state["base_edited"].copy() if state["base_edited"] is not None else None  # Restore base edited image
            self.show_image(self.edited_image, self.edited_canvas)  # Display edited image
        else:
            messagebox.showinfo("Info", "No actions to redo.")  # Inform user if nothing to redo

    def handle_resize(self, event):
        # Update image display when the window is resized
        if self.original_image is not None:  # Check if original image exists
            self.show_image(self.original_image, self.original_canvas)  # Redisplay original image
        if self.edited_image is not None:  # Check if edited image exists
            self.show_image(self.edited_image, self.edited_canvas)  # Redisplay edited image

    def handle_exit(self):
        # Handle the window close event
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):  # Confirm exit with user
            self.window.destroy()  # Close the application window

# Main entry point for the application
if __name__ == "__main__":
    root = tk.Tk()  # Create the main Tkinter window
    editor = PhotoEditorApp(root)  # Instantiate the application
    root.mainloop()  # Start the Tkinter event loop
