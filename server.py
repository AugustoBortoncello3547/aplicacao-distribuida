import socket
from numba import njit
from numba.openmp import openmp_context as openmp
from numba.openmp import omp_get_wtime, omp_get_thread_num, omp_get_num_threads,omp_set_num_threads
from numba.typed import List

import threading
from mpi4py import MPI

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
    steps = len(genomasRecebidos)
    genomas_processados = List()

    def processar_thread(start, end):
        for i in range(start, end):
            seq = genomasRecebidos[i]
            complemento_inverso_seq = processar_sequencia(seq)
            genomas_processados.append(complemento_inverso_seq)

    threads = []
    batch_size = steps // cores

    for i in range(cores):
        start = i * batch_size
        end = (i + 1) * batch_size if i < cores - 1 else steps
        thread = threading.Thread(target=processar_thread, args=(start, end))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return genomas_processados

def processarParalelamenteMpi(genomasRecebidos, cores):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    steps = len(genomasRecebidos)
    genomas_processados = List()

    # Distribuir as tarefas entre os processos
    chunk_size = steps // size
    start = rank * chunk_size
    end = (rank + 1) * chunk_size if rank < size - 1 else steps

    local_genomas = genomasRecebidos[start:end]

    # Processar localmente
    local_genomas_processados = [processar_sequencia(seq) for seq in local_genomas]

    # Juntar os resultados de todos os processos
    genomas_processados = comm.gather(local_genomas_processados, root=0)

    if rank == 0:
        # Apenas o processo mestre retorna os genomas processados
        return [item for sublist in genomas_processados for item in sublist]
    else:
        return None

def processarEmSerie(genomasRecebidos):
    genomas_processados = List()
    steps = len(genomasRecebidos)

    for i in range(steps):
        seq = genomasRecebidos[i]
        complemento_inverso_seq = processar_sequencia(seq)
        genomas_processados.append(complemento_inverso_seq)

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

HOST = 'localhost'
PORT = 12343

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
        while True:
            parte_dados = conn.recv(1024)
            if not parte_dados:
                break
            seq = parte_dados.decode('utf-8')
            if "final" in seq:
                seq = seq.replace("final", "")
                genomasRecebidos += seq
                break
            genomasRecebidos += seq

        print("Genomas recebidos:", len(genomasRecebidos))
        
        genomas_processados = []

        start_time = time.time()

        if(method == "OpenMP"):
            genomas_processados = processarParalelamenteOpenMP(genomasRecebidos, cores)
        elif(method == "Thread"):
            genomas_processados = processarParalelamenteThread(genomasRecebidos, cores)
        elif(method == "MPI"):
            genomas_processados = processarParalelamenteMpi(genomasRecebidos, cores)
        elif(method == "Serial"):
            genomas_processados = processarEmSerie(genomasRecebidos)

        end_time = time.time()
        processing_time = end_time - start_time

        print("\nTempo processamento:", processing_time)
        print("Genomas processados:", len(genomas_processados))

        print("\nPrimeiros genomas recebidos:", genomasRecebidos[0:10])
        print("Primeiros genomas processados:", genomas_processados[0:10])

        if genomas_processados:
            # Envio dados processados para client
            conn.send(str(processing_time).encode("utf-8"))

            for genoma in genomas_processados:
                conn.send(len(genoma).to_bytes(1024, 'big'))
                conn.send(genoma.encode('utf-8'))
