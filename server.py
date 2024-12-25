import socket
import threading
import argparse
import signal
import sys
import select

# Variable globale pour gérer l'arrêt du serveur
server_running = True

def handle_client(client_socket, output_file):
    with client_socket:
        print(f"Connexion établie avec {client_socket.getpeername()}")
        buffer = []
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode().strip()
            buffer.append(message)
            print(f"Données reçues : {message}")
        if output_file:
            with open(output_file, 'a') as f:
                f.write("\n".join(buffer) + "\n")
        print(f"Connexion fermée avec {client_socket.getpeername()}")

def stop_server(signal, frame):
    global server_running
    print("\nArrêt du serveur...")
    server_running = False  # Mettre à jour la variable pour arrêter la boucle d'acceptation
    sys.exit(0)  # Quitter proprement le programme

def start_server(host='0.0.0.0', port=12345, output_file=None):
    global server_running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                                   # création d'un socket de type ipV4 et TCP
    server_socket.bind((host, port))                                                                                    # liaison du socket au port et à l'IP du serveur
    server_socket.listen(5)                                                                                             # Le serveur peut gérer jusqu'à 5 connexions en attente
    print(f"Serveur démarré sur {host}:{port}")

    # Enregistrer le gestionnaire de signal pour intercepter Ctrl + C
    signal.signal(signal.SIGINT, stop_server)                                                                           # arrêter le serveur à tout moment, met à False server_running

    # Utilisation de select pour rendre le serveur réactif
    inputs = [server_socket]  # Liste des objets à surveiller (ici, juste le socket du serveur)
    while server_running:
        # Utilisation de select pour vérifier si une connexion est prête sans bloquer
        readable, _, _ = select.select(inputs, [], [], 1.0)  # Timeout de 1 seconde

        for s in readable:
            if s is server_socket:
                conn, addr = server_socket.accept()  # Accepte une nouvelle connexion
                print(f"Connexion établie avec {addr}")
                # Lancer un thread pour gérer chaque client
                client_thread = threading.Thread(target=handle_client, args=(conn, output_file))                        # création d'un thread pour chaque connexion avec un client
                client_thread.start()                                                                                   # client traité à indépendament des autres grâce à handle_client et peut simultanément accepter de nouvelles connexions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serveur pour recevoir les résultats de traceroute.")
    parser.add_argument("-p", "--port", type=int, default=12345, help="Port d'écoute du serveur.")
    parser.add_argument("-o", "--output-file", help="Fichier où enregistrer les résultats.")
    args = parser.parse_args()

    start_server(port=args.port, output_file=args.output_file)
