#!/usr/bin/python3

#---------------------------------------------------------#
# Implementacao de Chat utilizando conexoes TCP. Um lado  #
# comporta-se como cliente e outro como servidor. Este eh #
# o lado servidor.                                        #
#---------------------------------------------------------#
import socket
import threading
import sys
import select
import os

class Servidor():
    def __init__(self, host="localhost", port=4000):
        self.listaConectados = [] #lista de sockets conectados
        self.registroClientes = {} #registro de clientes, sendo que a chave é uma tupla de (ip,porta) e o valor o nome do cliente
        self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_tcp.bind((str(host), int(port)))
        self.socket_tcp.listen(5) #numero maximo de conexoes permitidas 
        self.socket_tcp.settimeout(2) #tempo maximo de espera
        self.socket_tcp.setblocking(False) #em caso de nao ter dados lidos nao bloqueia o socket, mas lanca um erro
        print ("\33[31m\33[1mDigite EXIT a qualquer momento para encerrar o servidor\n")
        print ("\33[32m \t\t\t\tSERVIDOR ONLINE \33[0m\n")
        self.listaConectados.append(self.socket_tcp) #coloca o servidor na lista de sockets conectados
        aceitarOuEnviar = threading.Thread(target=self.aceitarOuEnviar) 

        aceitarOuEnviar.daemon = True #garante que quando sair o processo e destruido
        aceitarOuEnviar.start()

        while True:
            msg = input()
            if msg == 'EXIT': #caso o servidor receba EXIT, fecha a conexao e o programa
                self.socket_tcp.close()
                sys.exit()
            else:
                pass
	
    def aceitarOuEnviar(self): #thread para tanto aceitar novas conexoes quanto para encaminhar mensagens broadcast para todos os clientes exceto o que enviou
        while True:
            rList,wList,error_sockets = select.select(self.listaConectados,[],[]) #retorna em rList todos os sockets que estao prontos para serem lidos
            for c in rList:
                if(c == self.socket_tcp): #se c for igual a socket_tcp significa que o destino é o proprio servidor, ou seja, alguem pretende se conectar
                    conn, addr = self.socket_tcp.accept() #aceita a conexao
                    nome = str(conn.recv(1024).decode()) #recebe o nome do cliente
                    self.registroClientes[addr] = ""
                    if nome in self.registroClientes.values(): #se o nome ja está cadastrado avisa o usuario e nao conecta
                        conn.send("\r\33[31m\33[1m Nome de usuario já existente! Escreva EXIT para sair e tente conectar de novo\n\33[0m".encode())
                        del self.registroClientes[addr]
                        conn.close()
                        continue
                    else: #caso o nome não esteja cadastrado adiciona na lista de conectados e no dicionario de clientes
                        self.registroClientes[addr] = nome 
                        self.listaConectados.append(conn)
                        print("Cliente (%s, %s) conectado" % addr, " [",self.registroClientes[addr],"]")
                        conn.send(("\33[32m\r\33[1m Bem vindo ao chat "+ nome +". Digite 'EXIT' a qualquer momento para sair\n\33[0m").encode()) #envia para o cliente que acabou de se conectar as mensagens de boas vindas
                        self.enviarBroadcast("\33[32m\33[1m\r "+nome+" juntou-se ao chat \n\33[0m", conn) #avisa a todos que o cliente se conectou, exceto ele mesmo            
                else: #trata mensagens vindo de algum usuario
                    try:
                        data1 = str(c.recv(1024).decode()) #recebe e decodifica mensagem
                        data = data1[:data1.index("\n")] #retorna todos os caracteres de 0 ate encontrar o primeiro caractere de fim de linha \n
                        i,p = c.getpeername() #retorna o ip e a porta separadamente do socket c
                        if (data == "EXIT"): #se o cliente quer se desconectar
                            msg="\r\33[1m"+"\33[31m "+self.registroClientes[(i,p)]+" saiu da conversa \33[0m\n"
                            self.enviarBroadcast(msg,c) #avisa para todos que ele se desconectou
                            print ("Cliente (%s, %s) esta offline" % (i,p)," [",self.registroClientes[(i,p)],"]")
                            del self.registroClientes[(i,p)] #remove do dicionario de clientes para permitir que o mesmo nome seja usado
                            self.listaConectados.remove(c) #remove da lista de conectados
                            c.close() #fecha conexao
                            continue
                        else:
                            msg="\r\33[1m"+"\33[35m "+self.registroClientes[(i,p)]+": "+"\33[0m"+data+"  \n"
                            self.enviarBroadcast(msg,c) #encaminha a mensagem para todos, junto com o nome de quem enviou
                    #abrupt user exit
                    except:
                        (i,p)=c.getpeername() #retorna o ip e a porta separadamente do socket c
                        self.enviarBroadcast("\r\33[31m \33[1m"+self.registroClientes[(i,p)]+" saiu da conversa inesperadamente\33[0m\n",c) #avisa para todos que ele se desconectou inesperadamente
                        print ("Cliente (%s, %s) esta offline (erro)" % (i,p)," [",self.registroClientes[(i,p)],"]\n") #imprime no servidor que o cliente esta desconectado
                        del self.registroClientes[(i,p)] #remove do dicionario de clientes para permitir que o mesmo nome seja usado
                        self.listaConectados.remove(c) #remove da lista de conectados
                        c.close() #fecha conexao
                        continue

    def enviarBroadcast(self, mensagem, cliente): #responsavel para encaminhar a mensagem para todos os clientes exceto o que enviou a mensagem
        i, p = cliente.getpeername() #retorna o ip e a porta separadamente do socket ciente
        for c in self.listaConectados:
            if((c != cliente) and (c != self.socket_tcp)): #se c for diferente do cliente que enviou a mensagem e diferente do socket do proprio servidor
                try:
                    c.send(mensagem.encode()) #envia mensagem codificada
                except: #significa que este socket ja nao esta mais conectado
                    ip, port = c.getpeername() #retorna o ip e a porta separadamente do socket c
                    self.listaConectados.remove(c) #remove da lista de conectados
                    del self.registroClientes[(ip,port)] #remove do dicionario de clientes para permitir que o mesmo nome seja usado
                    c.close() #fecha a conexao

os.system('clear')
s = Servidor()