from socket import *
import os


def parsing(message):
    sline = message.split('\r\n')[0]
    line = sline.split()[1]
    filename = line[1:]
    print('filename is', filename)
    return filename


def ipcheck():
    return gethostbyname(gethostname())


serverIP = 'localhost'
serverPort = 2000  # 10080 is not allowed in macOS
maxlisten = 5
filedir = './'
http_404_response = "HTTP/1.1 404 Not Found\r\n\r\n"
http_200_resposne_header = "HTTP/1.1 200 OK\r\n"

'''
TCP Case
'''
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind((serverIP, serverPort))
serverSocket.listen(maxlisten)
print('The TCP Server is ready to receive.')
print('IP Address is', ipcheck())

while True:
    print('accept wait')
    connectionSocket, clientaddr = serverSocket.accept()

    try:
        msg = connectionSocket.recv(1024)  # accept raw data
        msg = msg.decode()  # decode raw data

        filename = parsing(msg)
        file_path = os.path.join(filedir, filename)
        # file is available?
        if os.path.exists(file_path):
            print("I find the file.")
            with open(file_path, 'rb') as bfile:
                body = bfile.read()

            responseMsg = http_200_resposne_header  # 200 header
            if filename.split('.')[1] == 'jpg' or filename.split('.')[1] == 'jpeg':
                print('filetype is jpg')
                responseMsg += "Content-Type: image/jpeg\r\n"
            elif filename.split('.')[1] == 'png':
                print('filetype is png')
                responseMsg += "Content-Type: image/png\r\n"
            else:
                print('filetype is pdf')
                responseMsg += "Content-Type: application/pdf\r\n"
            responseMsg += "Content-Length: {}\r\n\r\n".format(len(body))
            if str(type(body)).find("str") > -1:
                print("String based file")
                connectionSocket.sendall(bytes(responseMsg + body, "ASCII"))
            else:
                print("Not String based file")
                connectionSocket.sendall(bytes(responseMsg, "ASCII") + body)
        else:
            print("I can't find the file.")
            http_response = http_404_response.encode()  # 404 header
            connectionSocket.send(http_response)

    except Exception as err:
        # error handling mechanism
        print('error occur', err)
        break
    finally:
        connectionSocket.close()


'''
Example of message

http://127.0.0.1:2000/ddd.jpg

GET /ddd HTTP/1.1
Host: 127.0.0.1:2000
Connection: keep-alive
Cache-Control: max-age=0
sec-ch-ua: "Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "macOS"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7
'''