from socket import *
import threading
import os

serverIP = 'localhost'
serverPort = 10080
maxlisten = 10
threadpool = [{'valid': False} for _ in range(maxlisten)]
gf_lock = threading.Lock()
global_file_list = []


def ipcheck():
    return gethostbyname(gethostname())


def broadcast(notice):
    for th in threadpool:
        if th['valid'] is False:
            break
        th['socket'].send(notice.encode())


def printglobalfile():
    print("The global file list is as follows:")
    with gf_lock:
        for g in global_file_list:
            print(g)


def handle_register_file(id, sock):
    filename = sock.recv(1024).decode()
    nameformat = id + "/" + filename
    if nameformat not in global_file_list:
        with gf_lock:
            global_file_list.append(nameformat)
        printglobalfile()
        broadcast("[Notice] The global file list is updated")


def handle_get_global_filelist(sock):
    msg = "[Global]"
    with gf_lock:
        for gf in global_file_list:
            msg = msg + "\n" + gf
    sock.send(msg.encode())


def handle_download_file(id, sock):
    filename = sock.recv(1024).decode()
    if filename not in global_file_list:
        msg = '[Request] Not available file'
        print(msg)
        sock.send(msg.encode())
        return
    print('[Request] Received the file download request from {} for {}'.format(id, filename))

    srcid = filename.split('/')[0]
    srcfilename = filename.split('/')[1]
    sockobj = None
    for th in threadpool:
        if th['id'] == srcid and th['valid'] is True:
            sockobj = th['obj']
            break
    msg = "[Relay]" + srcfilename
    sockobj.send(msg.encode())
    dir_path = "./" + srcid
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            print("Directory {} is created".format(srcid))
        except OSError as e:
            print("Directory create error: {}".format(e))
    file_path = os.path.join(dir_path, srcfilename)
    with open(file_path, 'wb') as f:
        print("Retrieving started")
        while True:
            pkt = sockobj.recv(1024)
            if not pkt:
                break
            f.write(pkt)
        print('Retrieved {} from {}'.format(srcfilename, srcid))

    msg = "[Request]" + srcfilename
    sock.send(msg.encode())
    with open(file_path, 'rb') as f:
        body = f.read()
        print("Transfer started")
        sock.sendall(body)
        print('The transfer of {} to {} has been completed'.format(srcfilename, id))

    printglobalfile()


def handle_exit(sock, id):
    print("{} has left".format(id))
    exitnotice = "Notified RelayServer\nGoodbye!"
    sock.send(exitnotice.encode())
    broadcast("[Notice] {} has left".format(id))
    with gf_lock:
        for gf in global_file_list[:]:
            if gf.startswith(id):
                global_file_list.remove(gf)
    broadcast("[Notice] The global file list is updated")
    printglobalfile()


def socket_handling(csocket, mytid):
    id = csocket.recv(1024).decode()
    print("{} is connected".format(id))
    broadcast("[Notice] Welcome {}".format(id))
    threadpool[mytid]['id'] = id
    while True:
        option = csocket.recv(1024).decode()
        if option == '1':
            handle_register_file(id, csocket)
        elif option == '2':
            handle_get_global_filelist(csocket)
        elif option == '3':
            handle_download_file(id, csocket)
        elif option == '4':
            handle_exit(csocket, id)
            break

    threadpool[mytid]['valid'] = False
    csocket.close()


def find_free_id():
    for idx, di in enumerate(threadpool):
        if di['valid'] is False:
            return idx
    return -1


'''
TCP Case
'''
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind((serverIP, serverPort))
serverSocket.listen(maxlisten)  # maximum listen
print('The TCP Server is ready to receive.')
print('IP Address is', ipcheck())

while True:
    connectionSocket, clientaddr = serverSocket.accept()
    eid = find_free_id()
    if eid == -1:
        print('No more thread pool')
        exit()
    t = threading.Thread(target=socket_handling, args=(connectionSocket, eid,))
    threadpool[eid]['obj'] = t
    threadpool[eid]['socket'] = connectionSocket
    threadpool[eid]['valid'] = True
    threadpool[eid]['caddr'] = clientaddr
    t.start()
