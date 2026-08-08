# Multi-User Chat Application

This is a Python-based multi-user TCP chat application consisting of a terminal-based chat server and a desktop-based GUI chat client built with `tkinter`. Multiple clients can connect to the server at the same time to chat in a shared room.

This project was built for the Oasis Infobyte Python Programming internship (Advanced tier).

## Architecture

The application uses a **Client-Server model** built on TCP sockets:
1. **Server (`chat_server.py`)**: Runs continuously, listening for incoming socket connections on a configurable host and port (default is localhost:5555). It spawns a separate background thread for every client that joins, listens for messages, and broadcasts them to all other active clients.
2. **Client (`chat_client.py`)**: A GUI application that prompts for a username and server address upon launch. Once connected, it spins up a background receiver thread to wait for messages while keeping the GUI responsive.

## Features

- **Multi-user Support**: Threading allows multiple clients to connect and chat simultaneously.
- **Join/Leave Notifications**: Displays a system message when users join or leave the chat room.
- **Scrollable Chat Log**: Visual conversation history with color-coded names and timestamps.
- **Graceful Disconnects**: Clicking the "Disconnect" button or closing a client window closes the socket and cleans up the list on the server.
- **Connection Error Handling**: Shows a friendly error popup if the server is offline or unreachable.

## Setup and Running

Since this project relies on Python's built-in standard library modules (`socket`, `threading`, `tkinter`), no external library packages are strictly required. However, a virtual environment can be configured to manage dependencies like `tkinter-embed` (which supplies Tcl/Tk DLL support for virtual environments).

### 1. Initialize Virtual Environment (Optional but recommended)
Open a terminal in the project directory and run:
```bash
python -m venv .venv
```

Activate the virtual environment:
- On Windows (PowerShell):
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- On Linux/macOS:
  ```bash
  source .venv/bin/activate
  ```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Launching the Application
To simulate a multi-user chat room locally, follow these steps:

1. **Start the Chat Server**:
   Open a terminal and run the server script:
   ```bash
   python chat_server.py
   ```
   You will see log events in the console indicating the server is running.

2. **Start Client 1**:
   Open a second terminal window (with the virtual environment activated if using one) and launch the client:
   ```bash
   python chat_client.py
   ```
   Enter a username (e.g., "Alice") and click "Connect".

3. **Start Client 2**:
   Open a third terminal window and launch a second client:
   ```bash
   python chat_client.py
   ```
   Enter a different username (e.g., "Bob") and click "Connect".

You can now type messages in either client window and watch them broadcast in real-time between Alice and Bob!
