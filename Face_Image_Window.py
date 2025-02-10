import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
import logging


class FaceImageWindow:
    def __init__(self, parent, face_number):
        self.logger = logging.getLogger('FaceImageWindow')
        self.logger.debug(f"Initializing Face Image Window for face number {face_number}")
        
        self.window = tk.Toplevel(parent)
        
        try:
            # Calculate if it's male or female and which number pair it is
            is_male = (face_number % 2) == 0  # Even numbers are male
            pair_number = (face_number // 2)
            gender = "Male" if is_male else "Female"
            
            # Format the title and display text
            display_text = f"{gender} {str(pair_number).zfill(2)}"
            self.logger.debug(f"Displaying face: {display_text}")
            
            self.window.title(f"Character Face - {display_text}")
            self.window.geometry("400x500")
            
            self.face_number = face_number
            self._load_and_display_image()
            
        except Exception as e:
            self.logger.error(f"Error initializing face window: {str(e)}", exc_info=True)
            raise
    
    def _load_and_display_image(self):
        self.logger.debug("Loading face image")
        try:
            gender = "Male" if self.face_number % 2 == 0 else "Female"
            pair_number = str(self.face_number // 2).zfill(2)
            
            image_path = os.path.join("Face_Images", f"{gender} {pair_number}.png")
            self.logger.debug(f"Loading image from path: {image_path}")
            
            if os.path.exists(image_path):
                # Open and resize the image
                original_image = Image.open(image_path)
                resized_image = original_image.resize((300, 300), Image.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(resized_image)
                
                # Create label to display image
                image_label = ttk.Label(self.window, image=photo)
                image_label.image = photo  # Keep a reference
                image_label.pack(pady=20)
                
                # Update the label to show the new format
                ttk.Label(
                    self.window, 
                    text=f"Face: {gender} {pair_number}", 
                    font=("", 12)
                ).pack(pady=10)
                
                self.logger.debug("Face image loaded and displayed successfully")
            
            else:
                self.logger.warning(f"Image file not found: {image_path}")
                ttk.Label(
                    self.window, 
                    text=f"No image found for {gender} {pair_number}", 
                    foreground="red"
                ).pack(pady=20)
                
        except Exception as e:
            self.logger.error(f"Error loading face image: {str(e)}", exc_info=True)
            ttk.Label(
                self.window,
                text=f"Error loading image: {str(e)}",
                foreground="red"
            ).pack(pady=20)