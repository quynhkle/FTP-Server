# Sydney Davis, Quynh Le, Monica Pasala

import os, socket, getpass, gzip

# program status starts off as normal. User is given the option to change.
status = "N"

serverIP = input("Please enter Server IP-address: ")
client = socket.socket()
port = 21

# establish connection with server
client.connect((serverIP, port))
print("Made the connection!")

# login validation - for us, getpass only works properly in command line
id = input("Please enter identification.\n")
password = getpass.getpass("Hello, please enter password.\n")
client.send(password.encode())
auth = client.recv(1024).decode()
while auth != "valid":
    password = getpass.getpass("That was not a valid password. Please enter again:\n")
    client.send(password.encode())
    auth = client.recv(1024).decode()
print("Password accepted.\n")

# change directory
def cd(pathName):
    # check if directory exists. if not, break.
    if os.path.isdir(pathName):
        # Opening the desired directory
        fd = os.open(pathName, os.O_RDONLY)
        # Changing directory
        os.fchdir(fd)
        # Print current working directory
        print("\nCurrent working dir is " + os.getcwd() + ".\n")
        # Closing opened directory
        os.close(fd)
    else:
        print("Directory " + pathName + " does not exist.\n")


# List everything in directory from input
def ls(pathName):
    # check if path exists. if not, break.
    if os.path.exists(pathName):
        # open a file
        dirs = os.listdir(pathName)
        # Print all the files and directories
        for file in dirs:
            print(file)
    else:
        print("Path " + pathName + " does not exist.\n")

# receive file from server
def get(filename, extension, status):
    global client
    newname = filename[:-4] + extension
    if status == "C":
        # compression option
        with open(newname, 'wb') as newFile:
            data = client.recv(1024)
            # receive until sender ends connection
            while data:
                newFile.write(data)
                data = client.recv(1024)
            newFile.close()
    elif status == "E":
        # encryption option
        with open(newname, 'w') as newFile:
            data = client.recv(1024).decode()
            # receive until sender ends connection
            while data:
                # undo the encryption, which was reverse each bit of data
                decrypt = ""
                for i in range(len(data)-1, -1, -1):
                    decrypt += data[i]
                newFile.write(decrypt)
                data = client.recv(1024).decode()
            newFile.close()
    else:
        # normal option
        with open(newname, 'wb') as newFile:
            data = client.recv(1024)
            # receive until sender ends connection
            while data:
                newFile.write(data)
                data = client.recv(1024)
            newFile.close()
    # prints even if file doesn't exist on sending side because we created an empty file.
    print("File " + newname + " received.")
    # closing and reopening connection.
    client.close()
    client = socket.socket()
    client.connect((serverIP, port))

# send file to server
def put(filename, status):
    global client
    # check if file exists. if not, break.
    if os.path.isfile(filename):
        if status == "C":
            # compress the file into a new gzip file and close.
            f = open(filename, 'rb')
            content = f.read()
            file = gzip.open(filename[:-4] + '.gz', 'wb')
            file.write(content)
            file.close()

            # open gzip file, read, and send
            file = gzip.open(filename[:-4] + '.gz', 'rb')
            data = file.read(1024)
            while data:
                client.send(data)
                data = file.read(1024)
        elif status == "E":
            # open txt file, read, encrypt, and send
            with open(filename, 'r') as file:
                data = file.read(1024)
                while data:
                    encrypt = ""
                    # encryption: just send each string reversed
                    for i in range(len(data) - 1, -1, -1):
                        encrypt += data[i]
                    client.send(encrypt.encode())
                    data = file.read(1024)
        else:
            # normal option. Just read from text file and send.
            with open(filename, 'rb') as file:
                data = file.read(1024)
                while data:
                    client.send(data)
                    data = file.read(1024)

        file.close()
        print("File " + filename + " sent!\n")
    else:
        print("File " + filename + " does not exist.\n")
    # close and reopen connection
    client.close()
    client = socket.socket()
    client.connect((serverIP, port))

# get multiple files from server
def mget(filelist, status):
    global client
    for word in filelist.split():
        get(word, "MGET.txt", status)

# send multiple files to server
def mput(status):
    # use client declared at top
    global client
    filelist = input('Please enter name of files you would like to send '
                      'with a space between each (no commas):\n')
    client.send(filelist.encode())
    for word in filelist.split():
        put(word, status)

# enter menu loop
while True:
    choice = input("\nHello, please input a number for what you'd like to do:"
                       "\n1. cd\n2. ls\n3. change status\n4. get\n5. put\n6. mget\n7. mput\n8. quit\n\n")
    client.send(choice.encode())
    if choice == '1':
        print("\nCurrent working dir is " + os.getcwd() + ".\n")
        pathName = input("Please enter name of directory you would like to change to:\n")
        cd(pathName)
    elif choice == '2':
        pathName = input("Please enter name of path you would like to look at:\n")
        ls(pathName)
    elif choice == '3':
        status = input('\nPlease enter the status you would like to set the program to:\n'
                       'N - normal\nC - compressed\nE - encrypted\n\n'
                       'If an invalid status is input, the program will set status to normal.\n')
        if status not in ["N", "E", "C"]:
            status = "N"
        client.send(status.encode())
        print("\nStatus has been set to " + status + ".\n")
    elif choice == '4':
        print("Receiving file from server...\n")
        filename = client.recv(1024).decode()
        get(filename, "GET.txt", status)
    elif choice == '5':
        filename = input("Please enter name of file you would like to send:\n")
        client.send(filename.encode())
        put(filename, status)
    elif choice == '6':
        print("\nReceiving files from server...\n")
        filelist = client.recv(1024).decode()
        mget(filelist, status)
    elif choice == '7':
        mput(status)
    elif choice == '8':
        client.close()
        print("The connection has been closed.")
        break
    else:
        print("That was not a choice. Please choose again.\n")