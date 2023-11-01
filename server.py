import socket
from Bio.Seq import Seq

"""
Fução que vamos utilziar para realizar o processamento
A na sequência original é substituído por T na sequência complementar.
T na sequência original é substituído por A na sequência complementar.
C na sequência original é substituído por G na sequência complementar.
G na sequência original é substituído por C na sequência complementar.
"""
def process_data(data):
    # Converte a sequência de DNA em uma sequência complementar
    seq = Seq(data)
    complement_seq = seq.complement()
    return complement_seq

HOST = 'localhost'
PORT = 12345

def receive_strings(client_socket):
    while True:
        try:
            # Receba o comprimento da string
            length_bytes = client_socket.recv(4)
            if not length_bytes:
                break  # Encerra a conexão quando não há mais dados
            length = int.from_bytes(length_bytes, 'big')
            # Receba a string
            string = client_socket.recv(length).decode('utf-8')
            yield string
        except ConnectionResetError:
            break

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    print(f"Servidor esperando conexão em {HOST}:{PORT}...")
    conn, addr = s.accept()

    with conn:
        print(f"Conectado por {addr}")

        received_strings = []
        for received_string in receive_strings(conn):
            received_strings.append(received_string)
            if len(received_strings) == 100:  # Imprime a cada 100 strings recebidas
                print("Strings recebidas:", received_strings)
                received_strings = []  # Limpa o buffer

        # Imprime qualquer string remanescente
        if received_strings:
            print("Strings finais recebidas:", received_strings)