import os
import sys
import socket
import threading
from datetime import datetime

# Point Tcl/Tk environment variables to virtual env if present, 
# to fix TclError about init.tcl not found
base_dir = os.path.dirname(os.path.abspath(__file__))
venv_tcl = os.path.join(base_dir, ".venv", "Lib", "site-packages", "tcl")
if os.path.exists(venv_tcl):
    os.environ["TCL_LIBRARY"] = os.path.join(venv_tcl, "tcl8.6")
    os.environ["TK_LIBRARY"] = os.path.join(venv_tcl, "tk8.6")


class ChatClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Room")
        self.root.geometry("450x520")
        self.root.resizable(False, False)
        
        self.client_socket = None
        self.username = ""
        self.is_connected = False
        
        # Defer imports of tkinter inside constructor so it loads correctly
        import tkinter as tk
        from tkinter import ttk, messagebox
        self.tk = tk
        self.ttk = ttk
        self.messagebox = messagebox
        
        # Main container frame
        self.container = self.ttk.Frame(self.root, padding=20)
        self.container.pack(fill="both", expand=True)
        
        self.show_connect_screen()
        
    def show_connect_screen(self):
        # Clear the frame widgets first
        for widget in self.container.winfo_children():
            widget.destroy()
            
        self.root.title("Join Chat Room")
        
        title_label = self.ttk.Label(self.container, text="Join Chat Room", font=("Arial", 16, "bold"), foreground="#2c3e50")
        title_label.pack(pady=(25, 25))
        
        form_frame = self.ttk.Frame(self.container)
        form_frame.pack(fill="x", padx=15)
        form_frame.columnconfigure(1, weight=1)
        
        # Username Input
        self.ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=8)
        self.username_entry = self.ttk.Entry(form_frame)
        self.username_entry.grid(row=0, column=1, sticky="ew", pady=8, padx=(10, 0))
        self.username_entry.focus()
        
        # Host Input
        self.ttk.Label(form_frame, text="Host:").grid(row=1, column=0, sticky="w", pady=8)
        self.host_entry = self.ttk.Entry(form_frame)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.grid(row=1, column=1, sticky="ew", pady=8, padx=(10, 0))
        
        # Port Input
        self.ttk.Label(form_frame, text="Port:").grid(row=2, column=0, sticky="w", pady=8)
        self.port_entry = self.ttk.Entry(form_frame)
        self.port_entry.insert(0, "5555")
        self.port_entry.grid(row=2, column=1, sticky="ew", pady=8, padx=(10, 0))
        
        # Bind Enter key to trigger connection
        self.username_entry.bind("<Return>", lambda e: self.connect_to_server())
        
        connect_btn = self.ttk.Button(self.container, text="Connect", command=self.connect_to_server)
        connect_btn.pack(pady=30, fill="x", padx=15)
        
        # TODO: save last used connection configurations in local json later
        
    def show_chat_screen(self):
        # Clear the frame widgets
        for widget in self.container.winfo_children():
            widget.destroy()
            
        self.root.title(f"Chat Room - {self.username}")
        
        # Top banner showing username and Disconnect button
        header_frame = self.ttk.Frame(self.container)
        header_frame.pack(fill="x", pady=(0, 10))
        
        status_lbl = self.ttk.Label(header_frame, text=f"Logged in: {self.username}", font=("Arial", 11, "bold"), foreground="#27ae60")
        status_lbl.pack(side="left")
        
        disc_btn = self.ttk.Button(header_frame, text="Disconnect", command=self.disconnect)
        disc_btn.pack(side="right")
        
        # Conversation log frame
        log_frame = self.ttk.Frame(self.container)
        log_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.chat_log = self.tk.Text(log_frame, wrap="word", state="disabled", font=("Arial", 10))
        self.chat_log.pack(side="left", fill="both", expand=True)
        
        scrollbar = self.ttk.Scrollbar(log_frame, command=self.chat_log.yview)
        scrollbar.pack(side="right", fill="y")
        self.chat_log.config(yscrollcommand=scrollbar.set)
        
        # Format tags
        self.chat_log.tag_config("me", foreground="#2980b9", font=("Arial", 10, "bold"))
        self.chat_log.tag_config("other", foreground="#8e44ad", font=("Arial", 10, "bold"))
        self.chat_log.tag_config("system", foreground="#7f8c8d", font=("Arial", 9, "italic"))
        self.chat_log.tag_config("time", foreground="#95a5a6", font=("Arial", 8))
        
        # Input message area
        input_frame = self.ttk.Frame(self.container)
        input_frame.pack(fill="x")
        
        self.msg_entry = self.ttk.Entry(input_frame)
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.msg_entry.bind("<Return>", lambda e: self.send_message())
        self.msg_entry.focus()
        
        send_btn = self.ttk.Button(input_frame, text="Send", command=self.send_message)
        send_btn.pack(side="right")
        
    def connect_to_server(self):
        username = self.username_entry.get().strip()
        host = self.host_entry.get().strip()
        port_str = self.port_entry.get().strip()
        
        if not username:
            self.messagebox.showerror("Error", "Please enter a username.")
            return
            
        try:
            port = int(port_str)
        except ValueError:
            self.messagebox.showerror("Error", "Port must be a valid number.")
            return
            
        try:
            # Create socket connection
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            
            # Send register join code to server
            join_payload = f"JOIN:{username}"
            self.client_socket.sendall(join_payload.encode("utf-8"))
            
            self.username = username
            self.is_connected = True
            
            # Load Chat Layout
            self.show_chat_screen()
            
            # Spawn receiver thread
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
        except Exception as e:
            self.messagebox.showerror("Connection Failed", f"Could not connect to {host}:{port}.\nError details: {str(e)}")
            if self.client_socket:
                try:
                    self.client_socket.close()
                except Exception:
                    pass
                    
    def receive_messages(self):
        # Listener loop running in background
        while self.is_connected:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    # Clean disconnect from server
                    self.root.after(0, self.handle_server_disconnect, "Connection closed by the server.")
                    break
                    
                msg_str = data.decode("utf-8")
                self.root.after(0, self.parse_and_append_message, msg_str)
            except Exception:
                if self.is_connected:
                    self.root.after(0, self.handle_server_disconnect, "Disconnected from server.")
                break
                
    def parse_and_append_message(self, msg_str):
        # Parse simple prefix codes and show to user
        if msg_str.startswith("SYS:"):
            text = msg_str.split("SYS:", 1)[1]
            self.append_to_log("system", text)
        elif msg_str.startswith("MSG:"):
            parts = msg_str.split("MSG:", 1)[1].split(":", 1)
            if len(parts) == 2:
                sender, text = parts
                self.append_to_log("other", text, sender)
                
    def send_message(self):
        text = self.msg_entry.get().strip()
        if not text or not self.is_connected:
            return
            
        self.msg_entry.delete(0, self.tk.END)
        
        try:
            payload = f"MSG:{text}"
            self.client_socket.sendall(payload.encode("utf-8"))
            # Append locally right away
            self.append_to_log("me", text)
        except Exception as e:
            self.messagebox.showerror("Error", f"Failed to send: {str(e)}")
            self.disconnect()
            
    def append_to_log(self, sender_type, text, sender_name=None):
        self.chat_log.config(state="normal")
        
        # Add timestamp
        time_str = datetime.now().strftime("[%H:%M] ")
        self.chat_log.insert(self.tk.END, time_str, "time")
        
        if sender_type == "me":
            self.chat_log.insert(self.tk.END, "You: ", "me")
            self.chat_log.insert(self.tk.END, text + "\n")
        elif sender_type == "other":
            self.chat_log.insert(self.tk.END, f"{sender_name}: ", "other")
            self.chat_log.insert(self.tk.END, text + "\n")
        elif sender_type == "system":
            self.chat_log.insert(self.tk.END, text + "\n", "system")
            
        self.chat_log.config(state="disabled")
        self.chat_log.see(self.tk.END)
        
    def disconnect(self):
        self.is_connected = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception:
                pass
        self.client_socket = None
        self.show_connect_screen()
        
    def handle_server_disconnect(self, message):
        self.messagebox.showwarning("Connection Lost", message)
        self.disconnect()


if __name__ == "__main__":
    import tkinter as tk
    root = tk.Tk()
    app = ChatClientApp(root)
    root.mainloop()
