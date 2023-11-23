# aplicacao-distribuida

OBS: Para o trabalho, utilizamos um VM com o Linux Lubuntu com 4 cores configurada.

# Pacotes

Pacotes instalados normalmente pelo pip:

threading, panda

# Instalação MPI:

https://ava.ucs.br/courses/35878/pages/tutorial-para-criacao-do-cluster-mpi?module_item_id=1203822

https://ava.ucs.br/courses/35878/pages/instalacao-do-mpi-no-python-mpi4py?module_item_id=1213699

Obs: para uma das máquinas que realizamos o teste o MPI retornou um erro para o List, exigindo o seguinte import no topo do server:

from typing import List

# Instalação PyOMP

https://ava.ucs.br/courses/35878/pages/passos-para-instalacao-pyomp-na-vm?module_item_id=1200030

# Rodar a aplicação

Primeiro iniciar o servidor: python3 ./server.py

Segundo iniciar o client: python3 ./client.py

Preencher todas informações que o client pedir

Obs: na máquina da UCS estava acontecendo aquele mesmo problema dos endereços não fecharem a conexão no final, então talvez tenha que mudar a porta ao rodar novamente ou botar o sleep. Caso isso não ocorra, como nas nossas máquinas desconsiderar esse parágrafo
