import socket
import threading

HOST = '127.0.0.1'
PORT = 5555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def authenticate():
    """
    Waits for AUTH prompt, then sends:
    LOGIN:username:password or REGISTER:username:password
    """
    try:
        message = client.recv(1024).decode('utf-8')
        if message == "AUTH":
            action = input("LOGIN or REGISTER: ").strip().upper()
            username = input("Username: ").strip()
            password = input("Password: ").strip()

            data = f"{action}:{username}:{password}"
            client.send(data.encode('utf-8'))

            response = client.recv(1024).decode('utf-8')
            if response == "SUCCESS":
                print("Authenticated successfully!")
                return username
            else:
                print("Authentication failed.")
                return None
    except:
        print("Connection error during authentication.")
        return None

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print(message)
        except:
            print("Connection lost!")
            client.close()
            break

def send_messages(username):
    while True:
        msg = input("")
        full = f"{username}: {msg}"
        client.send(full.encode('utf-8'))

# --- Start ---
username = authenticate()
if not username:
    client.close()
    exit()

threading.Thread(target=receive_messages).start()
threading.Thread(target=send_messages, args=(username,)).start()