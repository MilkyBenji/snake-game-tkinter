import tkinter as tk
from random import randint
from PIL import Image, ImageTk
from tkinter import font
import pygame

pygame.mixer.init()

# Path to the audio file
AUDIO_PATH = r"C:\Users\Evgen\OneDrive\Desktop\MySnakeGame\assets\Audio\8-bit-heaven-starting-audio.mp3"

def play_intro_audio():
    """Plays the intro audio when the game starts."""
    pygame.mixer.music.load(AUDIO_PATH)
    pygame.mixer.music.play(-1)  # Loop indefinitely until stopped

def stop_audio():
    """Stops any currently playing audio."""
    pygame.mixer.music.stop()

MOVE_INCREMENT = 20  # pixels

# Global variables to hold our game board and start menu frame.
board = None
start_frame = None

# --- Main Application Setup ---
root = tk.Tk()
root.title("Snake")
root.resizable(False, False)
root.tk.call("tk", "scaling", 2.0)
root.configure(bg="black")            # Root background is black

# Play the intro music when the app starts
play_intro_audio()

# --- 1) Create a header frame for the logo at the top ---
header_frame = tk.Frame(root, bg="black")
header_frame.pack(side="top", fill="x")

try:
    # Load your logo
    logo_image = Image.open("./assets/logo.png")
    # Optionally resize if needed, e.g.:
    # logo_image = logo_image.resize((400, 100))
    logo_photo = ImageTk.PhotoImage(logo_image)
except IOError:
    logo_photo = None

if logo_photo:
    logo_label = tk.Label(header_frame, image=logo_photo, bg="black")
    logo_label.pack(pady=5)
    # Keep a reference to avoid garbage-collection
    header_frame.logo_photo = logo_photo


# --- Define global fonts after the root window is created ---
try:
    jacquard_font_small = font.Font(root, family="Jacquard 12", size=12)
    jacquard_font_medium = font.Font(root, family="Jacquard 12", size=18)
    jacquard_font_large = font.Font(root, family="Jacquard 12", size=24)
except Exception:
    jacquard_font_small = font.Font(root, family="Arial", size=12)
    jacquard_font_medium = font.Font(root, family="Arial", size=18)
    jacquard_font_large = font.Font(root, family="Arial", size=24)



