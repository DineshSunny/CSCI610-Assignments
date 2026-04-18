import socket
import threading
import logging

# Server Configuration
HOST = '127.0.0.1'
PORT = 5555

# Configure Logging
logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

clients = []
usernames = []
users = {}  # in-memory: {username: password}

def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except:
            remove_client(client)

def remove_client(client):
    if client in clients:
        index = clients.index(client)
        username = usernames[index]
        clients.remove(client)
        usernames.remove(username)
        client.close()
        broadcast(f"{username} left the chat.".encode('utf-8'))
        logging.info(f"{username} disconnected")

def authenticate(client):
    """
    Expects: 'LOGIN:username:password' or 'REGISTER:username:password'
    """
    client.send("AUTH".encode('utf-8'))

    try:
        data = client.recv(1024).decode('utf-8')
        action, username, password = data.split(":")
    except:
        client.send("FAIL".encode('utf-8'))
        return None

    if action == "REGISTER":
        if username in users:
            client.send("FAIL".encode('utf-8'))
            return None
        users[username] = password
        client.send("SUCCESS".encode('utf-8'))
        return username

    elif action == "LOGIN":
        if username in users and users[username] == password:
            client.send("SUCCESS".encode('utf-8'))
            return username
        else:
            client.send("FAIL".encode('utf-8'))
            return None

    else:
        client.send("FAIL".encode('utf-8'))
        return None

def handle_client(client, username):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
            logging.info(f"Message: {message.decode('utf-8')}")
        except:
            remove_client(client)
            break

def receive_connections():
    server.listen()
    print(f"Server running on {HOST}:{PORT}")
    logging.info("Server started")

    while True:
        client, address = server.accept()
        print(f"Connected with {address}")

        username = authenticate(client)

        if not username:
            client.close()
            continue

        usernames.append(username)
        clients.append(client)

        print(f"User: {username}")
        broadcast(f"{username} joined the chat!".encode('utf-8'))
        client.send("Connected to server!".encode('utf-8'))

        logging.info(f"{username} connected from {address}")

        thread = threading.Thread(target=handle_client, args=(client, username))
        thread.start()

# Create Server Socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

receive_connections()