#!/bin/env python2
import socket
import subprocess
import threading
import getopt
import sys

def usage():
    print "-h --help"
    print "-t --target"
    print "-p --port"
    print "-l --listen"
    print "-c --command"
    print "-u --upload"
    print "-e --excute"
    print 
    print "Example: "
    print "         ./bhnet.py -t 127.0.0.1 -p 12345 -l -c"
    print "         ./bhnet.py -t 127.0.0.1 -p 12345 -l -u c://target.exe"
    print "         ./bhnet.py -t 127.0.0.1 -p 12345 -l -e \"cat /etc/passwd\""
    print "         echo ABCDEFG | ./bhnet.py -t 127.0.0.1 -p 12345"
    sys.exit(0)

def client_sender(buffer): 
    global target
    global port

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)
    
        while True:
            recv_len = 1
            response = ""
            while recv_len:
                recv_len = client.recv(1024)
                response += recv_len
                if len(recv_len) < 1024:
                    break

            buffer = raw_input(response)
            buffer += '\n'
            client.send(buffer)

    except:
        print "[*] Exception! Exiting."
        
        
def server_loop():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=client_handler, args=(client,))
        thread.start()

def client_handler(client_socket):
    if len(excute):
        output = run_command(excute)
        client_socket.send(output)

    if len(upload_file):
        file_buffer = ''
        while True:
            data = client_socket.recv(1024)
            file_buffer += data
            if len(data) < 1024:
                break
        write_file = open(upload_file, "wb")
        write_file.write(file_buffer)
        write_file.close()
        client_socket.send("Finished writing!")

    if command:
        while True:
            client_socket.send("<BHP:#> ")
            # get command from client
            cmd_buffer = ""

            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            client_socket.send(run_command(cmd_buffer))

def run_command(cmd):
    cmd = cmd.rstrip()
    try:
        output = subprocess.check_output(cmd, shell = True)
    except:
        output = "Failed to excute command.\r\n"
    return output

def main():
    global target
    global port
    global listen
    global command
    global upload_file
    global excute

    target = '0.0.0.0'
    listen = False
    command = False
    upload_file = ''
    excute = ''

    if not len(sys.argv[1:]):
        usage()
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ht:p:lcu:e:', ['help', 'target=', 'port=', 'listen', 'command', 'upload=', 'excute='])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-t', '--target'):
            target = a
        elif o in ('-p', '--port'):
            port = int(a)
        elif o in ('-l', '--listen'):
            listen = True
        elif o in ('-c', '--command'):
            command = True
        elif o in ('-u', '--upload'):
            upload_file = a
        elif o in ('-e', '--excute'):
            excute = a
        
    if not listen and len(target) and port > 0:

        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()

main()
