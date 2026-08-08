import socket
import threading
from datetime import datetime

# Configurable host/port. Default to localhost:5555.
HOST = "127.0.0.1"
PORT = 5555

# Maps active client socket connections to their usernames
# Structure: client_socket -> username_str
clients = {}
clients_lock = threading.Lock() # Lock to make it thread-safe

def log_event(message):
    # Log server event with a clean timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {message}")

def broadcast(message, exclude_socket=None):
    # Send a message to all active clients (excluding the sender if specified)
    # Storing bytes in variable for efficiency
    msg_bytes = message.encode("utf-8")
    with clients_lock:
        for client_sock in list(clients.keys()):
            if client_sock != exclude_socket:
                try:
                    client_sock.sendall(msg_bytes)
                except Exception:
                    # If send fails, clean up the client socket
                    # We can let the handle_client thread do the cleanup or do it here.
                    pass

def remove_client(client_socket):
    # Clean up client connection and notify others
    with clients_lock:
        username = clients.get(client_socket)
        if client_socket in clients:
            del clients[client_socket]
            
    if username:
        log_event(f"User disconnected: {username}")
        broadcast(f"SYS:{username} has left the chat.")
        
    try:
        client_socket.close()
    except Exception:
        pass

def handle_client(client_socket, client_addr):
    log_event(f"New connection from {client_addr[0]}:{client_addr[1]}")
    
    username = None
    try:
        # First message must be the JOIN prefix
        # E.g. JOIN:Gaurav
        join_data = client_socket.recv(1024).decode("utf-8")
        if not join_data or not join_data.startswith("JOIN:"):
            # Invalid protocol, kick
            client_socket.close()
            return
            
        username = join_data.split("JOIN:", 1)[1].strip()
        if not username:
            username = f"User_{client_addr[1]}" # fallback default name
            
        with clients_lock:
            clients[client_socket] = username
            
        log_event(f"User joined: {username} ({client_addr[0]}:{client_addr[1]})")
        broadcast(f"SYS:{username} has joined the chat.")
        
        # Message loop
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
                
            msg_str = data.decode("utf-8")
            if msg_str.startswith("MSG:"):
                text = msg_str.split("MSG:", 1)[1]
                log_event(f"[{username}] {text}")
                broadcast(f"MSG:{username}:{text}", exclude_socket=client_socket)
                
    except ConnectionResetError:
        # Handle abrupt client exit (e.g. closing terminal)
        pass
    except Exception as e:
        log_event(f"Error handling client: {str(e)}")
    finally:
        remove_client(client_socket)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow socket address reuse so we don't block port restarts
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen()
        log_event(f"Server listening on {HOST}:{PORT}...")
    except Exception as e:
        log_event(f"Failed to bind server to {HOST}:{PORT} - {str(e)}")
        return
        
    while True:
        try:
            client_socket, client_addr = server.accept()
            # Spawning thread so one slow client doesn't block everyone else
            threading.Thread(
                target=handle_client, 
                args=(client_socket, client_addr), 
                daemon=True
            ).start()
        except KeyboardInterrupt:
            log_event("Server shutting down.")
            break
        except Exception as e:
            log_event(f"Error accepting connection: {str(e)}")
            break
            
    server.close()

if __name__ == "__main__":
    start_server()
