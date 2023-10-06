from socket import *

def ipcheck():
    return gethostbyname(gethostname())

serverIP = 'localhost'
serverPort = 10080
maxlisten = 5

'''
TCP Case
'''
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverIP, serverPort))
serverSocket.listen(maxlisten) # maximum listen
print('The TCP Server is ready to receive.')
print('IP Address is', ipcheck())

while True:
    print('accept wait')
    connectionSocket, clientaddr = serverSocket.accept()

    try:
        msg = connectionSocket.recv(1024) # accept raw data
        msg = msg.decode() # decode raw data
        newMsg = msg.upper()
        connectionSocket.send(newMsg.encode())
    except Exception as err:
        # error handling mechansim
        print('error occur', err)
        break
    finally:
        connectionSocket.close()

'''
UDP Case

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((serverIP, serverPort))
print('The UDP server is ready to receive')

while True:
    message, clientaddr = serverSocket.recvfrom(2048)
    newMsg = message.decode().upper()
    serverSocket.sendto(newMsg.encode(), clientaddr)
'''