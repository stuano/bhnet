import socket

target_host = "127.0.0.1"
target_port = 9999

#build a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connect client
client.connect((target_host,target_port))

#send data
 
client.send("Hello world!123".encode("utf-8"))

#receive data
response = client.recv(4096)

print response
