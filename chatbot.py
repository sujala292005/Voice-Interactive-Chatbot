import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
import pyttsx3
import threading
import webbrowser
import re
from nltk.chat.util import Chat, reflections
from queue import Queue

LANGUAGES = {'English': 'en'}

WEBSITE_COMMANDS = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "web whatsapp": "https://web.whatsapp.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "perplexity": "https://www.perplexity.ai",
    "netflix":"https://www.netflix.com",
    "prime video":"https://www.primrvideo.com",
    "hotstar":"https://www.hotstar.com"
}

engine = pyttsx3.init()
speech_queue = Queue()

def tts_worker():
    while True:
        text, lang_code = speech_queue.get()
        try:
            voices = engine.getProperty('voices')
            selected_voice = None
            for voice in voices:
                langs = []
                if hasattr(voice, 'languages'):
                    for l in voice.languages:
                        if isinstance(l, bytes):
                            try:
                                langs.append(l.decode('utf-8').lower())
                            except:
                                pass
                        else:
                            langs.append(str(l).lower())
                else:
                    langs = [voice.id.lower(), voice.name.lower()]
                if any(lang_code in l for l in langs):
                    selected_voice = voice.id
                    break
            engine.setProperty('voice', selected_voice if selected_voice else voices[0].id)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS error: {e}")
        speech_queue.task_done()

threading.Thread(target=tts_worker, daemon=True).start()

def speak(text, lang_code='en'):
    speech_queue.put((text, lang_code))

reflections_en = {
    "i am": "you are?", "i was": "you were?", "i": "you?", "i'm": "you are?",
    "i'd": "you would?", "i've": "you have?", "i'll": "you will?",
    "my": "your?", "you are": "I am?", "you were": "I was?",
    "you've": "I have?", "you'll": "I will?", "your": "my?",
    "yours": "mine?", "you": "me?", "me": "you?"
}

pairs_en = [
    [r"(hi|hello|hey)", ["Hello there!", "Hi!", "Hey! How can I help you?"]],
    [r"my name is (.*)", ["Nice to meet you, %1!", "Hello %1, how can I help you today?"]],
    [r"what is your name\??", ["I'm PyBot, your Python chatbot.", "You can call me PyBot!"]],
    [r"how are you\??", ["I'm just code, but I'm happy to chat!", "Doing great, thanks! How about you?"]],
    [r"(.)(help|support)(.)", ["Sure! Tell me about your issue, and I'll do my best to help.", "I'm here for support! What's up?"]],
    [r"bye|quit|exit", ["Goodbye!", "See you soon!", "Bye! Have a wonderful day!"]],
    [r"tell me about you|tell me about yourself|introduce yourself", ["Hey there! I'm the multitasker you didn’t know you needed. Ask me how I'm doing—I’ll respond. Feeling lazy? Tell me, and I’ll open Netflix. Want to challenge your brain? Let’s play the maze game. Math trouble? I’m also a calculator. You can talk or type, and I’ll reply with a smile (well, if I had a face 😄). I’m not just a chatbot—I’m your new virtual buddy!"]],
    [r"what can you do\??", [
        "I can answer questions, chat with you, tell jokes, and open websites for you!",
        "I'm here to help with questions or just to have a nice conversation."
    ]],
    [r"okay|ok|anything new", ["Do you want to do something new?"]],
    [r"tell me a joke", [
        "Why did the computer show up at work late? It had a hard drive!",
        "Why did the Python programmer go broke? Because he couldn't get any arrays!"
    ]],
    [r"who created you\??", ["I was created by a Python developer.", "I'm a Python chatbot, made for friendly chat!"]],
    [r"open (google|youtube|web whatsapp|facebook|instagram|perplexity|netflix|hotstar)", ["Sure, opening %1 for you!"]],
    [r"(.*)", [
        "I'm not sure I understand. Could you say that another way?",
        "That's interesting! Tell me more.",
        "Let's keep talking! I'm here to chat."
    ]]
]

def get_pairs_by_lang(lang_code):
    # Since only English supported, always return English pairs
    return pairs_en

