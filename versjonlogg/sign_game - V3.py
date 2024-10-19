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
    def __init__(self, root, base_folder):
        self.root = root
        self.root.title("ASK123 - Tegn til tale spill")

        # Set window size to 800x600
        self.root.geometry("800x600")

        self.base_folder = base_folder
        self.category_stats = {}  # Holds the number of correct answers per category
        self.total_images = {}    # Holds the total number of images per category
        self.current_category = None

        # Variables for score, streak, and high score
        self.score = 0
        self.streak = 0
        self.high_score = 0

        # Load the categories and statistics
        self.load_categories()
        self.load_category_stats()

        # Show the start menu when the game starts
        self.show_start_menu()

    def load_categories(self):
        """Load all categories (folders) dynamically from the base folder."""
        categories_path = resource_path(self.base_folder)
        self.categories = [d for d in os.listdir(categories_path) if os.path.isdir(os.path.join(categories_path, d))]

    def load_category_stats(self):
        """Load or initialize the stats for each category."""
        for category in self.categories:
            self.category_stats[category] = 0  # Initializing with 0 correct answers
            category_path = os.path.join(self.base_folder, category)
            images = [f for f in os.listdir(category_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
            self.total_images[category] = len(images)  # Total number of images in each category

    def show_start_menu(self):
        """Display the start menu with category buttons and percentage of correct answers."""
        # Clear the current window content
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Velg en kategori:", font=("Helvetica", 16)).pack(pady=20)

        for category in self.categories:
            self.create_category_button(category)

        # Button for playing with all categories
        tk.Button(self.root, text="Alle kategorier", command=self.use_all_categories, height=2, width=20).pack(pady=10)

    def create_category_button(self, category):
        """Create a button for each category with percentage display."""
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        # Category button
        button = tk.Button(frame, text=category, command=lambda c=category: self.use_category(c), height=2, width=20)
        button.pack(side=tk.LEFT)

        # Calculate percentage of correct answers
        correct = self.category_stats.get(category, 0)
        total = self.total_images.get(category, 1)
        percentage = (correct / total) * 100 if total > 0 else 0

        # Display percentage label
        percentage_label = tk.Label(frame, text=f"Du kan {percentage:.1f}% av tegnene", font=("Helvetica", 10))
        percentage_label.pack(side=tk.LEFT, padx=10)

    def use_category(self, category):
        """Start quiz for a specific category."""
        self.current_category = category
        self.load_images_from_folder(category)
        self.start_quiz()

    def use_all_categories(self):
        """Start quiz with all categories."""
        self.current_category = "Alle kategorier"
        all_images = []
        for category in self.categories:
            all_images.extend(self.load_images_from_folder(category, add_to_pool=False))
        self.image_pool = random.sample(all_images, len(all_images))
        self.start_quiz()

    def load_images_from_folder(self, category, add_to_pool=True):
        """Load images from the given category folder and return the image list."""
        folder_path = os.path.join(self.base_folder, category)
        images = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        image_to_answer = {img: os.path.splitext(img)[0] for img in images}
        self.image_to_answer = image_to_answer

        if add_to_pool:
            self.image_pool = random.sample(images, len(images))

        return images

    def start_quiz(self):
        """Set up the quiz interface."""
        for widget in self.root.winfo_children():
            widget.destroy()

        # Show current category at the top of the screen
        tk.Label(self.root, text=f"Kategori: {self.current_category}", font=("Helvetica", 16)).pack(pady=10)

        # Back button to return to the start menu
        back_button = tk.Button(self.root, text="Tilbake", command=self.show_start_menu)
        back_button.pack(pady=5)

        self.score = 0
        self.streak = 0
        self.feedback_label = tk.Label(self.root, text="", font=("Helvetica", 12))
        self.feedback_label.pack(pady=10)

        self.image_label = tk.Label(self.root)
        self.image_label.pack(pady=20)

        self.entry = tk.Entry(self.root, font=("Helvetica", 14), width=30)
        self.entry.pack(pady=10)
        self.entry.focus_set()

        # Center the "Submit" button
        self.submit_button = tk.Button(self.root, text="Submit", command=self.check_answer, height=2, width=10)
        self.submit_button.pack(pady=10)

        # Display score, streak, and high score
        self.score_label = tk.Label(self.root, text=f"Score: {self.score}", font=("Helvetica", 12))
        self.score_label.pack()

        self.streak_label = tk.Label(self.root, text=f"Streak: {self.streak}", font=("Helvetica", 12))
        self.streak_label.pack()

        self.high_score_label = tk.Label(self.root, text=f"High Score: {self.high_score}", font=("Helvetica", 12))
        self.high_score_label.pack()

        # Re-bind the Enter key to submit the answer
        self.root.bind('<Return>', self.enter_key_pressed)

        # Bind mouse clicks outside the entry box to clear focus
        self.root.bind('<Button-1>', self.handle_click)

        self.load_new_image()

    def load_new_image(self):
        """Load a new image for the quiz."""
        if not self.image_pool:
            self.show_end_screen()
            return

        self.current_image = self.image_pool.pop()
        self.correct_answer = self.image_to_answer.get(self.current_image, "Ingen svar funnet")

        img_path = resource_path(os.path.join(self.base_folder, self.current_category, self.current_image))
        img = Image.open(img_path)
        img = img.resize((300, 300), Image.LANCZOS)  # Changed to 300x300 for better spacing
        img = ImageTk.PhotoImage(img)
        self.image_label.configure(image=img)
        self.image_label.image = img  # Keep a reference to avoid garbage collection

    def enter_key_pressed(self, event):
        """Handle pressing the Enter key to check the answer."""
        self.check_answer()

    def check_answer(self):
        """Check if the answer is correct."""
        user_input = self.entry.get().strip().lower()
        if user_input == self.correct_answer.lower():
            self.score += 1
            self.streak += 1
            if self.score > self.high_score:
                self.high_score = self.score  # Update high score if current score is higher
            self.feedback_label.config(text="Riktig svar!", fg="green")
        else:
            self.streak = 0  # Reset streak if the answer is incorrect
            self.feedback_label.config(text=f"Feil svar! Riktig svar var '{self.correct_answer}'", fg="red")

        self.entry.delete(0, tk.END)
        self.update_labels()
        self.load_new_image()

    def update_labels(self):
        """Update the score, streak, and high score labels."""
        self.score_label.config(text=f"Score: {self.score}")
        self.streak_label.config(text=f"Streak: {self.streak}")
        self.high_score_label.config(text=f"High Score: {self.high_score}")

    def show_end_screen(self):
        """Display end screen when the quiz is finished."""
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text=f"Gratulerer! Du har fullført kategorien.", font=("Helvetica", 16)).pack(pady=20)
        tk.Button(self.root, text="Tilbake til hovedmeny", command=self.show_start_menu, height=2, width=20).pack(pady=10)

    def handle_click(self, event):
        """Handle clicks outside the entry box to clear focus and allow shortcuts."""
        if event.widget != self.entry:
            self.root.focus()

    def save_stats(self):
        """Save stats to a file (for future implementation)."""
        pass

# Set up the main window and game
root = tk.Tk()
base_folder = resource_path("Kategorier")  # Use the "Kategorier" folder as the base

game = SignGame(root, base_folder)
root.mainloop()
