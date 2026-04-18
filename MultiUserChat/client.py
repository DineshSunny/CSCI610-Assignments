import socket
import threading

HOST = '127.0.0.1'
PORT = 5555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

nickname = input("Enter your name: ")

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print(message)
        except:
            print("Disconnected from server")
            client.close()
            break

def send_messages():
    while True:
        message = input()
        full_message = f"{nickname}: {message}"
        client.send(full_message.encode('utf-8'))

threading.Thread(target=receive_messages).start()
threading.Thread(target=send_messages).start()