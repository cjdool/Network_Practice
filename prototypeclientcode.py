from socket import *

serverIP = 'localhost'
serverPort = 10080

'''
TCP Case
'''
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverIP, serverPort))

msg = input('Input lowercase sentence: ')
clientSocket.send(msg.encode())

newMsg = clientSocket.recv(1024)
newMsg = newMsg.decode()
print('From Server:', newMsg)
clientSocket.close()

'''
UDP Case

clientSocket = socket(AF_INET, SOCK_DGRAM)
msg = input('Input lowercase sentence: ')
clientSocket.sendto(msg.encode(),(serverIP, serverPort))

newMsg, serveraddr = clientSocket.recvfrom(2048)
print(newMsg.decode())
clientSocket.close()
'''