#!/usr/bin/python3

#---------------------------------------------------------#
# Implementacao de Chat utilizando conexoes TCP. Um lado  #
# comporta-se como cliente e outro como servidor. Este eh #
# o lado cliente.                                         #
#---------------------------------------------------------#

import socket
import threading
import sys
import os
import select

class Cliente():
    def __init__(self, host, port, nome):
        ## Criacao do socket para comunicacao
        self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket_tcp.connect((str(host), int(port)))
        except :
            print ("\33[31m\33[1m Nao foi possivel conectar ao servidor \33[0m")
            sys.exit()

        self.socket_tcp.send(nome.encode())

        receber = threading.Thread(target=self.receberMensagens)
        receber.daemon = True
        receber.start()

        while True:
            self.display()
            msg = sys.stdin.readline()
            self.socket_tcp.send(msg.encode())
	
    def display(self) :
        you="\33[33m\33[1m"+" Voce: "+"\33[0m"
        sys.stdout.write(you)
        sys.stdout.flush()

    def receberMensagens(self):
        while True:
            data = self.socket_tcp.recv(1024)
            if(data):
                sys.stdout.write(str(data.decode()))
                self.display()
ipHost = input("IP DO SERVIDOR: ")
nome = input("Nome de usuario: ")
os.system('clear')
c = Cliente(ipHost, 4000, nome)