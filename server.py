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

class Servidor():
    def __init__(self, host="localhost", port=4000):
        self.listaConectados = []
        self.registroClientes = {}
        self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_tcp.bind((str(host), int(port)))
        self.socket_tcp.listen(5)
        self.socket_tcp.settimeout(2)
        self.socket_tcp.setblocking(False)

        print ("\33[32m \t\t\t\tSERVIDOR ONLINE \33[0m")
        self.listaConectados.append(self.socket_tcp)
        aceitarOuEnviar = threading.Thread(target=self.aceitarOuEnviar)

        aceitarOuEnviar.daemon = True
        aceitarOuEnviar.start()

        while True:
            msg = input('=>')
            if msg == 'EXIT':
                self.socket_tcp.close()
                sys.exit()
            else:
                pass
	
    def aceitarOuEnviar(self):
        while True:
            rList,wList,error_sockets = select.select(self.listaConectados,[],[])
            for c in rList:
                if(c == self.socket_tcp):
                    conn, addr = self.socket_tcp.accept()
                    nome = str(conn.recv(1024).decode())
                    self.registroClientes[addr] = ""
                    if nome in self.registroClientes.values():
                        conn.send("\r\33[31m\33[1m Nome de usuario já existente! Escreva EXIT para sair e tente conectar de novo\n\33[0m".encode())
                        del self.registroClientes[addr]
                        conn.close()
                        continue
                    else:
                        self.registroClientes[addr] = nome
                        self.listaConectados.append(conn)
                        print("Cliente (%s, %s) conectado" % addr, " [",self.registroClientes[addr],"]")
                        conn.send(("\33[32m\r\33[1m Bem vindo ao chat. Digite 'EXIT' a qualquer momento para sair\n\33[0m").encode())
                        self.enviarBroadcast("\33[32m\33[1m\r "+nome+" juntou-se ao chat \n\33[0m", conn)            
                else: #mensagem vindo de algum usuario
                    try:
                        data1 = str(c.recv(1024).decode())
                        data = data1[:data1.index("\n")]
                        i,p = c.getpeername()
                        if (data == "EXIT"):
                            msg="\r\33[1m"+"\33[31m "+self.registroClientes[(i,p)]+" saiu da conversa \33[0m\n"
                            self.enviarBroadcast(msg,c)
                            print ("Cliente (%s, %s) esta offline" % (i,p)," [",self.registroClientes[(i,p)],"]")
                            del self.registroClientes[(i,p)]
                            self.listaConectados.remove(c)
                            c.close()
                            continue
                        else:
                            msg="\r\33[1m"+"\33[35m "+self.registroClientes[(i,p)]+": "+"\33[0m"+data+"  \n"
                            self.enviarBroadcast(msg,c)
                    #abrupt user exit
                    except:
                        (i,p)=c.getpeername()
                        self.enviarBroadcast("\r\33[31m \33[1m"+self.registroClientes[(i,p)]+" saiu da conversa inesperadamente\33[0m\n",c)
                        print ("Cliente (%s, %s) esta offline (erro)" % (i,p)," [",self.registroClientes[(i,p)],"]\n")
                        del self.registroClientes[(i,p)]
                        self.listaConectados.remove(c)
                        c.close()
                        continue

    def enviarBroadcast(self, mensagem, cliente):
        i, p = cliente.getpeername()
        for c in self.listaConectados:
            if((c != cliente) and (c != self.socket_tcp)):
                try:
                    c.send(mensagem.encode())
                except:
                    ip, port = c.getpeername()
                    self.listaConectados.remove(c)
                    del self.registroClientes[(ip,port)]
                    c.close()
                    

s = Servidor()