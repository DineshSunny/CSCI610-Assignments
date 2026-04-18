import socket
import threading
from cryptography.fernet import Fernet

# Load encryption key
with open("key.key", "rb") as f:
    key = f.read()

cipher = Fernet(key)

HOST = '127.0.0.1'
PORT = 5555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def authenticate():
    action = input("LOGIN or REGISTER: ").strip().upper()
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    data = f"{action}:{username}:{password}"
    client.send(cipher.encrypt(data.encode()))

    try:
        response = cipher.decrypt(client.recv(1024)).decode()
    except:
        print("Server error")
        return None

    if response == "SUCCESS":
        print("Authenticated successfully!")
        return username
    else:
        print("Authentication failed")
        return None

def receive():
    while True:
        try:
            message = client.recv(1024)
            print(cipher.decrypt(message).decode())
        except:
            print("Disconnected from server")
            break

def write(username):
    while True:
        message = input()
        full_message = f"{username}: {message}"
        client.send(cipher.encrypt(full_message.encode()))

# Start process
try:
    initial = cipher.decrypt(client.recv(1024)).decode()
except:
    print("Connection failed")
    exit()

if initial == "AUTH":
    username = authenticate()
    if not username:
        exit()

threading.Thread(target=receive, daemon=True).start()
write(username)