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
nicknames = []

def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except:
            remove_client(client)

def remove_client(client):
    if client in clients:
        index = clients.index(client)
        nickname = nicknames[index]
        clients.remove(client)
        nicknames.remove(nickname)
        client.close()
        broadcast(f"{nickname} left the chat.".encode('utf-8'))
        logging.info(f"{nickname} disconnected")

def handle_client(client):
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
        print(f"Connected with {str(address)}")

        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')

        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname: {nickname}")
        broadcast(f"{nickname} joined the chat!".encode('utf-8'))
        client.send("Connected to server!".encode('utf-8'))

        logging.info(f"{nickname} connected from {address}")

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

# Create Server Socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

receive_connections()