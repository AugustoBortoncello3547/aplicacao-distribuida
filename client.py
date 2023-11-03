import socket
import pandas as pd

df = pd.read_csv("dados.csv", delimiter="\t")
valores = df["intergenicregion_sequence"].astype(str).tolist()

#print(valores)

# Configurações do cliente
HOST = 'localhost'
PORT = 12345

def send_strings(client_socket, strings):
    for string in strings:
        client_socket.send(len(string).to_bytes(4, 'big'))
        client_socket.send(string.encode('utf-8'))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    chunk_size = 100  # Tamanho de cada parte
    for i in range(0, len(valores), chunk_size):
        chunk = valores[i:i + chunk_size]
        send_strings(s, chunk)

print("Dados enviados com sucesso para o servidor.")