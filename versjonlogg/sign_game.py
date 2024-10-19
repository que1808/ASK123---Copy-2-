import tkinter as tk
from tkinter import messagebox
import random
import os
import sys
from PIL import Image, ImageTk

# Function to get the resource path
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SignGame:
    def __init__(self, root, image_folder):
        self.root = root
        self.root.title("ASK123 - Tegn til tale spill")
        self.score = 0
        self.streak = 0
        self.current_image = None

        # Load all images from the specified folder
        self.image_folder = image_folder
        self.image_files = sorted([f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))])
        
        # Create a dictionary mapping images to their corresponding answers (based on filename, no extension)
        self.image_to_answer = {img: os.path.splitext(img)[0] for img in self.image_files}

        # Debugging: print image to answer mapping to check correctness
        print("Image to answer mapping:")
        for img, ans in self.image_to_answer.items():
            print(f"{img}: {ans}")

        # Create GUI elements
        self.label = tk.Label(root, text="Hva er tegnet?")
        self.label.pack(pady=10)

        self.image_label = tk.Label(root)
        self.image_label.pack()

        self.entry = tk.Entry(root)
        self.entry.pack(pady=10)

        self.submit_button = tk.Button(root, text="Submit", command=self.check_answer)
        self.submit_button.pack(pady=10)

        self.score_label = tk.Label(root, text="Score: 0")
        self.score_label.pack(pady=10)

        self.streak_label = tk.Label(root, text="Streak: 0")
        self.streak_label.pack(pady=10)

        # Start game by loading a random image
        self.load_new_image()

    def load_new_image(self):
        """Load a random image and display it."""
        self.current_image = random.choice(self.image_files)
        self.correct_answer = self.image_to_answer.get(self.current_image, "Ingen svar funnet")

        img_path = resource_path(os.path.join(self.image_folder, self.current_image))
        try:
            img = Image.open(img_path)
            img = img.resize((300, 300), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            self.image_label.configure(image=img)
            self.image_label.image = img  # Keep a reference to avoid garbage collection
        except Exception as e:
            print(f"Error loading image: {e}")
            messagebox.showerror("Error", f"Kunne ikke laste inn bildet: {e}")

    def check_answer(self):
        """Check if the entered answer matches the filename without extension (case insensitive)."""
        user_input = self.entry.get().strip().lower()  # Convert user input to lowercase
        if user_input == self.correct_answer.lower():  # Convert correct answer to lowercase
            self.score += 1
            self.streak += 1
            messagebox.showinfo("Riktig!", "Bra jobbet!")
        else:
            self.streak = 0
            messagebox.showerror("Feil!", f"Feil svar! Det riktige svaret var '{self.correct_answer}'.")

        # Update labels
        self.score_label.config(text=f"Score: {self.score}")
        self.streak_label.config(text=f"Streak: {self.streak}")

        # Clear the entry and load a new image
        self.entry.delete(0, tk.END)
        self.load_new_image()

# Set up the main window and game
root = tk.Tk()
image_folder = resource_path("images")  # Use resource_path for images

game = SignGame(root, image_folder)
root.mainloop()
