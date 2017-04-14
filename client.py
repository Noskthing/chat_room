import socket
from select import select  
import sys
import threading
import Queue


def add_input(input_queue):
	while True:
		input_queue.put(sys.stdin.readline())
		


class Client(object):
	 
	def __init__(self):
		self.nicknames = {}
		self.input_list = []   
		self.output_list = [] 

		self.input_queue = Queue.Queue()

	def get_server(self):
		hostname = socket.gethostname()
		ip = socket.gethostbyname(hostname) 
		return (ip, 8000) 

	def run(self,server_ip = None):
		client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		if not server_ip:
			server_ip = self.get_server()
		client.connect(server_ip)

		self.output_list.append(client)
		self.input_list.append(client)

		cmd = raw_input("Please input your nickname:")
		client.sendall(cmd)
		
		input_thread = threading.Thread(target=add_input, args=(self.input_queue,))
		input_thread.daemon = True
		input_thread.start()  

		while True:
			stdinput, stdoutput, stderr = select(self.input_list, self.output_list, self.input_list)

			for obj in stdinput:  
				try:
					recv_data = obj.recv(1024)
					if recv_data:
						print recv_data
				except Exception, e:
					print 'error'

			for sendobj in stdoutput:  
				try:
					if not self.input_queue.empty():
						mess =  self.input_queue.get().strip('\n')
						sendobj.sendall(mess)
				except Exception as ex:  
					self.output_list.remove(sendobj)  
					print("\n[output] Client  {0} disconnected".format(sendobj))
					print ex

if __name__ == '__main__':

	client = Client()
	client.run()


	

	



	

	