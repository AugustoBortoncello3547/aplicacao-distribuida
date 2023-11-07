import socket
from Bio.Seq import Seq
from numba import njit
from numba.openmp import openmp_context as openmp
from numba.openmp import omp_get_wtime, omp_get_thread_num, omp_get_num_threads,omp_set_num_threads
from numba.typed import List

import struct
import time 


"""
Fução que vamos utiliziar para realizar o processamento
Converte a sequência de DNA em uma sequência complementar
A na sequência original é substituído por T na sequência complementar.
T na sequência original é substituído por A na sequência complementar.
C na sequência original é substituído por G na sequência complementar.
G na sequência original é substituído por C na sequência complementar.
"""
@njit
def processarParalelamenteOpenMP(genomasRecebidos, cores):
    omp_set_num_threads(cores)
    steps = len(genomasRecebidos)
    genomas_processados = List()

    with openmp("parallel for"):
        for i in range(steps):
            seq = genomasRecebidos[i]
            complemento = {"A": "T", "T": "A", "C": "G", "G": "C"}
            complemento_inverso_seq = ""
            for nucleotideo in seq:
                if nucleotideo in complemento:
                    complemento_inverso_seq += complemento[nucleotideo]
                else:
                    complemento_inverso_seq += nucleotideo  # Se não for A, T, C, ou G, mantém o mesmo caractere
            genomas_processados.append(complemento_inverso_seq)
    return genomas_processados

def processarParalelamenteThread(genomasRecebidos, cores):
    genomas_processados = List()

    return genomas_processados

def recieve_metadata(client_socket):
    # Receba o método
    method_bytes = client_socket.recv(4)
    method_length = int.from_bytes(method_bytes, 'big')
    method = client_socket.recv(method_length).decode('utf-8')

    # Receba a quantidade de núcleos
    cores_bytes = client_socket.recv(4)
    cores = int.from_bytes(cores_bytes, 'big')

    # Receba o nível
    level_bytes = client_socket.recv(4)
    level_length = int.from_bytes(level_bytes, 'big')
    level = client_socket.recv(level_length).decode('utf-8')

    return method, cores, level

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

HOST = 'localhost'
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    print(f"Servidor esperando conexão em {HOST}:{PORT}...")
    conn, addr = s.accept()

    with conn:
        print(f"Conectado por {addr}")

        method, cores, level = recieve_metadata(conn)

        print("Método:", method)
        print("Qtde Núcleos:", cores)
        print("Level Paralelização:", level)

        genomasRecebidos = []
        for genomas in receive_strings(conn):
            genomasRecebidos.append(genomas)
        
        genomas_processados = []

        start_time = time.time()

        if(method == "OpenMP"):
            genomas_processados = processarParalelamenteOpenMP(genomasRecebidos, cores)
        elif(method == "Threads"):
            genomas_processados = processarParalelamenteThread(genomasRecebidos, cores)

        end_time = time.time()
        processing_time = end_time - start_time

        if genomas_processados:
            print("Genomas processados:", len(genomas_processados))

            # Envio dados processados para client
            conn.send(struct.pack('!d', processing_time))

            for genoma in genomas_processados:
                conn.send(len(genoma).to_bytes(4, 'big'))
                conn.send(genoma.encode('utf-8'))
