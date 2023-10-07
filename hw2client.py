from socket import *
import os
import threading


def handle_recving(sock):
    while True:
        if done:
            break
        msg = sock.recv(1024).decode()
        if msg.startswith('[Notice]'):  # notice case
            print(msg)
        elif msg.startswith('[Global]'):  # global file list case
            partmsg = msg.split('\n')
            partmsg = partmsg[1:]
            for g in partmsg:
                print(g)
        elif msg.startswith('[Request]'):  # file download case
            with cond:
                if msg == '[Request] Not available file':
                    print(msg)
                    cond.notify()
                    continue
            filename = msg.split(']')[1]
            file_path = os.path.join('./', filename)
            with cond:
                with open(file_path, 'wb') as bfile:
                    print("Download start")
                    while True:
                        pkt = sock.recv(1024)
                        if not pkt:
                            break
                        bfile.write(pkt)
                    print("Download end")
                cond.notify()
            print("{} has been downloaded".format(filename))
        elif msg.startswith('[Relay]'):  # file upload case
            filename = msg.split(']')[1]
            file_path = os.path.join('./', filename)
            sock.send("5".encode())
            with open(file_path, 'rb') as bfile:
                body = bfile.read()
                print("Upload start")
                sock.sendall(body)
                print("Upload end")
        else:
            if msg == "Notified RelayServer\nGoodbye!":
                print(msg)
            else:
                print('Not Available recving type')


serverPort = 10080
cond = threading.Condition()

'''
TCP Case
'''
id = input('Enter UserID: ')
serverIP = input('Enter RelayServerIP address: ')
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverIP, serverPort))
clientSocket.send(id.encode())
notice = clientSocket.recv(1024).decode()
print(notice)

done = False
t = threading.Thread(target=handle_recving, args=(clientSocket,))
t.start()

while True:
    op = input()
    if op == '0':
        print('########################')
        print('1. Register a file')
        print('2. Get the global file list')
        print('3. Download a file')
        print('4. Exit')
        print('########################')
    elif op == '1':
        clientSocket.send(op.encode())
        filename = input('which file to register? ')
        clientSocket.send(filename.encode())
    elif op == '2':
        clientSocket.send(op.encode())
        print('The global file list is as follows:')
    elif op == '3':
        clientSocket.send(op.encode())
        filename = input('which file to download? ')
        clientSocket.send(filename.encode())
        with cond:
            print('Waiting for file download')
            cond.wait()
            print('Waiting Done')
    elif op == '4':
        clientSocket.send(op.encode())
        done = True
        break
    else:
        print('Wrong option')

t.join()
clientSocket.close()
