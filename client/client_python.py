from socket import *
from select import select
import sys

HOST = '192.168.0.12'
PORT = 9898
BUFSIZE = 1024
ADDR = (HOST, PORT)

cli_sock = socket(AF_INET, SOCK_STREAM)

try:
	cli_sock.connect(ADDR)
except Exception as e:
	print ('Can not connect server (%s:%s)' % ADDR)
	sys.exit()

print ('Connected ....with (%s:%s)' % ADDR)

def prompt():
	sys.stdout.write('[Master] : ')
	sys.stdout.flush()
def recv_prompt():
	sys.stdout.write('[Received] : ')
	sys.stdout.flush()


cli_sock.send('[[Master]]')
while True:
	try:
		connection_list = [sys.stdin, cli_sock]

		rd_sock, wr_sock, err_sock = select(connection_list,[],[],10)

		for sock in rd_sock:
			if sock == cli_sock:
				data = sock.recv(BUFSIZE)
				if not data:
					cli_sock.close()
					sys.exit()
				else:
					
					print('Recv : %s' % data)
					prompt()

			else:
				message = sys.stdin.readline()
				cli_sock.send(message)
				prompt()

	except KeyboardInterrupt:
		cli_sock.close()
		sys.exit()
