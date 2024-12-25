import socket
import subprocess
import re

def run_traceroute(target):
    command = ["traceroute", target]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
    results = []
    for line in process.stdout:
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
        if match:
            results.append(match.group(1))
    return results

def send_results_to_server(results, host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        for result in results:
            client_socket.sendall((result + "\n").encode())
        print("Résultats envoyés au serveur.")
    finally:
        client_socket.close()

if __name__ == "__main__":
    target = "example.com"
    host = "127.0.0.1"
    port = 12345

    results = run_traceroute(target)
    send_results_to_server(results, host, port)
