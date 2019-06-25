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

class Cliente():
    def __init__(self, host, port, nome):
        ## Criacao do socket para comunicacao
        self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try: #tenta conectar, caso nao consiga imprime a mensagem e fecha o programa no terminal
            self.socket_tcp.connect((str(host), int(port)))
        except :
            print ("\33[31m\33[1m Nao foi possivel conectar ao servidor \33[0m")
            sys.exit()

        self.socket_tcp.send(nome.encode()) #envia o nome do cliente para fazer a conexao

        receber = threading.Thread(target=self.receberMensagens) 
        receber.daemon = True #garante que quando sair o processo e destruido
        receber.start()

        while True: 
            self.display() 
            msg = sys.stdin.readline()
            if(msg != "\n"): #caso o usuario digite algo, ou seja, nao pode ter um unico caractere lido, que e o proprio fim de linha
                self.socket_tcp.send(msg.encode()) #envia mensagem codificada em bytes
                if(msg.strip() == "EXIT"): #caso a mensagem seja EXIT termina o programa no terminal
                    sys.exit()
	
    def display(self) : #mostra a interface indicando que é voce que esta digitando
        you="\33[33m\33[1m"+" Voce: "+"\33[0m"
        sys.stdout.write(you)
        sys.stdout.flush() #garante que o terminal vai escrever mesmo antes de pular de linha

    def receberMensagens(self): #thread responsavel por receber mensagens de outras pessoas
        while True:
            data = self.socket_tcp.recv(1024) #recebe dados a partir do socket com o servidor
            if(data): #se os dados forem validos ou se haverem dados
                sys.stdout.write(str(data.decode())) #escreve os dados na tela decodificados
                self.display()
ipHost = input("IP DO SERVIDOR: ")
nome = input("Nome de usuario: ")
os.system('clear')
c = Cliente(ipHost, 4000, nome) #porta padrao setada como 4000