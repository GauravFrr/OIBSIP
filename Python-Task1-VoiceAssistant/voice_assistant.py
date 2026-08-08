import os
import sys
import webbrowser
import requests
import wikipedia
import pyttsx3
import speech_recognition as sr
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import threading

# Point Tcl/Tk environment variables to virtual env if present, 
# to fix TclError about init.tcl not found
base_dir = os.path.dirname(os.path.abspath(__file__))
venv_tcl = os.path.join(base_dir, ".venv", "Lib", "site-packages", "tcl")
if os.path.exists(venv_tcl):
    os.environ["TCL_LIBRARY"] = os.path.join(venv_tcl, "tcl8.6")
    os.environ["TK_LIBRARY"] = os.path.join(venv_tcl, "tk8.6")

# Import OpenWeatherMap API Key configuration
try:
    import config
    WEATHER_API_KEY = config.WEATHER_API_KEY
except ImportError:
    WEATHER_API_KEY = ""

# Core helper functions

def speak(text):
    # Speak the given text out loud using pyttsx3.
    # We initialize the engine instance inside this function to prevent 
    # threading issues when run from background threads.
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        # TODO: log speech error somewhere
        pass

def listen():
    # Record from microphone and convert to text using Google Speech Recognition
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # Small adjustment for ambient room noise
        r.adjust_for_ambient_noise(source, duration=0.6)
        try:
            audio = r.listen(source, timeout=4, phrase_time_limit=5)
            text = r.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            # Silence/timeout
            return None
        except sr.UnknownValueError:
            return "ERROR: Could not understand the voice audio."
        except sr.RequestError:
            return "ERROR: Google speech service is currently unreachable."
        except Exception as e:
            return f"ERROR: Microphone problem ({str(e)})."

def get_time():
    # Return current time in a friendly format
    return datetime.now().strftime("%I:%M %p")

def get_date():
    # Return current date formatted nicely
    return datetime.now().strftime("%A, %B %d, %Y")

def get_weather(city):
    # Fetch current weather details for a city using OpenWeatherMap API
    if not WEATHER_API_KEY or WEATHER_API_KEY == "YOUR_API_KEY_HERE":
        return "I can't fetch weather updates because the API key is not configured. Please add it to config.py."
    
    # speech recognition sometimes adds a period at the end of city name
    city_clean = city.strip().lower().rstrip(".")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_clean}&appid={WEATHER_API_KEY}&units=metric"
    
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            temp = round(data["main"]["temp"])
            condition = data["weather"][0]["description"]
            return f"The weather in {city.title()} is currently {temp} degrees Celsius with {condition}."
        elif res.status_code == 404:
            return f"Sorry, I couldn't find the city '{city}'. Please check the spelling."
        else:
            return "Sorry, I had trouble reaching the weather service. Try again later."
    except Exception:
        return "Unable to retrieve weather. Please check your internet connection."

def search_wikipedia(query):
    # Lookup query summary from wikipedia
    query_clean = query.strip().lower().rstrip(".")
    try:
        summary = wikipedia.summary(query_clean, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        # list first few options if ambiguous
        options = ", ".join(e.options[:3])
        return f"That query could mean a few things. Did you mean: {options}?"
    except wikipedia.exceptions.PageError:
        return f"I couldn't find any Wikipedia page matching '{query}'."
    except Exception:
        return "I had trouble loading Wikipedia. Check your internet connection."

def open_website(name):
    # Open commonly used websites in default browser
    sites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "github": "https://www.github.com",
        "stackoverflow": "https://stackoverflow.com"
    }
    
    clean_name = name.strip().lower().rstrip(".")
    url = sites.get(clean_name)
    if url:
        webbrowser.open(url)
        return f"Opening {name}."
    else:
        # Search google if direct URL isn't mapped
        search_url = f"https://www.google.com/search?q={name}"
        webbrowser.open(search_url)
        return f"Searching Google for '{name}'."

def handle_command(command):
    # Route command to appropriate helper function based on keywords
    cmd = command.lower().strip()
    
    # Basic conversation / chit-chat
    if any(greet in cmd for greet in ["hello", "hi", "hey assistant"]):
        return "Hello! How can I help you today?"
        
    elif "how are you" in cmd:
        return "I'm doing great, thank you for asking! How are you?"
        
    elif "your name" in cmd:
        return "I am your Python Voice Assistant. You can call me helper."
        
    elif any(thanks in cmd for thanks in ["thank you", "thanks"]):
        return "You're very welcome!"
        
    elif any(bye in cmd for bye in ["bye", "goodbye", "exit"]):
        return "Goodbye! Have a nice day!"
        
    # Time & Date
    elif "time" in cmd:
        return f"The current time is {get_time()}."
        
    elif any(date_word in cmd for date_word in ["date", "today"]):
        return f"Today's date is {get_date()}."
        
    # Weather check
    elif "weather" in cmd:
        if "in " in cmd:
            parts = cmd.split("in ")
            city = parts[-1].strip()
            return get_weather(city)
        else:
            return "Which city would you like to check the weather for? E.g. say 'weather in Paris'."
            
    # Wikipedia lookup
    elif any(wiki in cmd for wiki in ["wikipedia", "search for", "search", "look up", "who is", "what is"]):
        # Strip routing keywords to get the core query
        query = cmd
        for phrase in ["wikipedia", "search for", "search", "look up", "who is", "what is"]:
            query = query.replace(phrase, "")
        query = query.strip()
        
        if not query:
            return "What would you like me to look up on Wikipedia?"
        return search_wikipedia(query)
        
    # Opening websites
    elif "open" in cmd:
        parts = cmd.split("open ")
        site_name = parts[-1].strip()
        if not site_name or site_name == "open":
            return "Which site would you like me to open? E.g. 'open google'."
        return open_website(site_name)
        
    # Fallback response for unmatched commands
    else:
        return "I didn't quite catch that. Can you try again or ask something else?"


class VoiceAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Desktop Voice Assistant")
        self.root.geometry("480x560")
        self.root.resizable(False, False)
        
        # Grid layout configure
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configure layout and custom styles
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10, "bold"))
        style.configure("Status.TLabel", font=("Arial", 11, "italic"), foreground="#7f8c8d")
        
        # Header title
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_label = ttk.Label(header_frame, text="Desktop Voice Assistant", font=("Arial", 14, "bold"), foreground="#2c3e50")
        header_label.pack(side="left")
        
        # Scrollable Conversation Log (Chat History)
        log_frame = ttk.Frame(self.root, padding=10)
        log_frame.grid(row=1, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.chat_log = tk.Text(log_frame, wrap="word", state="disabled", font=("Arial", 10))
        self.chat_log.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.chat_log.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_log.config(yscrollcommand=scrollbar.set)
        
        # Chat log formatting tags
        self.chat_log.tag_config("user", foreground="#2980b9", font=("Arial", 10, "bold"))
        self.chat_log.tag_config("assistant", foreground="#27ae60", font=("Arial", 10, "bold"))
        self.chat_log.tag_config("system", foreground="#7f8c8d", font=("Arial", 9, "italic"))
        
        # Status Bar / Listening Indicator
        status_frame = ttk.Frame(self.root, padding=(10, 5))
        status_frame.grid(row=2, column=0, sticky="ew")
        self.status_label = ttk.Label(status_frame, text="Status: Idle", style="Status.TLabel")
        self.status_label.pack(side="left")
        
        # Input Frame (Text Entry + Send Button)
        input_frame = ttk.Frame(self.root, padding=10)
        input_frame.grid(row=3, column=0, sticky="ew")
        input_frame.columnconfigure(0, weight=1)
        
        self.entry_field = ttk.Entry(input_frame)
        self.entry_field.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.entry_field.bind("<Return>", lambda event: self.send_text_command())
        
        send_btn = ttk.Button(input_frame, text="Send", command=self.send_text_command)
        send_btn.grid(row=0, column=1, padx=(0, 5))
        
        # Voice Input Frame (Mic Button)
        voice_frame = ttk.Frame(self.root, padding=(10, 0, 10, 15))
        voice_frame.grid(row=4, column=0, sticky="ew")
        
        self.mic_btn = ttk.Button(voice_frame, text="🎤 Click & Speak", command=self.start_voice_input)
        self.mic_btn.pack(fill="x")
        
        # Show greeting in chat history
        self.append_to_log("assistant", "Hello! I am your Voice Assistant. Ask me anything or say 'hello'.")
        
    def append_to_log(self, sender, text):
        # Add a message to the chat log
        self.chat_log.config(state="normal")
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        self.chat_log.insert(tk.END, timestamp, "system")
        
        if sender == "user":
            self.chat_log.insert(tk.END, "You: ", "user")
            self.chat_log.insert(tk.END, text + "\n\n")
        elif sender == "assistant":
            self.chat_log.insert(tk.END, "Assistant: ", "assistant")
            self.chat_log.insert(tk.END, text + "\n\n")
        else:
            self.chat_log.insert(tk.END, text + "\n\n", "system")
            
        self.chat_log.config(state="disabled")
        self.chat_log.see(tk.END)
        
    def update_status(self, text, color=None):
        # Update the listening/status indicator in a thread-safe way
        self.root.after(0, lambda: self.status_label.config(text=f"Status: {text}"))
        
    def send_text_command(self):
        # Process user commands from the text field
        cmd = self.entry_field.get().strip()
        if not cmd:
            return
        
        self.entry_field.delete(0, tk.END)
        self.append_to_log("user", cmd)
        
        # Run processing on a background thread so the GUI doesn't hang
        threading.Thread(target=self.process_command_flow, args=(cmd,), daemon=True).start()
        
    def start_voice_input(self):
        # Disable buttons and start background speech recognition flow
        self.mic_btn.config(state="disabled")
        self.update_status("Listening...")
        self.append_to_log("system", "Listening for voice input...")
        
        threading.Thread(target=self.voice_input_flow, daemon=True).start()
        
    def voice_input_flow(self):
        # Background thread flow for mic listening
        cmd = listen()
        
        # Reset buttons and state on UI thread
        self.root.after(0, lambda: self.mic_btn.config(state="normal"))
        self.update_status("Idle")
        
        if not cmd:
            self.root.after(0, lambda: self.append_to_log("system", "No audio detected / timed out."))
            return
            
        if cmd.startswith("ERROR:"):
            # If microphone error occurred, print it and announce it
            self.root.after(0, lambda: self.append_to_log("system", cmd))
            return
            
        # Log voice command as user text and process it
        self.root.after(0, lambda: self.append_to_log("user", cmd))
        self.process_command_flow(cmd)
        
    def process_command_flow(self, cmd):
        # Route command and get assistant response
        self.update_status("Thinking...")
        response = handle_command(cmd)
        
        self.update_status("Speaking...")
        # Write assistant response to GUI chat log
        self.root.after(0, lambda: self.append_to_log("assistant", response))
        
        # Speak the response out loud
        speak(response)
        
        self.update_status("Idle")


if __name__ == "__main__":
    import tkinter as tk
    root = tk.Tk()
    app = VoiceAssistantApp(root)
    root.mainloop()
