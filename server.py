import socket  
import Queue  
from select import select  
import sys

class PRINT_COLOR:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    OKCONTENT = '\033[37m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Server(object):

      
    def __init__(self):
        self.message_queue = {}  
        self.nicknames = {}
        self.input_list = []  
        self.output_list = []

    def get_server(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname) 
        return (ip, 8000)  
        
    def run(self,server_ip = None):
        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        if not server_ip:
            server_ip = self.get_server()    
        server.bind(server_ip)  
        server.listen(10)  
        server.setblocking(False)  

        self.input_list.append(server)  

        while True:  
            stdinput, stdoutput, stderr = select(self.input_list, self.output_list, self.input_list)  
 
            for obj in stdinput:  
                if obj == server:  
                    conn, addr = server.accept()  
                    print("Client {0} connected! ".format(addr))   
                    self.input_list.append(conn)  
                    self.message_queue[conn] = Queue.Queue()  
                    if conn not in self.output_list:  
                        self.output_list.append(conn)
                else:      
                    try:       
                        recv_data = obj.recv(1024)  
                        if not self.nicknames.has_key(obj):
                           self.nicknames[obj] = recv_data
                           print("{0} login! ".format(self.nicknames[obj]))  
                           continue
                        if recv_data:  
                            print("received {0} from client {1}".format(recv_data.decode(), self.nicknames[obj]))  
                            for key in self.message_queue:
                                if key == obj:continue
                                self.message_queue[key].put(
                                    PRINT_COLOR.OKBLUE + self.nicknames[obj] + ':\n' + PRINT_COLOR.ENDC + 
                                    PRINT_COLOR.OKCONTENT + recv_data + '\n' + PRINT_COLOR.ENDC
                                    )        
                    except Exception as ex:  
                        self.input_list.remove(obj)  
                        if self.message_queue.has_key(obj):del self.message_queue[obj] 
                        print("\n[input] Client  {0} disconnected".format(obj)) 
                        print ex 

            for sendobj in stdoutput:  
                try:  
                    if not self.message_queue[sendobj].empty():     
                        mess = self.message_queue[sendobj].get()
                        print("send data {0}".format(mess)) 
                        sendobj.sendall(mess)  
                except Exception as ex:  
                    if self.message_queue.has_key(sendobj): del self.message_queue[sendobj]  
                    self.output_list.remove(sendobj)  
                    print("\n[output] Client  {0} disconnected".format(sendobj))  

            for error_socket in stderr:
                self.input_list.remove(error_socket)

if __name__ == "__main__":  
    
    server = Server()
    server.run()