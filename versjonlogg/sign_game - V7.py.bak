import tkinter as tk
from tkinter import messagebox, ttk
import random
import os
import sys
import json
from PIL import Image, ImageTk

def resource_path(relative_path):
  """ Get absolute path to resource, works for development and for PyInstaller """
  try:
      base_path = sys._MEIPASS
  except AttributeError:
      base_path = os.path.abspath(".")
  return os.path.join(base_path, relative_path)

class SignGame:
  def __init__(self, root, base_folder):
      self.root = root
      self.root.title("ASK123 - Tegn til tale spill")
      self.root.geometry("1280x960")
      self.root.configure(bg="#b0bec5")

      self.base_folder = base_folder
      self.category_stats = {}
      self.total_images = {}
      self.current_category = None

      self.score = 0
      self.streak = 0
      self.high_score = 0
      self.total_questions = 0
      self.answered_questions = 0
      self.hint_used = False

      self.player_name = None
      self.players_dir = "players"
      os.makedirs(self.players_dir, exist_ok=True)

      self.current_difficulty = "easy"

      self.show_welcome_screen()
      self.load_player_menu()

  def show_welcome_screen(self):
      welcome_window = tk.Toplevel(self.root)
      welcome_window.title("Velkommen til ASK123")
      welcome_window.geometry("600x400")
      welcome_window.configure(bg="#b0bec5")

      tk.Label(welcome_window, text="ASK123", font=("Helvetica", 36, "bold"), bg="#b0bec5").pack(pady=20)

      explanation_text = """
      ASK (Alternativ og Supplerende Kommunikasjon) er tegn til tale 
      som hjelper barn å kommunisere mer effektivt.

      Alle barn kan dra nytte av ASK fordi det:
      • Støtter språkutvikling
      • Forbedrer kommunikasjonsevner
      • Øker forståelse og uttrykksevne
      """
      tk.Label(welcome_window, text=explanation_text, font=("Helvetica", 12), bg="#b0bec5", justify=tk.LEFT).pack(pady=20)

      tk.Button(welcome_window, text="Start spillet", command=welcome_window.destroy, 
                font=("Helvetica", 14), bg="#78909c").pack(pady=20)

      self.root.wait_window(welcome_window)

  def load_player_menu(self):
      for widget in self.root.winfo_children():
          widget.destroy()

      tk.Label(self.root, text="Velkommen! Velg eller opprett en profil:", font=("Helvetica", 20, "bold"), bg="#b0bec5").pack(pady=20)

      player_files = [f.replace(".json", "") for f in os.listdir(self.players_dir) if f.endswith(".json")]
      if player_files:
          tk.Label(self.root, text="Eksisterende spillere:", font=("Helvetica", 14), bg="#b0bec5").pack(pady=10)
          for player in player_files:
              frame = tk.Frame(self.root, bg="#b0bec5")
              frame.pack(pady=5)
              tk.Button(frame, text=player, font=("Helvetica", 12), bg="#78909c",
                        command=lambda p=player: self.select_player(p)).pack(side=tk.LEFT)
              tk.Button(frame, text="Slett", font=("Helvetica", 12), bg="#e57373",
                        command=lambda p=player: self.delete_player(p)).pack(side=tk.LEFT, padx=10)

      tk.Label(self.root, text="Opprett ny spiller:", font=("Helvetica", 14), bg="#b0bec5").pack(pady=20)
      self.new_player_entry = tk.Entry(self.root, font=("Helvetica", 14))
      self.new_player_entry.pack(pady=10)
      tk.Button(self.root, text="Opprett spiller", font=("Helvetica", 12), bg="#78909c", command=self.create_player).pack(pady=10)

  def create_player(self):
      player_name = self.new_player_entry.get().strip()
      if player_name:
          player_file = os.path.join(self.players_dir, f"{player_name}.json")
          if os.path.exists(player_file):
              messagebox.showerror("Feil", "Spilleren finnes allerede. Velg et annet navn.")
          else:
              self.player_name = player_name
              self.save_progress()
              self.load_categories()
              self.load_category_stats()
              self.show_start_menu()

  def delete_player(self, player_name):
      response = messagebox.askyesno("Bekreftelse", f"Er du sikker på at du vil slette spilleren {player_name}?")
      if response:
          player_file = os.path.join(self.players_dir, f"{player_name}.json")
          if os.path.exists(player_file):
              os.remove(player_file)
              messagebox.showinfo("Slettet", f"Spilleren {player_name} er slettet.")
              self.load_player_menu()
          else:
              messagebox.showerror("Feil", f"Spilleren {player_name} finnes ikke.")

  def reset_progress(self):
      response = messagebox.askyesno("Bekreftelse", "Er du sikker på at du vil tilbakestille progresjonen din?")
      if response and self.player_name:
          self.score = 0
          self.streak = 0
          self.high_score = 0
          self.category_stats = {category: 0 for category in self.categories}
          self.save_progress()
          messagebox.showinfo("Tilbakestill", f"Progresjonen til {self.player_name} er tilbakestilt.")

  def select_player(self, player_name):
      self.player_name = player_name
      self.load_progress()
      self.load_categories()
      self.load_category_stats()
      self.show_start_menu()

  def load_progress(self):
      if self.player_name:
          player_file = os.path.join(self.players_dir, f"{self.player_name}.json")
          if os.path.exists(player_file):
              with open(player_file, "r") as f:
                  progress_data = json.load(f)
                  self.category_stats = progress_data.get("category_stats", {})
                  self.score = progress_data.get("score", 0)
                  self.streak = progress_data.get("streak", 0)
                  self.high_score = progress_data.get("high_score", 0)

  def save_progress(self):
      if self.player_name:
          player_file = os.path.join(self.players_dir, f"{self.player_name}.json")
          progress_data = {
              "category_stats": self.category_stats,
              "score": self.score,
              "streak": self.streak,
              "high_score": self.high_score
          }
          with open(player_file, "w") as f:
              json.dump(progress_data, f)

  def load_categories(self):
      categories_path = resource_path(self.base_folder)
      self.categories = [d for d in os.listdir(categories_path) if os.path.isdir(os.path.join(categories_path, d))]
      self.assign_category_colors()

  def assign_category_colors(self):
      colors = ["#FFB3BA", "#BAFFC9", "#BAE1FF", "#FFFFBA", "#FFDFBA", "#E0BBE4"]
      self.category_colors = {}
      for i, category in enumerate(self.categories):
          self.category_colors[category] = colors[i % len(colors)]

  def load_category_stats(self):
      for category in self.categories:
          if category not in self.category_stats:
              self.category_stats[category] = 0
          category_path = os.path.join(self.base_folder, category)
          images = [f for f in os.listdir(category_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
          self.total_images[category] = len(images)

  def show_start_menu(self):
      for widget in self.root.winfo_children():
          widget.destroy()

      tk.Label(self.root, text=f"Velkommen, {self.player_name}!", font=("Helvetica", 20, "bold"), bg="#b0bec5").pack(pady=20)
      tk.Label(self.root, text="Velg en kategori:", font=("Helvetica", 16), bg="#b0bec5").pack(pady=20)

      for category in self.categories:
          self.create_category_button(category)

      tk.Button(self.root, text="Alle kategorier", command=self.use_all_categories, height=2, width=20,
                font=("Helvetica", 14, "bold"), bg="#78909c").pack(pady=10)
      tk.Button(self.root, text="Tilbakestill progresjon", command=self.reset_progress, font=("Helvetica", 12), bg="#78909c").pack(pady=10)
      player_menu_button = tk.Button(self.root, text="Spiller meny", command=self.load_player_menu, font=("Helvetica", 12), bg="#78909c")
      player_menu_button.place(x=1100, y=850)

  def create_category_button(self, category):
      frame = tk.Frame(self.root, bg="#b0bec5")
      frame.pack(pady=10)
      button = tk.Button(frame, text=category, command=lambda c=category: self.use_category(c), 
                         height=2, width=20, font=("Helvetica", 14, "bold"), 
                         bg=self.category_colors[category])
      button.pack(side=tk.LEFT)

      correct = self.category_stats.get(category, 0)
      total = self.total_images.get(category, 1)
      percentage = (correct / total) * 100 if total > 0 else 0

      progress_bar = ttk.Progressbar(frame, length=100, mode='determinate')
      progress_bar['value'] = percentage
      progress_bar.pack(side=tk.LEFT, padx=10)

      percentage_label = tk.Label(frame, text=f"Du kan {percentage:.1f}% av tegnene", font=("Helvetica", 12),
                                  bg="#b0bec5")
      percentage_label.pack(side=tk.LEFT, padx=10)

  def use_category(self, category):
      self.current_category = category
      self.load_images_from_folder(category)
      self.start_quiz()

  def use_all_categories(self):
      self.current_category = "Alle kategorier"
      all_images = []
      self.image_to_answer = {}
      for category in self.categories:
          images = self.load_images_from_folder(category, add_to_pool=False)
          all_images.extend([(img, category) for img in images])
          for img in images:
              self.image_to_answer[img] = os.path.splitext(img)[0]
      self.image_pool = random.sample(all_images, len(all_images))
      self.total_questions = len(self.image_pool)
      self.answered_questions = 0
      self.start_quiz()

  def load_images_from_folder(self, category, add_to_pool=True):
      folder_path = os.path.join(self.base_folder, category)
      images = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
      if add_to_pool:
          image_to_answer = {img: os.path.splitext(img)[0] for img in images}
          self.image_to_answer = image_to_answer
          self.image_pool = random.sample(images, len(images))
          self.total_questions = len(images)
          self.answered_questions = 0
      return images

  def start_quiz(self):
      for widget in self.root.winfo_children():
          widget.destroy()

      tk.Label(self.root, text=f"Kategori: {self.current_category}", font=("Helvetica", 20, "bold"), bg="#b0bec5").pack(pady=10)
      back_button = tk.Button(self.root, text="Tilbake", command=self.show_start_menu, font=("Helvetica", 14), bg="#78909c")
      back_button.pack(pady=5)

      self.feedback_label = tk.Label(self.root, text="", font=("Helvetica", 14), bg="#b0bec5")
      self.feedback_label.pack(pady=10)

      self.image_label = tk.Label(self.root, bg="#b0bec5")
      self.image_label.pack(pady=20)

      self.entry = tk.Entry(self.root, font=("Helvetica", 18), width=30)
      self.entry.pack(pady=10)
      self.entry.focus_set()

      self.submit_button = tk.Button(self.root, text="Submit", command=self.check_answer, height=2, width=10,
                                     font=("Helvetica", 14, "bold"), bg="#78909c")
      self.submit_button.pack(pady=10)

      self.score_label = tk.Label(self.root, text=f"Score: {self.score}", font=("Helvetica", 14), bg="#b0bec5")
      self.score_label.pack()

      self.streak_label = tk.Label(self.root, text=f"Streak: {self.streak}", font=("Helvetica", 14), bg="#b0bec5")
      self.streak_label.pack()

      self.high_score_label = tk.Label(self.root, text=f"High Score: {self.high_score}", font=("Helvetica", 14), bg="#b0bec5")
      self.high_score_label.pack()

      progress_percentage = (self.answered_questions / self.total_questions) * 100 if self.total_questions > 0 else 0
      self.progress_label = tk.Label(self.root, text=f"Progresjon: {progress_percentage:.1f}% ({self.answered_questions}/{self.total_questions})",
                                     font=("Helvetica", 14), bg="#b0bec5")
      self.progress_label.pack()

      self.root.bind('<Return>', self.enter_key_pressed)
      self.root.bind('<Button-1>', self.handle_click)

      self.hint_frame = None
      self.load_new_image()

  def load_new_image(self):
      if not self.image_pool:
          self.show_end_screen()
          return

      if self.hint_frame:
          self.hint_frame.destroy()

      if self.current_category == "Alle kategorier":
          self.current_image, self.current_image_category = self.image_pool.pop()
      else:
          self.current_image = self.image_pool.pop()
          self.current_image_category = self.current_category

      self.correct_answer = self.image_to_answer.get(self.current_image, "Ingen svar funnet")

      img_path = resource_path(os.path.join(self.base_folder, self.current_image_category, self.current_image))
      img = Image.open(img_path)
      img = img.resize((400, 400), Image.LANCZOS)
      img = ImageTk.PhotoImage(img)
      self.image_label.configure(image=img)
      self.image_label.image = img
      self.hint_used = False

  def enter_key_pressed(self, event):
      self.check_answer()

  def check_answer(self):
      user_input = self.entry.get().strip().lower()
      self.answered_questions += 1

      if user_input == self.correct_answer.lower():
          self.score += 1
          self.streak += 1
          self.category_stats[self.current_image_category] += 1
          if self.score > self.high_score:
              self.high_score = self.score
          self.feedback_label.config(text="Riktig svar!", fg="#66bb6a")
          self.entry.delete(0, tk.END)
          self.update_labels()
          self.save_progress()
          self.adjust_difficulty()
          self.load_new_image()
      else:
          self.feedback_label.config(text="Feil svar! Prøv igjen eller få et hint.", fg="#e57373")
          self.show_hint_options()

  def adjust_difficulty(self):
      if self.streak > 5:
          self.current_difficulty = "hard"
      elif self.streak > 2:
          self.current_difficulty = "medium"
      else:
          self.current_difficulty = "easy"

  def give_hint(self):
      if self.current_difficulty == "easy":
          hint_text = self.correct_answer[:3] + "..."
      elif self.current_difficulty == "medium":
          hint_text = self.correct_answer[:2] + "..."
      else:
          hint_text = self.correct_answer[0] + "..."

      self.feedback_label.config(text=f"Hint: {hint_text}", fg="#fafafa")
      self.hint_used = True

  def show_hint_options(self):
      if self.hint_frame:
          self.hint_frame.destroy()

      self.hint_frame = tk.Frame(self.root, bg="#b0bec5")
      self.hint_frame.pack(pady=10)

      hint_button = tk.Button(self.hint_frame, text="Ta et hint", font=("Helvetica", 12), bg="#78909c",
                              command=lambda: [self.give_hint()])
      hint_button.pack(side=tk.LEFT, padx=5)

      retry_button = tk.Button(self.hint_frame, text="Prøv igjen uten hint", font=("Helvetica", 12), bg="#78909c",
                               command=lambda: self.hint_frame.destroy())
      retry_button.pack(side=tk.LEFT, padx=5)

      skip_button = tk.Button(self.hint_frame, text="Gå videre", font=("Helvetica", 12), bg="#78909c",
                              command=lambda: [self.entry.delete(0, tk.END), self.load_new_image(), self.hint_frame.destroy()])
      skip_button.pack(side=tk.LEFT, padx=5)

  def update_labels(self):
      self.score_label.config(text=f"Score: {self.score}")
      
      if self.streak >= 5:
          streak_emoji = "🔥" * (self.streak // 5)
          self.streak_label.config(text=f"Streak: {self.streak} {streak_emoji}")
      else:
          self.streak_label.config(text=f"Streak: {self.streak}")
      
      self.high_score_label.config(text=f"High Score: {self.high_score}")
      progress_percentage = (self.answered_questions / self.total_questions) * 100 if self.total_questions > 0 else 0
      self.progress_label.config(text=f"Progresjon: {progress_percentage:.1f}% ({self.answered_questions}/{self.total_questions})")

  def show_end_screen(self):
      for widget in self.root.winfo_children():
          widget.destroy()

      tk.Label(self.root, text=f"Gratulerer! Du har fullført {self.current_category}.", font=("Helvetica", 20, "bold"),
               bg="#b0bec5").pack(pady=20)
      tk.Button(self.root, text="Tilbake til hovedmeny", command=self.show_start_menu, height=2, width=20,
                font=("Helvetica", 14, "bold"), bg="#78909c").pack(pady=10)

  def handle_click(self, event):
      if event.widget != self.entry:
          self.root.focus()

# Set up the main window and game
root = tk.Tk()
base_folder = resource_path("Kategorier")  # Use the "Kategorier" folder as the base

game = SignGame(root, base_folder)
root.mainloop()