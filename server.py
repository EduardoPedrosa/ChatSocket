#!/usr/bin/python3

#---------------------------------------------------------#
# Implementacao de Chat utilizando conexoes TCP. Um lado  #
# comporta-se como cliente e outro como servidor. Este eh #
# o lado servidor.                                        #
#---------------------------------------------------------#
import socket
import threading
import sys


class Servidor():
    def __init__(self, host="localhost", port=4000):
        self.listaConectados = []
        self.registroClientes = {}
        self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_tcp.bind((str(host), int(port)))
        self.socket_tcp.listen(5)
        self.socket_tcp.setblocking(False)

        print ('Servidor ONLINE')

        aceitar = threading.Thread(target=self.aceitarConexao)
        enviar = threading.Thread(target=self.enviarMensagens)

        aceitar.daemon = True
        aceitar.start()

        enviar.daemon = True
        enviar.start()

        while True:
                msg = input('=>')
                if msg == 'EXIT':
                    self.socket_tcp.close()
                    sys.exit()
                else:
                    pass
	
    def aceitarConexao(self):
        while True:
            try:
                conn, addr = self.socket_tcp.accept()
                nome = conn.recv(4096).decode()
                self.registroClientes[addr] = ""
                if nome in self.registroClientes.values():
                    conn.send("\r\33[31m\33[1m Username já existente! Escreva EXIT para sair e tente conectar de novo\n\33[0m".encode())
                    del self.registroClientes[addr]
                    conn.close()
                else:
                    self.registroClientes[addr] = nome
                    conn.setblocking(False)
                    self.listaConectados.append(conn)
                    print("Cliente (%s, %s) conectado" % addr, " [",self.registroClientes[addr],"]")
                    conn.send("\33[32m\r\33[1m Bem vindo ao chat. Digite 'EXIT' a qualquer momento para sair\n\33[0m".encode())
                    self.enviarBroadcast(("\33[32m\33[1m\r "+nome+" juntou-se ao chat \n\33[0m").encode(), conn)
            except:
                pass

    def enviarBroadcast(self, mensagem, cliente):
        i, p = cliente.getpeername()
        for c in self.listaConectados:
            try:
                if c != cliente:
                    envio = self.registroClientes[(i,p)]
                    mensagemEnviada = envio + ": " + mensagem.decode()
                    c.send(mensagemEnviada.encode())
            except:
                self.listaConectados.remove(c)
                del self.registroClientes[addr] 

    def enviarMensagens(self):
        while True:
            if len(self.listaConectados) > 0:
                for c in self.listaConectados:
                    try:
                        dados = c.recv(1024)
                        if dados:
                            self.enviarBroadcast(dados, c)
                    except:
                        pass

s = Servidor()