class Snake(tk.Canvas):
    def __init__(self, parent, moves_per_second=15):
        self.moves_per_second = moves_per_second
        self.GAME_SPEED = 1000 // self.moves_per_second  # milliseconds between moves
        
        super().__init__(parent, width=610, height=620, background="black", 
                        highlightthickness=0, highlightbackground="black")
        
        self.snake_positions = [(100, 100), (80, 100), (60, 100)]
        self.food_position = self.set_new_food_position()  # This was causing an error
        self.direction = "Right"
        self.score = 0

        self.load_assets()
        self.create_objects()

        self.bind_all("<Key>", self.on_key_press)
        self.pack()

        self.game_loop_id = None
        self.start_game_loop()

    def set_new_food_position(self): 
        while True:
            x_position = randint(1, 29) * MOVE_INCREMENT
            y_position = randint(3, 30) * MOVE_INCREMENT
            food_position = (x_position, y_position)
            if food_position not in self.snake_positions:
                return food_position

    def start_game_loop(self):
        if self.game_loop_id is not None:
            self.after_cancel(self.game_loop_id)
        self.game_loop_id = self.after(self.GAME_SPEED, self.perform_actions)

    def load_assets(self):
        try:
            self.snake_body_image = Image.open("./assets/snake.png")
            self.snake_body = ImageTk.PhotoImage(self.snake_body_image)

            self.food_image = Image.open("./assets/food.png")
            self.food = ImageTk.PhotoImage(self.food_image)

            
            # Load movement sound effect
            self.move_sound = pygame.mixer.Sound(r"C:\Users\Evgen\OneDrive\Desktop\MySnakeGame\assets\Audio\gameboy-pluck-button.MP3")
        
        except IOError as error:
            root.destroy()
            raise

    def create_objects(self):
        # Use jacquard_font_small for score text
        self.create_text(35, 12, text=f"Score: {self.score}", tag="score", fill="#fff", font=jacquard_font_small)
        for x_position, y_position in self.snake_positions:
            self.create_image(x_position, y_position, image=self.snake_body, tag="snake")
        self.create_image(*self.food_position, image=self.food, tag="food")
        self.create_rectangle(7, 27, 593, 613, outline="#525d69")

    def check_collisions(self):
        head_x_position, head_y_position = self.snake_positions[0]
        return (
            head_x_position in (0, 600)
            or head_y_position in (20, 620)
            or (head_x_position, head_y_position) in self.snake_positions[1:]
        )

    def check_food_collision(self):
        if self.snake_positions[0] == self.food_position:
            self.score += 1
            self.snake_positions.append(self.snake_positions[-1])
            self.create_image(*self.snake_positions[-1], image=self.snake_body, tag="snake")
            self.food_position = self.set_new_food_position()
            self.coords(self.find_withtag("food"), *self.food_position)
            score = self.find_withtag("score")
            self.itemconfigure(score, text=f"Score: {self.score}", tag="score")

    def end_game(self):
        if self.game_loop_id is not None:
            self.after_cancel(self.game_loop_id)
            self.game_loop_id = None

        self.delete(tk.ALL)

        # 1) Multi-line text with blank lines for spacing
        text_str = (
            f"Game over! You scored {self.score}!\n\n"
            "Press Enter to try again\n"
            "Press ESC for menu"
        )

        # 2) Create the text (no spacing1 or spacing3)
        text_id = self.create_text(
            self.winfo_width() / 2,
            self.winfo_height() / 2,
            text=text_str,
            fill="#fff",
            font=jacquard_font_small,
            anchor="center",
            justify="center",
            width=500  # wrap at 500px
        )

        # 3) Get bounding box and draw rectangle with margin
        x1, y1, x2, y2 = self.bbox(text_id)
        margin = 20
        rect_id = self.create_rectangle(
            x1 - margin, y1 - margin,
            x2 + margin, y2 + margin,
            fill="black",
            outline="white",
            width=2
        )
        self.tag_raise(text_id, rect_id)

        # 4) Bind keys
        self.bind_all("<Return>", self.reset_game)
        self.bind_all("<Escape>", back_to_menu)
        
    def reset_game(self, event=None):
        if self.game_loop_id is not None:
            self.after_cancel(self.game_loop_id)
            self.game_loop_id = None
        self.snake_positions = [(100, 100), (80, 100), (60, 100)]
        self.food_position = self.set_new_food_position()
        self.direction = "Right"
        self.score = 0
        self.delete(tk.ALL)
        self.create_objects()
        self.start_game_loop()

    def move_snake(self):
        head_x_position, head_y_position = self.snake_positions[0]
        if self.direction == "Left":
            new_head_position = (head_x_position - MOVE_INCREMENT, head_y_position)
        elif self.direction == "Right":
            new_head_position = (head_x_position + MOVE_INCREMENT, head_y_position)
        elif self.direction == "Down":
            new_head_position = (head_x_position, head_y_position + MOVE_INCREMENT)
        elif self.direction == "Up":
            new_head_position = (head_x_position, head_y_position - MOVE_INCREMENT)
        self.snake_positions = [new_head_position] + self.snake_positions[:-1]
        for segment, position in zip(self.find_withtag("snake"), self.snake_positions):
            self.coords(segment, position)

    def on_key_press(self, e):
        new_direction = e.keysym
        all_directions = ("Up", "Down", "Left", "Right")
        opposites = ({"Up", "Down"}, {"Left", "Right"})

        if new_direction in all_directions and {new_direction, self.direction} not in opposites:

            self.direction = new_direction
        self.move_sound.play()  # Play movement sound



    def perform_actions(self):
        self.move_snake()              # Move snake first
        if self.check_collisions():      # Then check for collisions immediately
            self.end_game()
            return
        self.check_food_collision()     # Then check for food collision
        self.game_loop_id = self.after(self.GAME_SPEED, self.perform_actions)


def create_start_menu():
    """Creates the start screen where the user can choose a difficulty."""
    global start_frame
    start_frame = tk.Frame(root, bg="black")
    start_frame.pack(fill="both", expand=True)
    
    difficulty_label = tk.Label(start_frame, text="Choose Difficulty", font=jacquard_font_large, fg="white", bg="black")
    difficulty_label.pack(pady=20)
    
    difficulty_var = tk.StringVar(value="15")  # Default difficulty
    
    difficulties = {"Easy": "15", "Fast": "20", "Fastest": "30"}
    for text, value in difficulties.items():
        rb = tk.Radiobutton(start_frame, text=text, variable=difficulty_var, value=value,
                            font=jacquard_font_medium, fg="white", bg="black", selectcolor="grey")
        rb.pack(pady=5)

    
    start_button = tk.Button(start_frame, text="Start Game", font=jacquard_font_medium,
                            command=lambda: start_game(int(difficulty_var.get())))
    start_button.pack(pady=20)

def start_game(chosen_difficulty):
    """Destroys the start menu, stops the intro music, and starts the game with the chosen difficulty."""
    global start_frame, board
    stop_audio()  # Stop the intro music
    start_frame.destroy()
    board = Snake(root, moves_per_second=chosen_difficulty)
    board.pack()

def back_to_menu(event=None):
    """Destroys the game board and returns to the start menu."""
    global board
    if board:
        board.destroy()
        board = None
    play_intro_audio()  # Restart the intro music
    create_start_menu()


create_start_menu()
root.mainloop()