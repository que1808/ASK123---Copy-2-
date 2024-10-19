import tkinter as tk
from tkinter import messagebox, ttk
import random
import os
import sys
import json
from PIL import Image, ImageTk
import logging

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SignGame:
    def __init__(self, root, base_folder):
        logging.info("Initialiserer SignGame...")
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

        self.image_cache = {}  # Optimalisert bildehåndtering
        self.images_used = set()  # Holder styr på brukte bilder

        self.button_bg_color = "#78909c"
        self.label_font = ("Helvetica", 14)
        
        self.max_attempts = 3  # Maximum number of incorrect attempts before a hint is given
        self.attempts = 0  # Counter for incorrect attempts

        self.correct_answer = ""  # Initialiser correct_answer for å unngå AttributeError
        self.image_pool = []  # Initialiser image_pool for å unngå AttributeError

        self.show_welcome_screen()

    def clear_window(self):
        """ Helper function to clear all widgets from the root window. """
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_welcome_screen(self):
        self.clear_window()
        tk.Label(self.root, text="Velkommen til ASK123", font=("Helvetica", 36, "bold"), bg="#b0bec5").pack(pady=20)

        explanation_text = (
            "ASK (Alternativ og Supplerende Kommunikasjon) er tegn til tale som hjelper barn å kommunisere mer effektivt.\n\n"
            "Alle barn kan dra nytte av ASK fordi det:\n"
            "• Støtter språkutvikling\n"
            "• Forbedrer kommunikasjonsevner\n"
            "• Øker forståelse og uttrykksevne"
        )
        tk.Label(self.root, text=explanation_text, font=("Helvetica", 12), bg="#b0bec5", justify=tk.LEFT).pack(pady=20)

        # Viser "Månedens Tegn" bilder på startskjermen
        self.show_monthly_signs()

        tk.Button(self.root, text="Start spillet", command=self.load_player_menu,
                  font=self.label_font, bg=self.button_bg_color).pack(pady=20)

    def show_monthly_signs(self):
        monthly_signs_folder = os.path.join(self.base_folder, 'manedens_tegn')
        images = self.load_images_for_month(monthly_signs_folder)

        if images:
            tk.Label(self.root, text="Månedens Tegn", font=("Helvetica", 24, "bold"), bg="#b0bec5").pack(pady=10)
            images_frame = tk.Frame(self.root, bg="#b0bec5")
            images_frame.pack(pady=10)

            for i, image_path in enumerate(images[:4]):  
                if image_path not in self.image_cache:
                    img = Image.open(image_path)
                    img = img.resize((200, 200), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.image_cache[image_path] = photo

                label = tk.Label(images_frame, image=self.image_cache[image_path], bg="#b0bec5")
                label.grid(row=0, column=i, padx=10, pady=10)

    def load_images_for_month(self, folder_path):
        """Henter fire bilder fra en kategori eller fra flere kategorier"""
        if os.path.exists(folder_path):
            images = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            return images[:4]
        return []

    def load_player_menu(self):
        self.clear_window()
        tk.Label(self.root, text="Velkommen! Velg eller opprett en profil:", font=("Helvetica", 20, "bold"), bg="#b0bec5").pack(pady=20)

        player_files = [f.replace(".json", "") for f in os.listdir(self.players_dir) if f.endswith(".json")]
        if player_files:
            tk.Label(self.root, text="Eksisterende spillere:", font=("Helvetica", 14), bg="#b0bec5").pack(pady=10)
            for player in player_files:
                frame = tk.Frame(self.root, bg="#b0bec5")
                frame.pack(pady=5)
                tk.Button(frame, text=player, font=self.label_font, bg=self.button_bg_color,
                          command=lambda p=player: self.select_player(p)).pack(side=tk.LEFT)
                tk.Button(frame, text="Slett", font=self.label_font, bg="#e57373",
                          command=lambda p=player: self.delete_player(p)).pack(side=tk.LEFT, padx=10)

        tk.Label(self.root, text="Opprett ny spiller:", font=self.label_font, bg="#b0bec5").pack(pady=20)
        self.new_player_entry = tk.Entry(self.root, font=self.label_font)
        self.new_player_entry.pack(pady=10)
        tk.Button(self.root, text="Opprett spiller", font=self.label_font, bg=self.button_bg_color, command=self.create_player).pack(pady=10)

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
        else:
            messagebox.showwarning("Advarsel", "Spillernavnet kan ikke være tomt. Vennligst skriv inn et navn.")

    def delete_player(self, player_name):
        try:
            response = messagebox.askyesno("Bekreftelse", f"Er du sikker på at du vil slette spilleren {player_name}?")
            if response:
                player_file = os.path.join(self.players_dir, f"{player_name}.json")
                if os.path.exists(player_file):
                    os.remove(player_file)
                    logging.info(f"Player {player_name} deleted successfully.")
                    messagebox.showinfo("Slettet", f"Spilleren {player_name} er slettet.")
                    self.load_player_menu()
                else:
                    raise FileNotFoundError(f"Spilleren {player_name} finnes ikke.")
        except Exception as e:
            logging.error(f"Error while deleting player {player_name}: {e}")
            messagebox.showerror("Feil", str(e))

    def reset_progress(self):
        response = messagebox.askyesno("Bekreftelse", "Er du sikker på at du vil tilbakestille progresjonen din?")
        if response and self.player_name:
            self.backup_progress()  # Backup progress before resetting
            self.score = 0
            self.streak = 0
            self.high_score = 0
            self.category_stats = {category: 0 for category in self.categories}
            self.save_progress()
            messagebox.showinfo("Tilbakestill", f"Progresjonen til {self.player_name} er tilbakestilt.")

    def backup_progress(self):
        if self.player_name:
            player_file = os.path.join(self.players_dir, f"{self.player_name}.json")
            backup_file = os.path.join(self.players_dir, f"{self.player_name}_backup.json")
            try:
                if os.path.exists(player_file):
                    with open(player_file, "r") as f:
                        progress_data = json.load(f)
                    with open(backup_file, "w") as f:
                        json.dump(progress_data, f)
                    logging.info(f"Backup fullført for spiller {self.player_name}.")
            except Exception as e:
                logging.error(f"Feil under sikkerhetskopiering av progresjon: {e}")

    def select_player(self, player_name):
        self.player_name = player_name
        if not self.load_progress():
            messagebox.showerror("Feil", "Kunne ikke laste spilleren. Prøv igjen.")
            return
        self.load_categories()
        self.load_category_stats()
        self.show_start_menu()

    def load_progress(self):
        logging.info(f"Laster spillerdata for {self.player_name}...")
        if self.player_name:
            player_file = os.path.join(self.players_dir, f"{self.player_name}.json")
            if os.path.exists(player_file):
                try:
                    with open(player_file, "r") as f:
                        progress_data = json.load(f)
                        missing_data = []
                        self.category_stats = progress_data.get("category_stats", {})
                        if not self.category_stats:
                            missing_data.append("category_stats")
                        self.score = progress_data.get("score", 0)
                        self.streak = progress_data.get("streak", 0)
                        self.high_score = progress_data.get("high_score", 0)

                        if missing_data:
                            logging.warning(f"Følgende data mangler i spillerfilen: {', '.join(missing_data)}")
                            messagebox.showwarning("Manglende data", f"Følgende data mangler i spillerfilen: {', '.join(missing_data)}")
                    logging.info("Spillerdata lastet inn.")
                    return True
                except json.JSONDecodeError:
                    logging.error(f"Feil under lasting av spillerdata: Filen inneholder ugyldig JSON-format.")
                    messagebox.showerror("Feil", "Kunne ikke laste spillerdata: Ugyldig JSON-format.")
                    return False
                except Exception as e:
                    logging.error(f"Feil under lasting av spillerdata: {e}")
                    messagebox.showerror("Feil", str(e))
                    return False
            else:
                logging.warning(f"Spillerfilen for {self.player_name} finnes ikke.")
        else:
            logging.warning("Ingen spiller valgt.")
        return False

    def save_progress(self):
        if self.player_name:
            player_file = os.path.join(self.players_dir, f"{self.player_name}.json")
            progress_data = {
                "category_stats": self.category_stats,
                "score": self.score,
                "streak": self.streak,
                "high_score": self.high_score
            }
            try:
                with open(player_file, "w") as f:
                    json.dump(progress_data, f)
                logging.info(f"Progresjon lagret for spiller {self.player_name}.")
            except Exception as e:
                logging.error(f"Feil under lagring av progresjon: {e}")

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
            images = [f for f in os.listdir(category_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.total_images[category] = len(images)

    def show_start_menu(self):
        self.streak = 0
        self.clear_window()

        tk.Label(self.root, text=f"Velkommen, {self.player_name}!", font=("Helvetica", 20, "bold"), bg="#b0bec5").pack(pady=20)
        tk.Label(self.root, text="Velg en kategori:", font=("Helvetica", 16), bg="#b0bec5").pack(pady=20)

        for category in self.categories:
            self.create_category_button(category)

        tk.Button(self.root, text="Alle kategorier", command=self.use_all_categories, height=2, width=20,
                  font=("Helvetica", 14, "bold"), bg=self.button_bg_color).pack(pady=10)
        tk.Button(self.root, text="Tilbakestill progresjon", command=self.reset_progress, font=self.label_font, bg=self.button_bg_color).pack(pady=10)
        player_menu_button = tk.Button(self.root, text="Spiller meny", command=self.load_player_menu, font=self.label_font, bg=self.button_bg_color)
        player_menu_button.place(x=1100, y=850)

        # Flerspiller-knapp
        tk.Button(self.root, text="Flerspiller modus", command=self.multiplayer_mode, height=2, width=20,
                  font=("Helvetica", 14, "bold"), bg=self.button_bg_color).pack(pady=10)

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
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if add_to_pool:
            image_to_answer = {img: os.path.splitext(img)[0] for img in images}
            self.image_to_answer = image_to_answer
            self.image_pool = random.sample(images, len(images))
            self.total_questions = len(images)
            self.answered_questions = 0
        return images

    def start_quiz(self):
        logging.info("Starting quiz...")

        self.streak = 0  

        self.clear_window()

        tk.Label(self.root, text=f"Kategori: {self.current_category}", font=("Helvetica", 20, "bold"), bg="#b0bec5").pack(pady=10)
        back_button = tk.Button(self.root, text="Tilbake", command=self.show_start_menu, font=self.label_font, bg=self.button_bg_color)
        back_button.pack(pady=5)

        self.feedback_label = tk.Label(self.root, text="", font=self.label_font, bg="#b0bec5")
        self.feedback_label.pack(pady=10)

        self.image_label = tk.Label(self.root, bg="#b0bec5")
        self.image_label.pack(pady=20)

        self.entry_text = tk.StringVar()  
        self.entry = tk.Entry(self.root, font=("Helvetica", 18), width=30, textvariable=self.entry_text)
        self.entry.pack(pady=10)
        self.entry.focus_set()

        self.submit_button = tk.Button(self.root, text="Submit", command=self.check_answer, height=2, width=10,
                                       font=("Helvetica", 14, "bold"), bg=self.button_bg_color)
        self.submit_button.pack(pady=10)

        self.score_label = tk.Label(self.root, text=f"Score: {self.score}", font=self.label_font, bg="#b0bec5")
        self.score_label.pack(pady=5)

        self.streak_label = tk.Label(self.root, text=f"Streak: {self.streak}", font=self.label_font, bg="#b0bec5")
        self.streak_label.pack(pady=5)

        self.high_score_label = tk.Label(self.root, text=f"High Score: {self.high_score}", font=self.label_font, bg="#b0bec5")
        self.high_score_label.pack(pady=5)

        progress_percentage = (self.answered_questions / self.total_questions) * 100 if self.total_questions > 0 else 0
        self.progress_label = tk.Label(self.root, text=f"Progresjon: {progress_percentage:.1f}% ({self.answered_questions}/{self.total_questions})",
                                       font=self.label_font, bg="#b0bec5")
        self.progress_label.pack()

        self.root.bind('<Return>', self.enter_key_pressed)
        self.root.bind('<Button-1>', self.handle_click)

        self.hint_frame = None
        self.load_new_image()

    def check_answer(self):
        user_input = self.entry_text.get().strip().lower()
        self.answered_questions += 1

        if user_input == self.correct_answer.lower():
            self.score += self.get_score_increment()  
            self.streak += 1  
            self.category_stats[self.current_image_category] += 1
            if self.score > self.high_score:
                self.high_score = self.score
            self.feedback_label.config(text="Riktig svar!", fg="#66bb6a")
            self.entry_text.set("")  
            self.update_labels()
            self.save_progress()
            self.adjust_difficulty()
            self.load_new_image()
        else:
            self.feedback_label.config(text="Feil svar! Prøv igjen eller få et hint.", fg="#e57373")
            self.streak = 0  
            if self.score > self.high_score:
                self.high_score = self.score
            self.score = 0  # Reset score on incorrect answer
            self.update_labels()
            self.show_hint_options()

    def get_score_increment(self):
        """ Determine score increment based on difficulty """
        if self.current_difficulty == "easy":
            return 1
        elif self.current_difficulty == "medium":
            return 2
        else:
            return 3

    def adjust_difficulty(self):
        if self.streak > 5:
            self.current_difficulty = "hard"
        elif self.streak > 2:
            self.current_difficulty = "medium"
        else:
            self.current_difficulty = "easy"

    def update_labels(self):
        self.score_label.config(text=f"Score: {self.score}")
        self.streak_label.config(text=f"Streak: {self.streak}")
        self.high_score_label.config(text=f"High Score: {self.high_score}")

        progress_percentage = (self.answered_questions / self.total_questions) * 100 if self.total_questions > 0 else 0
        self.progress_label.config(text=f"Progresjon: {progress_percentage:.1f}% ({self.answered_questions}/{self.total_questions})")

    def show_hint_options(self):
        if self.hint_frame:
            self.hint_frame.destroy()

        self.hint_frame = tk.Frame(self.root, bg="#b0bec5")
        self.hint_frame.pack(pady=10)

        hint_button = tk.Button(self.hint_frame, text="Ta et hint", font=self.label_font, bg=self.button_bg_color,
                                command=lambda: [self.give_hint()])
        hint_button.pack(side=tk.LEFT, padx=5)

        retry_button = tk.Button(self.hint_frame, text="Prøv igjen uten hint", font=self.label_font, bg=self.button_bg_color,
                                 command=lambda: self.hint_frame.destroy())
        retry_button.pack(side=tk.LEFT, padx=5)

        skip_button = tk.Button(self.hint_frame, text="Gå videre", font=self.label_font, bg=self.button_bg_color,
                                command=lambda: [self.entry_text.set(""), self.load_new_image(), self.hint_frame.destroy()])
        skip_button.pack(side=tk.LEFT, padx=5)

    def give_hint(self):
        if self.current_difficulty == "easy":
            hint_text = self.correct_answer[:3] + "..."
        elif self.current_difficulty == "medium":
            hint_text = self.correct_answer[:2] + "..."
        else:
            hint_text = self.correct_answer[0] + "..."

        self.feedback_label.config(text=f"Hint: {hint_text}", fg="#fafafa")
        self.hint_used = True

    def load_new_image(self):
        if not self.image_pool:
            self.show_end_screen()
            return

        if self.hint_frame:
            self.hint_frame.destroy()

        if self.current_category == "Alle kategorier":
            self.current_image, self.current_image_category = self.get_unique_image()
        else:
            self.current_image = self.get_unique_image_from_category()
            self.current_image_category = self.current_category

        self.correct_answer = self.image_to_answer.get(self.current_image, "Ingen svar funnet")

        img_path = resource_path(os.path.join(self.base_folder, self.current_image_category, self.current_image))

        if img_path not in self.image_cache:
            img = Image.open(img_path)
            img = img.resize((400, 400), Image.Resampling.LANCZOS)
            self.image_cache[img_path] = ImageTk.PhotoImage(img)

        self.image_label.configure(image=self.image_cache[img_path])
        self.image_label.image = self.image_cache[img_path]
        self.hint_used = False

    def get_unique_image(self):
        """ Get an image that has not been used yet, ensuring all images are used before repetition. """
        remaining_images = [img for img in self.image_pool if img not in self.images_used]
        if not remaining_images:
            self.images_used.clear()  # Reset after all images have been used
            remaining_images = self.image_pool
        selected_image = random.choice(remaining_images)
        self.images_used.add(selected_image)
        return selected_image

    def get_unique_image_from_category(self):
        """ Get an image from the current category that has not been used yet. """
        remaining_images = [img for img in self.image_pool if img not in self.images_used]
        if not remaining_images:
            self.images_used.clear()  # Reset after all images have been used
            remaining_images = self.image_pool
        selected_image = random.choice(remaining_images)
        self.images_used.add(selected_image)
        return selected_image

    def enter_key_pressed(self, event):
        self.check_answer()

    def handle_click(self, event):
        if event.widget != self.entry:
            self.root.focus()

    def show_end_screen(self):
        self.clear_window()

        if hasattr(self, 'multiplayer_scores'):
            winner = 1 if self.multiplayer_scores[0] > self.multiplayer_scores[1] else 2
            tk.Label(self.root, text=f"Gratulerer! Spiller {winner} vant!", font=("Helvetica", 20, "bold"), bg="#b0bec5").pack(pady=20)
        else:
            tk.Label(self.root, text=f"Gratulerer! Du har fullført {self.current_category}.", font=("Helvetica", 20, "bold"), bg="#b0bec5").pack(pady=20)

        tk.Button(self.root, text="Tilbake til hovedmeny", command=self.show_start_menu, height=2, width=20,
                  font=("Helvetica", 14, "bold"), bg=self.button_bg_color).pack(pady=10)
        tk.Button(self.root, text="Avslutt spillet", command=self.show_welcome_screen, height=2, width=20,
                  font=("Helvetica", 14, "bold"), bg=self.button_bg_color).pack(pady=10)

    def multiplayer_mode(self):
        """Set up multiplayer mode where two players can compete."""
        self.clear_window()

        tk.Label(self.root, text="Flerspiller modus", font=("Helvetica", 24, "bold"), bg="#b0bec5").pack(pady=20)
        tk.Label(self.root, text="Velg modus for to spillere.", font=("Helvetica", 16), bg="#b0bec5").pack(pady=10)

        # Option to start a multiplayer game
        tk.Button(self.root, text="Start flerspiller", command=self.start_multiplayer_game, height=2, width=20,
                  font=("Helvetica", 14, "bold"), bg=self.button_bg_color).pack(pady=10)

        # Back to main menu
        tk.Button(self.root, text="Tilbake", command=self.show_start_menu, height=2, width=20,
                  font=("Helvetica", 14, "bold"), bg=self.button_bg_color).pack(pady=10)

    def start_multiplayer_game(self):
        """Initialize a multiplayer quiz session."""
        self.clear_window()
        self.multiplayer_scores = [0, 0]
        self.current_player = 0

        tk.Label(self.root, text="Flerspiller quiz", font=("Helvetica", 20, "bold"), bg="#b0bec5").pack(pady=20)
        self.feedback_label = tk.Label(self.root, text=f"Spiller {self.current_player + 1} sin tur", font=("Helvetica", 16), bg="#b0bec5")
        self.feedback_label.pack(pady=10)

        self.image_label = tk.Label(self.root, bg="#b0bec5")
        self.image_label.pack(pady=20)

        self.entry_text = tk.StringVar()  
        self.entry = tk.Entry(self.root, font=("Helvetica", 18), width=30, textvariable=self.entry_text)
        self.entry.pack(pady=10)
        self.entry.focus_set()

        self.submit_button = tk.Button(self.root, text="Submit", command=self.check_multiplayer_answer, height=2, width=10,
                                       font=("Helvetica", 14, "bold"), bg=self.button_bg_color)
        self.submit_button.pack(pady=10)

        self.load_new_image()

    def check_multiplayer_answer(self):
        user_input = self.entry_text.get().strip().lower()

        if user_input == self.correct_answer.lower():
            self.multiplayer_scores[self.current_player] += 1
            self.feedback_label.config(text=f"Spiller {self.current_player + 1} svarte riktig!", fg="#66bb6a")
        else:
            self.feedback_label.config(text=f"Spiller {self.current_player + 1} svarte feil!", fg="#e57373")

        # Switch to the next player
        self.current_player = (self.current_player + 1) % 2
        self.entry_text.set("")
        self.feedback_label.config(text=f"Spiller {self.current_player + 1} sin tur")

        # Load a new image for the next player
        self.load_new_image()

    def show_end_screen(self):
        self.clear_window()

        if hasattr(self, 'multiplayer_scores'):
            winner = 1 if self.multiplayer_scores[0] > self.multiplayer_scores[1] else 2
            tk.Label(self.root, text=f"Gratulerer! Spiller {winner} vant!", font=("Helvetica", 20, "bold"), bg="#b0bec5").pack(pady=20)
        else:
            tk.Label(self.root, text=f"Gratulerer! Du har fullført {self.current_category}.", font=("Helvetica", 20, "bold"), bg="#b0bec5").pack(pady=20)

        tk.Button(self.root, text="Tilbake til hovedmeny", command=self.show_start_menu, height=2, width=20,
                  font=("Helvetica", 14, "bold"), bg=self.button_bg_color).pack(pady=10)
        tk.Button(self.root, text="Avslutt spillet", command=self.show_welcome_screen, height=2, width=20,
                  font=("Helvetica", 14, "bold"), bg=self.button_bg_color).pack(pady=10)

# Set up the main window and game
root = tk.Tk()
logging.info("Tkinter-vindu opprettet.")
base_folder = resource_path("Kategorier")

if not os.path.exists(base_folder):
    logging.warning(f"Katalogen '{base_folder}' finnes ikke. Oppretter katalogen automatisk...")
    os.makedirs(base_folder, exist_ok=True)
logging.info("Oppretter SignGame-objekt...")
game = SignGame(root, base_folder)
logging.info("Starter hovedløkke...")
root.mainloop()