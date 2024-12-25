import socket
import subprocess
import re
import argparse
import platform

def resolve_ip(domain):
    """
    Résout un nom de domaine en adresse IPv4.
    """
    try:
        ip = socket.gethostbyname(domain)                                                                               # résout un nom de domaine en adresse IP
        print(f"Adresse IP résolue pour {domain}: {ip}")
        return ip
    except socket.gaierror as e:
        print(f"Erreur de résolution DNS pour {domain}: {e}")
        return None

def run_traceroute(target, progressive):
    """
    Exécute la commande traceroute et récupère les adresses IP.
    """
    # Résolution DNS si le target est un nom de domaine
    if not re.match(r"^\d+\.\d+\.\d+\.\d+$", target):  # Si ce n'est pas une IP
        target = resolve_ip(target)
        if not target:
            return []

    if platform.system().lower() == "windows":
        command = ["tracert", target]
    else:
        command = ["traceroute", target]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)                      # récupère les IP des routeurs traversé en utilisant la commande tracert vers 'target'
    results = []
    print(process.stdout)
    for line in iter(process.stdout.readline, ''):
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)                                                        # extrait l'adresse ip de la ligne
        if match:
            ip = match.group(1)
            results.append(ip)
            if progressive:
                print(ip)

    stderr = process.stderr.read()
    if stderr:
        print("Erreur lors de l'exécution de la commande :", stderr)

    process.wait()
    return results


def send_results_to_server(results, host, port):
    """
    Envoie les résultats au serveur.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                                   # création du socket de type IpV4 et TCP
    try:
        client_socket.connect((host, port))                                                                             # connexion du client au serveur grace au port et à l'IP
        for result in results:
            client_socket.sendall((result + "\n").encode())                                                             #
        print("Résultats envoyés au serveur.")
    finally:
        client_socket.close()
        print("Connexion fermée.")


def save_results_to_file(results, output_file):
    """
    Sauvegarde les résultats dans un fichier local.
    """
    with open(output_file, 'w') as f:
        for ip in results:
            f.write(ip + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Client pour exécuter traceroute et envoyer les résultats.",
        epilog="Exemple : python client.py google.com -s 192.168.1.1 -p 8080 --progressive"
    )
    parser.add_argument("target", help="URL ou adresse IP cible.")
    parser.add_argument("-s", "--server", default="127.0.0.1", help="Adresse IP du serveur.")
    parser.add_argument("-p", "--port", type=int, default=12345, help="Port du serveur.")
    parser.add_argument("--progressive", action="store_true", help="Afficher les résultats au fur et à mesure.")
    parser.add_argument("-o", "--output-file", help="Fichier où enregistrer les résultats localement.")
    args = parser.parse_args()

    # Exécution du traceroute
    results = run_traceroute(args.target, args.progressive)
    print("Résultats du traceroute :", results)

    # Enregistrement local si demandé
    if args.output_file:
        save_results_to_file(results, args.output_file)

    # Envoi au serveur
    if results:
        print("Envoi des résultats au serveur...")
        send_results_to_server(results, args.server, args.port)
    else:
        print("Aucun résultat à envoyer.")
