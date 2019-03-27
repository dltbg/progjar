import socket
import sys
import os
import time
import threading
import glob
import json

class ClientHandler(threading.Thread):
	def __init__(self, connection, address):
		self.connection = connection
		self.address = address
		threading.Thread.__init__(self)

	def _dirc_command(self, request):
		response = {}
		list_ = glob.glob(request['dir']+'*')
		response['list_'] = map(
			lambda file_name : {'name':file_name, 'is_file' : os.path.isfile(request['dir']+file_name)},
			list_
		)
		self.connection.sendall(json.dumps(response))

	def _put_command(self, request):
		max_size = request['file_size']
		recv_ = 0
		fd = open(request['path'], 'wb+', 0)
		self.connection.sendall('--READY--')
		while recv_ < max_size:
			data = self.connection.recv(1024)
			recv_ += len(data)
			fd.write(data)

		fd.close()
		print('File Diterima')

	def _get_command(self, request):
		fd = open(request['path'], 'rb')
		response = {}
		response['file_size'] = os.path.getsize(request['path'])
		self.connection.sendall(json.dumps(response))
		for data in fd:
			self.connection.sendall(data)
		fd.close()

	def _mkdir_command(self, request):
		try:
			os.mkdir(request['path'])
			self.connection.sendall('Direktori Berhasil Dibuat')
		except:
			self.connection.sendall('Error!')

	def run(self):
		while True:
			data = self.connection.recv(1024)
			request = json.loads(data)
			print(request)
			cmd = request['command']

			if cmd == 'dirc':
				self._dirc_command(request)
			elif cmd == 'put':
				self._put_command(request)
			elif cmd == 'get':
				self._get_command(request)
			elif cmd == 'mkdir':
				self._mkdir_command(request)

class Server(threading.Thread):
	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind(('127.0.0.1', 10000))
		print('Server Run')
		threading.Thread.__init__(self)

	def run(self):
		self.sock.listen(1)
		while True:
			conn, address = self.sock.accept()
			print('Client Accepted > '+str(address))
			ClientHandler(conn, address).start()


if __name__=="__main__":
	Server().start()
