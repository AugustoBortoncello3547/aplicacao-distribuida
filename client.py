import socket
import pandas as pd

import struct
import time

df = pd.read_csv("dados.csv", delimiter="\t")
valores = df["intergenicregion_sequence"].astype(str).tolist()

#print(valores)

# Configurações do cliente
HOST = 'localhost'
PORT = 12345

def input_data():
    # Solicita ao usuário escolher um método de paralelização
    print("Escolha um método de paralelização:")
    print("1. OpenMP")
    print("2. Thread")
    print("3. MPI")
    print("4. Serial")
    choice = input("Digite o número correspondente ao método desejado: ")

    if choice == "1":
        method = "OpenMP"
    elif choice == "2":
        method = "Thread"
    elif choice == "3":
        method = "MPI"
    elif choice == "4":
        method = "Serial"
    else:
        print("Opção inválida. Escolha um método válido.")
        exit()

    # Solicita ao usuário escolher a quantidade de núcleos/nós utilizados
    cores = input("Digite a quantidade de núcleos/nós a serem utilizados: ")

    # Solicita ao usuário escolher o nível de paralelização
    print("Escolha um nível de paralelização:")
    print("1. CPU")
    choice = input("Digite o número correspondente ao nível de paralelização desejado: ")

    if choice == "1":
        level = "CPU"
    else:
        print("Opção inválida. Escolha um nível de paralelização válido.")
        exit()
    
    return method, cores, level

def receive_strings(client_socket):
    while True:
        try:
            string = client_socket.recv(2018).decode('utf-8')
            if "final" in string:
                break
            yield string
        except ConnectionResetError:
            break

method, cores, level = input_data()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # Método de paralelização (OpenCL, MPI, OpenMP, etc)
    s.send(len(method).to_bytes(4, 'big'))
    s.send(method.encode('utf-8'))

    # Quantidade de núcleos/nós utilizados
    s.send(int(cores).to_bytes(4, 'big'))

    # Nível de paralelização (CPU, GPU, distribuído, etc)
    s.send(len(level).to_bytes(4, 'big'))
    s.send(level.encode('utf-8'))

    s.sendall('\n'.join(valores).encode('utf-8'))

    s.send("final".encode('utf-8'))

    print("\nEsperando resposta do servidor\n")

    # Receber resposta do server
    processing_time = s.recv(1024).decode("utf-8")
    
    genomasProcessados = []
    for genomas in receive_strings(s):
        genomasProcessados.append(genomas)

    print("Tempo processamento:", processing_time)
    print("Genomas processados:", len(genomasProcessados))

    s.close()

print("Conexão finalizada com sucesso.")