class PyBotApp:
    def _init_(self, root):
        self.lang_code = 'en'
        self.chatbot = Chat(get_pairs_by_lang(self.lang_code), reflections_en)
        self.root = root
        self.waiting_for_special_option = False
        self.root.title("English Voice-Interactive Chatbot")
        self.create_widgets()
        self.bot_start_conversation()

    def create_widgets(self):
        frame_top = tk.Frame(self.root)
        frame_top.pack(pady=5)

        tk.Label(frame_top, text="Language: English").pack(side=tk.LEFT)

        self.chat_area = tk.Text(self.root, width=60, height=25, state=tk.DISABLED, bg="#F7F7F7",
                                 wrap=tk.WORD, padx=10, pady=10)
        self.chat_area.pack(padx=10, pady=10)
        self.chat_area.tag_configure('user', foreground="#222", background="#cce5ff", justify='right',
                                     lmargin1=60, lmargin2=60, rmargin=5, spacing1=8, spacing3=8)
        self.chat_area.tag_configure('bot', foreground="#333", background="#f1f0f0", justify='left',
                                     lmargin1=5, lmargin2=5, rmargin=60, spacing1=8, spacing3=8)
        self.chat_area.tag_configure('margin', spacing1=4)
        self.chat_area.tag_configure('info', foreground="#888", background="#F7F7F7", justify='center')

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=5)

        self.entry_field = tk.Entry(bottom_frame, width=55)
        self.entry_field.pack(side=tk.LEFT, padx=(10, 0))
        self.entry_field.focus()
        self.entry_field.bind('<Return>', self.send_message)

        send_button = tk.Button(bottom_frame, text="Send", width=8, command=self.send_message)
        send_button.pack(side=tk.LEFT, padx=5)

        voice_button = tk.Button(bottom_frame, text="🎤 Speak", width=8, command=self.voice_input)
        voice_button.pack(side=tk.LEFT)

    def bot_start_conversation(self):
        welcome_msg = "System online! Hello guys!!!, I’m your all-in-one chatbot—ready to chat, calculate, play, or open your favorite apps. Quick heads-up: I only talk during this welcome—after that, I’ll text you back like a pro. So go ahead, type or speak—I’m listening!"

        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete('1.0', tk.END)
        self.chat_area.insert(tk.END, "Bot: " + welcome_msg + "\n\n", "bot")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
        speak(welcome_msg, self.lang_code)

    def listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                self.chat_area.config(state=tk.NORMAL)
                self.chat_area.insert(tk.END, "(Listening...)\n", "info")
                self.chat_area.config(state=tk.DISABLED)
                self.root.update()
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio, language=self.lang_code)
                return text
            except Exception:
                return None

    def send_message(self, event=None, user_message=None):
        # If waiting for special option, handle it first and return early
        if self.waiting_for_special_option:
            if user_message is None:
                user_message = self.entry_field.get()
            self.handle_special_option(user_message.strip().lower())
            self.waiting_for_special_option = False
            self.entry_field.delete(0, tk.END)
            return

        if user_message is None:
            user_message = self.entry_field.get()
        user_message = user_message.strip()
        if user_message == "":
            return

        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, "\n", "margin")
        self.chat_area.insert(tk.END, "You: " + user_message + "\n", "user")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

        low_msg = user_message.lower()
        opened_website_flag = False

        for site in WEBSITE_COMMANDS:
            if re.search(rf"\bopen {site}\b", low_msg):
                reply = f"Opening {site} for you!"
                self.reply_and_speak(reply)
                webbrowser.open_new_tab(WEBSITE_COMMANDS[site])
                opened_website_flag = True
                break

        if opened_website_flag:
            if low_msg in ["quit", "exit", "bye"]:
                self.root.after(1000, self.root.destroy)
            self.entry_field.delete(0, tk.END)
            return

        try:
            bot_reply = self.chatbot.respond(user_message)
            if bot_reply is None:
                bot_reply = "I'm not sure I understand that."
        except Exception:
            bot_reply = "Sorry, I had some trouble processing that."

        self.reply_and_speak(bot_reply)

        if bot_reply == "Do you want to do something new?":
            self.waiting_for_special_option = True
            self.show_special_options()
            self.entry_field.delete(0, tk.END)
            return

        if low_msg in ["quit", "exit", "bye"]:
            self.root.after(1500, self.root.destroy)

        self.entry_field.delete(0, tk.END)

    def show_special_options(self):
        options_frame = tk.Frame(self.root)
        options_frame.pack(pady=8)
        self.special_options_frame = options_frame
        tk.Label(options_frame, text="Choose an activity:").pack()
        tk.Button(options_frame, text="Maze Runner Game", command=self.launch_maze_runner).pack(fill='x', pady=2)
        tk.Button(options_frame, text="Calculator", command=self.launch_calculator).pack(fill='x', pady=2)
        tk.Button(options_frame, text="Morse Code Translator", command=self.launch_morse_translator).pack(fill='x', pady=2)

    def handle_special_option(self, choice):
        if hasattr(self, 'special_options_frame'):
            self.special_options_frame.destroy()
            del self.special_options_frame
        if 'maze' in choice:
            self.launch_maze_runner()
        elif 'calculator' in choice:
            self.launch_calculator()
        elif 'morse' in choice:
            self.launch_morse_translator()
        else:
            self.chat_area.config(state=tk.NORMAL)
    
    def launch_maze_runner(self):
        self.reply_and_speak("Launching Maze Runner Game!")

        import pygame
        import random
        import time

        def maze_runner():
            pygame.init()

            WIDTH, HEIGHT = 600, 600
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Maze Runner")

            WHITE = (255, 255, 255)
            BLACK = (0, 0, 0)
            GREEN = (0, 255, 0)
            RED = (255, 0, 0)
            BLUE = (0, 0, 255)

            grid_size = 20
            cols = WIDTH // grid_size
            rows = HEIGHT // grid_size

            UP = (0, -1)
            DOWN = (0, 1)
            LEFT = (-1, 0)
            RIGHT = (1, 0)

            player_pos = [1, 1]
            maze = [[1 for _ in range(cols)] for _ in range(rows)]
            visited = [[False for _ in range(cols)] for _ in range(rows)]

            game_time = 60  # seconds
            finish_pos = [cols - 2, rows - 2]

            def generate_maze(x, y):
                visited[y][x] = True
                maze[y][x] = 0
                directions = [UP, DOWN, LEFT, RIGHT]
                random.shuffle(directions)

                for direction in directions:
                    nx, ny = x + direction[0] * 2, y + direction[1] * 2
                    if 0 <= nx < cols and 0 <= ny < rows and not visited[ny][nx]:
                        maze[y + direction[1]][x + direction[0]] = 0
                        maze[ny][nx] = 0
                        visited[ny][nx] = True
                        generate_maze(nx, ny)

            def draw_maze():
                for y in range(rows):
                    for x in range(cols):
                        rect = (x * grid_size, y * grid_size, grid_size, grid_size)
                        color = BLACK if maze[y][x] == 1 else WHITE
                        pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, RED, (finish_pos[0] * grid_size, finish_pos[1] * grid_size, grid_size, grid_size))

            def draw_player():
                pygame.draw.rect(screen, GREEN, (player_pos[0] * grid_size, player_pos[1] * grid_size, grid_size, grid_size))

            def valid_move(x, y):
                return 0 <= x < cols and 0 <= y < rows and maze[y][x] == 0

            def show_message(text, color):
                font = pygame.font.SysFont(None, 72)
                message = font.render(text, True, color)
                rect = message.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(message, rect)
                pygame.display.update()
                pygame.time.delay(2000)

            def game_loop():
                nonlocal player_pos  # Use nonlocal to modify player_pos inside nested function
                running = True
                generate_maze(1, 1)
                visited[1][1] = True
                maze[finish_pos[1]][finish_pos[0]] = 0

                start_time = time.time()
                clock = pygame.time.Clock()

                while running:
                    screen.fill(BLUE)
                    draw_maze()
                    draw_player()

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False

                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_UP] and valid_move(player_pos[0], player_pos[1] - 1):
                        player_pos[1] -= 1
                        time.sleep(0.1)
                    if keys[pygame.K_DOWN] and valid_move(player_pos[0], player_pos[1] + 1):
                        player_pos[1] += 1
                        time.sleep(0.1)
                    if keys[pygame.K_LEFT] and valid_move(player_pos[0] - 1, player_pos[1]):
                        player_pos[0] -= 1
                        time.sleep(0.1)
                    if keys[pygame.K_RIGHT] and valid_move(player_pos[0] + 1, player_pos[1]):
                        player_pos[0] += 1
                        time.sleep(0.1)

                    elapsed_time = int(time.time() - start_time)
                    if elapsed_time >= game_time:
                        show_message("Time's Up! You Lose!", RED)
                        running = False

                    if player_pos == finish_pos:
                        show_message("You Win!", GREEN)
                        running = False

                    font = pygame.font.SysFont(None, 36)
                    timer_text = font.render(f"Time: {game_time - elapsed_time}s", True, WHITE)
                    screen.blit(timer_text, (10, 10))

                    pygame.display.update()
                    clock.tick(30)

                pygame.quit()

            game_loop()

        maze_runner()


    def launch_calculator(self):
       self.reply_and_speak("Launching Calculator!")
       import tkinter as tk

       calc_win = tk.Toplevel(self.root)
       calc_win.title("Calculator")
       calc_win.geometry("406x500")
       calc_win.resizable(False, False)

       expr = tk.StringVar()

       def btn_click(item):
           expr.set(expr.get() + str(item))

       def clear():
           expr.set("")
       def equal():
           try:
                result = str(eval(expr.get()))
                expr.set(result)
           except Exception:
                expr.set("Error")

       entry = tk.Entry(calc_win, textvariable=expr, font=("Arial", 24), bd=8, relief=tk.RIDGE, justify="right")
       entry.grid(row=0, column=0, columnspan=4, ipadx=8, ipady=12, padx=4, pady=8, sticky="we")

       buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('+', 4, 2), ('=', 4, 3),
        ]

       for (text, row, col) in buttons:
            if text == '=':
                btn = tk.Button(calc_win, text=text, width=5, height=2, font=("Arial", 18),
                   command=equal, bg='#4CAF50', fg='white')
            else:
                cmd = lambda ch=text: btn_click(ch) if ch != 'C' else clear()
                btn = tk.Button(calc_win, text=text, width=5, height=2, font=("Arial", 18),
                            command=cmd)
            btn.grid(row=row, column=col, padx=2, pady=2)

        # Clear button
       clear_btn = tk.Button(calc_win, text='C', width=5, height=2, font=("Arial", 18),
                        command=clear, bg='#f44336', fg='white')
       clear_btn.grid(row=5, column=0, columnspan=4, sticky='we', padx=2, pady=6)


    def launch_morse_translator(self):
        self.reply_and_speak("Launching Morse Code Translator!")

        import tkinter as tk

        # Morse code dictionary, uppercase keys only
        morse_code = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
            'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
            'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
            'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
            'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
            'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
            '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
            '0': '-----', ' ': '/'
        }

        def text_to_morse(text):
            morse_chars = {'.', '-', '/'}
        # ONLY treat as Morse if the input contains ONLY Morse characters (and spaces)
            if all(char in morse_chars or char == ' ' for char in text):
                return "Invalid input! You entered Morse code instead of text."
            return ' '.join(morse_code.get(ch.upper(), '') for ch in text)

        def morse_to_text(morse):
            reverse_morse_code = {v: k for k, v in morse_code.items()}
            if any(char not in '.- /' for char in morse):
                return "Invalid Morse code! Please enter a valid Morse code."
            return ''.join(reverse_morse_code.get(ch, '') for ch in morse.split())

        def convert():
            input_text = input_text_var.get().strip()
            if not input_text:
                output_var.set("Please enter some text or Morse code.")
                return
            if conversion_var.get() == "text_to_morse":
                output_var.set(text_to_morse(input_text))
            else:
                if any(char not in '.- /' for char in input_text):
                    output_var.set("Invalid Morse code! Please enter a valid Morse code.")
                    return
                output_var.set(morse_to_text(input_text))

        def clear_all():
            input_text_var.set('')
            output_var.set('')

    # Build GUI
        morse_win = tk.Toplevel(self.root)
        morse_win.title("Morse Code Translator")
        morse_win.geometry("500x300")
        morse_win.resizable(False, False)

        tk.Label(morse_win, text="Enter Text or Morse Code:", font=("Arial", 12)).pack(pady=(10, 0))
        input_text_var = tk.StringVar()
        input_entry = tk.Entry(morse_win, textvariable=input_text_var, font=("Arial", 14), width=50)
        input_entry.pack(pady=5)
        input_entry.focus()

        conversion_var = tk.StringVar(value="text_to_morse")
        frame_radio = tk.Frame(morse_win)
        frame_radio.pack(pady=5)
        tk.Radiobutton(frame_radio, text="Text to Morse Code", variable=conversion_var, value="text_to_morse").pack(side=tk.LEFT, padx=20)
        tk.Radiobutton(frame_radio, text="Morse Code to Text", variable=conversion_var, value="morse_to_text").pack(side=tk.LEFT, padx=20)

        btn_frame = tk.Frame(morse_win)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Convert", command=convert, width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Clear", command=clear_all, width=15).pack(side=tk.LEFT, padx=10)

        tk.Label(morse_win, text="Output:", font=("Arial", 12)).pack(pady=(10, 0))
        output_var = tk.StringVar()
        output_label = tk.Label(morse_win, textvariable=output_var, font=("Arial", 14), bg="#f0f0f0",
                            width=50, height=4, anchor='nw', justify='left', bd=2, relief=tk.SUNKEN)
        output_label.pack(padx=10, pady=5, fill='both', expand=True)


    def reply_and_speak(self, bot_reply):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, "Bot: " + bot_reply + "\n", "bot")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
        self.root.update()
        speak(bot_reply, lang_code=self.lang_code)

    def voice_input(self):
        text = self.listen()
        if text:
            self.send_message(user_message=text)
        else:
            self.reply_and_speak("Sorry, I couldn't hear you properly. Please repeat it again.")

if _name_ == "_main_":
    root = tk.Tk()
    app = PyBotApp(root)
    root.mainloop()