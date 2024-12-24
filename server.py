import socket
import threading
import signal
import sys


def handle_client(client_socket):
    with client_socket:
        print(f"Connexion établie avec {client_socket.getpeername()}")
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Données reçues : {data.decode().strip()}")
        print(f"Connexion fermée avec {client_socket.getpeername()}")

server_running = True

def stop_server(signal, frame):
    global server_running
    print("\nArrêt du serveur...")
    server_running = False
    sys.exit(0)

def start_server(host='0.0.0.0', port=12345):
    global server_running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Serveur démarré sur {host}:{port}")

    signal.signal(signal.SIGINT, stop_server)

    while server_running:
        conn, addr = server_socket.accept()
        print(f"Connexion établie avec {addr}")
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.start()

if __name__ == "__main__":
    start_server()


