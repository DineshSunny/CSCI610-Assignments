import socket
import threading
import sqlite3
from cryptography.fernet import Fernet

# Load encryption key
with open("key.key", "rb") as f:
    key = f.read()

cipher = Fernet(key)

HOST = '127.0.0.1'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
usernames = []

def authenticate(username, password):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()

    conn.close()
    return result

def register(username, password):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def broadcast(message):
    for client in clients:
        client.send(message)

def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            decrypted = cipher.decrypt(message).decode()
            print(decrypted)

            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            usernames.pop(index)
            print("User disconnected")
            break

def receive():
    print("Server running...")

    while True:
        client, address = server.accept()
        print(f"Connected: {address}")

        client.send(cipher.encrypt("AUTH".encode()))

        try:
            data = cipher.decrypt(client.recv(1024)).decode()
            action, username, password = data.split(":")
        except:
            client.close()
            continue

        if action == "LOGIN":
            if authenticate(username, password):
                client.send(cipher.encrypt("SUCCESS".encode()))
            else:
                client.send(cipher.encrypt("FAIL".encode()))
                client.close()
                continue

        elif action == "REGISTER":
            if register(username, password):
                client.send(cipher.encrypt("SUCCESS".encode()))
            else:
                client.send(cipher.encrypt("FAIL".encode()))
                client.close()
                continue

        clients.append(client)
        usernames.append(username)

        print(f"{username} joined chat")

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

receive()