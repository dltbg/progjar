import socket
import json
import os
import threading

class Client(threading.Thread):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_addr = ('127.0.0.1', 10000)
        self.sock.connect(server_addr)
        print('Terhubung ke -> '+str(server_addr))
        self.r_path = RelativePath()
        threading.Thread.__init__(self)


    def _dirc_command(self):
        request = {}
        request['command'] = 'dirc'
        request['dir'] = self.r_path.get_dir()

        self.sock.sendall(json.dumps(request))
        resp = self.sock.recv(1024)
        data = json.loads(resp)

        dir_list = data['list_']
        print(self.r_path.get_dir()+' > ')
        for dir in dir_list:
            dir_type = ''
            if dir['is_file']:
                dir_type = 'file'
            else :
                dir_type = 'folder'

            print('-> '+dir['name'] + '     [{}]'.format(dir_type))


    def _put_command(self, file_name):
        path = self.r_path.get_dir()+file_name
        fd = open(file_name, 'rb')
        request = {}
        request['command'] = 'put'
        request['path'] = path
        request['file_size'] = os.path.getsize(file_name)
        self.sock.sendall(json.dumps(request))
        resp = self.sock.recv(1024)
        if resp == '--READY--':
            for data in fd:
                self.sock.sendall(data)

        self.sock.send(bytes('--END--'))
        print('File Terkirim!')


    def _get_command(self, file_name):
        request = {}
        request['command'] = 'get'
        request['path'] = self.r_path.get_dir() + file_name
        self.sock.sendall(json.dumps(request))
        fd = open(file_name, 'wb+', 0)
        resp = self.sock.recv(1024)
        data = json.loads(resp)
        if data['file_size'] is not None:
            max_size = data['file_size']
            recv_ = 0
            while recv_ < max_size:
                data = self.sock.recv(1024)
                recv_ += len(data)
                fd.write(data)
        fd.close()
        print('File Terdownload!')


    def _mkdir_command(self, dir_name):
        request = {}
        request['command'] = 'mkdir'
        request['path'] = self.r_path.get_dir() + dir_name
        self.sock.sendall(json.dumps(request))
        resp = self.sock.recv(1024)
        print(resp)


    def run(self):
        while True:
            commands = raw_input().split(' ')
            command = commands[0]

            if command == 'dirc':
                self._dirc_command()
            elif command == 'cd':
                cd_path = commands[1]
                self.r_path.cd(cd_path)
                print(self.r_path.get_dir())
            elif command == 'put':
                self._put_command(commands[1])
            elif command == 'get':
                self._get_command(commands[1])
            elif command == 'mkdir':
                self._mkdir_command(commands[1])


class RelativePath:
    def __init__(self):
        self.current_dir = ''

    def get_dir(self):
        return self.current_dir

    def _get_array_dir(self):
        return self.current_dir.split('/')

    def cd(self, dir):
        if dir == '..':
            array_dir = self._get_array_dir()
            self.current_dir = ''

            a_len = len(array_dir)

            for i in range(0, a_len-2):
                print('concat : '+array_dir[i])
                self.current_dir += array_dir[i]
                self.current_dir += '/'

        elif self.current_dir == '':
            self.current_dir = dir + '/'
        else:
            self.current_dir += dir + '/'


if __name__=="__main__":
    Client().start()
