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
        self.socket_tcp.setblocking(False)

        print ("\33[32m \t\t\t\tSERVIDOR ONLINE \33[0m")

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
                nome = str(conn.recv(1024).decode())
                self.registroClientes[addr] = ""
                if nome in self.registroClientes.values():
                    conn.send("\r\33[31m\33[1m Nome de usuario já existente! Escreva EXIT para sair e tente conectar de novo\n\33[0m".encode())
                    del self.registroClientes[addr]
                    conn.close()
                else:
                    self.registroClientes[addr] = nome
                    conn.setblocking(False)
                    self.listaConectados.append(conn)
                    print("Cliente (%s, %s) conectado" % addr, " [",self.registroClientes[addr],"]")
                    conn.send("\33[32m\r\33[1m Bem vindo ao chat. Digite 'EXIT' a qualquer momento para sair\n\33[0m".encode())
                    self.enviarBroadcast(("\33[32m\33[1m\r "+nome+" juntou-se ao chat \n\33[0m"), conn)            
            except:
                pass

    def enviarBroadcast(self, mensagem, cliente):
        i, p = cliente.getpeername()
        for c in self.listaConectados:
            try:
                if c != cliente:
                    c.send(mensagem.encode())
            except:
                self.listaConectados.remove(c)
                ip, port = c.getpeername()
                del self.registroClientes[(ip,port)]

    def enviarMensagens(self):
        while True:
            rList,wList,error_sockets = select.select(self.listaConectados,[],[])
            for c in rList:
                    try:
                        data = str(c.recv(1024).decode())
                        if(data):
                            i,p = c.getpeername()
                            if data == "EXIT":
                                msg="\r\33[1m"+"\33[31m "+self.registroClientes[(i,p)]+" saiu da conversa \33[0m\n"
                                enviarBroadcast(c,msg)
                                print ("Cliente (%s, %s) esta offline" % (i,p)," [",self.registroClientes[(i,p)],"]")
                                del self.registroClientes[(i,p)]
                                self.listaConectados.remove(c)
                                c.close()
                                continue

                            else:
                                msg="\r\33[1m"+"\33[35m "+self.registroClientes[(i,p)]+": "+"\33[0m"+data+"\n"
                                enviarBroadcast(c,msg)
                        
                    #abrupt user exit
                    except:
                        (i,p)=c.getpeername()
                        self.enviarBroadcast("\r\33[31m \33[1m"+self.registroClientes[(i,p)]+" saiu da conversa inesperadamente\33[0m\n",c)
                        print ("Cliente (%s, %s) esta offline (erro)" % (i,p)," [",self.registroClientes[(i,p)],"]\n")
                        del self.registroClientes[(i,p)]
                        self.listaConectados.remove(c)
                        c.close()
                        continue

s = Servidor()