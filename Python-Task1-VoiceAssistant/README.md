# Desktop Voice Assistant

This is a Python-based desktop voice assistant application featuring a graphical user interface (GUI) built with `tkinter`. It supports hybrid input, allowing you to click a microphone button to speak commands or type them directly into a text entry box. It uses speech recognition to parse voice commands, OpenWeatherMap API for weather details, Wikipedia library for general knowledge lookups, and text-to-speech (TTS) to speak its replies out loud.

This project was built for the Oasis Infobyte Python Programming internship (Advanced tier).

## Features

- **Hybrid Input**: Use voice command recognition via your microphone or type fallback text commands.
- **Out-Loud Responses**: Speaks replies using the `pyttsx3` text-to-speech engine.
- **Scrollable Chat Log**: A visual scrollable interface showing user inputs and assistant replies with color-coded tags.
- **Status Indicator**: Shows what the assistant is doing (Idle, Listening, Thinking, Speaking).
- **Time & Date**: Check current time and date.
- **Weather Information**: Fetch real-time weather details for any city (requires OpenWeatherMap API key).
- **Wikipedia Search**: Look up short summaries of topics directly from Wikipedia.
- **Web Navigation**: Open popular websites (like YouTube, Google, Gmail, GitHub) or perform search queries in the default web browser.
- **Basic Chit-chat**: Responds to greetings, "how are you", "what's your name", and farewells.

## Tech Stack

- **Python 3.12**
- **Tkinter**: GUI library
- **SpeechRecognition**: Google Speech Recognition API wrapper
- **PyAudio**: Microphone audio input streaming
- **Pyttsx3**: Offline Text-to-Speech library
- **Wikipedia**: Wikipedia search wrapper
- **Requests**: Fetching weather data via OpenWeatherMap API
- **Tkinter-embed**: Portability package to provide Tcl/Tk DLLs in embedded Python setups

## Getting a Weather API Key

To get weather updates, you will need a free API key from OpenWeatherMap:
1. Go to [OpenWeatherMap](https://openweathermap.org/) and register for a free account.
2. Navigate to the **API keys** tab on your profile dashboard.
3. Copy your unique API key.
4. Rename `config_example.py` to `config.py` in your project folder and replace the placeholder value with your key:
   ```python
   WEATHER_API_KEY = "your_actual_api_key_here"
   ```

## Setup and Running

1. **Extract or clone** the project files into a folder.
2. **Open a terminal/PowerShell** in the directory.
3. **Initialize the Python virtual environment**:
   ```bash
   python -m venv .venv
   ```
4. **Activate the virtual environment**:
   - On Windows (PowerShell):
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - On Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
5. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
6. **Configure the Weather API Key** in `config.py` (see the section above).
7. **Run the application**:
   ```bash
   python voice_assistant.py
   ```

To run the unit tests:
```bash
python -m unittest test_voice_assistant.py
```

## Example Commands to Try

Here are some examples of what you can type or say:
- "Hello" or "Hey assistant"
- "What is your name?" or "How are you?"
- "What is the time?"
- "What is today's date?"
- "Weather in London" (requires OpenWeatherMap API key)
- "Wikipedia Python programming language" or "Who is Albert Einstein?"
- "Open YouTube" or "Open Google"
- "Thank you"
- "Goodbye" or "Bye"
