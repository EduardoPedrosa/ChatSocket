#!/usr/bin/python3

#---------------------------------------------------------#
# Implementacao de Chat utilizando conexoes TCP. Um lado  #
# comporta-se como cliente e outro como servidor. Este eh #
# o lado cliente.                                         #
#---------------------------------------------------------#

import socket
import threading
import sys

class Cliente():
    def __init__(self, host, port, nome):
        ## Criacao do socket para comunicacao
        self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_tcp.connect((str(host), int(port)))
        self.socket_tcp.send(nome.encode())

        receber = threading.Thread(target=self.receberMensagens)
        receber.daemon = True
        receber.start()

        while True:
            msg = input(nome+": ")

            if msg == "EXIT":
                print ("Fim de chat")
                self.socket_tcp.close()
                sys.exit()
            else:
                self.socket_tcp.send(msg.encode())
	
    def receberMensagens(self):
        while True:
            try:
                dados = self.socket_tcp.recv(1024)
                if dados:
                    print(dados.decode())
            except:
                pass

ipHost = input("IP DO SERVIDOR: ")
nome = input("Nome de usuario: ")
c = Cliente(ipHost, 4000, nome)