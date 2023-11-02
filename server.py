import socket
from Bio.Seq import Seq
from numba import njit
from numba.openmp import openmp_context as openmp

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

@njit
def process_genomas(genomas):
    genomas_processados = []
    with openmp("parallel"):
        with openmp("for reduction(+:genomas_processados) schedule(static)"):
            for genoma in genomas:
                genomas_processados.append(process_data(genoma))

    return genomas_processados

HOST = 'localhost'
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    print(f"Servidor esperando conexão em {HOST}:{PORT}...")
    conn, addr = s.accept()

    with conn:
        print(f"Conectado por {addr}")

        genomas = []
        for genomas in receive_strings(conn):
            genomas.append(genomas)
        
        genomas_processados = process_genomas(genomas)

        if genomas_processados:
            print("Genomas processados:", genomas_processados)