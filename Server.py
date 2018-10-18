# Sydney Davis, Quynh Le, Monica Pasala

import os, socket, gzip

# program status starts off as normal. Client can change later
status = "N"

server = socket.socket()
host = socket.gethostname()
port = 21

server.bind((host, port))
server.listen(5)
print("Waiting for connection...")

# Establish connection with client.
conn, addr = server.accept()
print("Made the connection!")

# get log in validation
password = conn.recv(1024).decode()
while '@' not in password:
    auth = "invalid"
    conn.send(auth.encode())
    password = conn.recv(1024).decode()
auth = "valid"
conn.send(auth.encode())

# change directory (should we do path or just directory name??)
# Does cd and ls need close and reeopen connections??
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


# List everything in directory (takes path...but should it take directory only?)
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

# send file to client
def put(filename):
    # use client declared at top
    global conn
    # check if file exists. if not, break
    if os.path.isfile(filename):
        if status == "C":
            f = open(filename, 'rb')
            content = f.read()
            file = gzip.open(filename[:-4] + '.gz', 'wb')
            file.write(content)
            file.close()

            file = gzip.open(filename[:-4]+ '.gz', 'rb')
            data = file.read(1024)
            while data:
                conn.send(data)
                data = file.read(1024)
        elif status == "E":
            with open(filename, 'r') as file:
                data = file.read(1024)
                # in this encryption method, we send the data backwards
                while data:
                    encrypt = ""
                    for i in range(len(data)-1, -1, -1):
                        encrypt += data[i]
                    conn.send(encrypt.encode())
                    data = file.read(1024)
        else:
            with open(filename, 'rb') as file:
                data = file.read(1024)
                while data:
                    conn.send(data)
                    data = file.read(1024)
        file.close()
        print("File " + filename + " sent!\n")
    else:
        print("File " + filename + " does not exist.\n")
    # closing and reopening connection
    conn.close()
    conn, addr = server.accept()

# receive file from client
def get(filename, extension):
    # use client declared at top
    global conn
    newname = filename[:-4] + extension
    if status == "C":
        with open(newname, 'wb') as newFile:
            data = conn.recv(1024)
            # receive until sender ends connection
            while data:
                newFile.write(data)
                data = conn.recv(1024)
    elif status == "E":
        with open(newname, 'w') as newFile:
            data = conn.recv(1024).decode()
            # receive until sender ends connection
            while data:
                decrypt = ""
                for i in range(len(data)-1, -1, -1):
                    decrypt += data[i]
                newFile.write(decrypt)
                data = conn.recv(1024).decode()
    else:
        with open(newname, 'wb') as newFile:
            data = conn.recv(1024)
            # receive until sender ends connection
            while data:
                newFile.write(data)
                data = conn.recv(1024)
    newFile.close()
    # prints even if file doesn't exist on sending side because we created an empty file.
    print("File " + newname + " received.")
    # closing and reopening connection
    conn.close()
    conn, addr = server.accept()

# send multiple files to client
def mput():
    # use client declared at top
    global conn
    filelist = input('Please enter name of files you would like to send '
                      'with a space between each (no commas):\n')
    conn.send(filelist.encode())
    for word in filelist.split():
        put(word)

# receive multiple files from client
def mget(filelist):
    # use client declared at top
    global conn
    for word in filelist.split():
        get(word, "MGET.txt")

while True:
    print("\nWaiting for command from client...\nOptions are: "
          "\n1. cd\t2. ls\t3. change status\t4. get\t5. put\t6. mget\t7. mput\t8. quit\n")

    choice = conn.recv(1024).decode()
    print("Client chose: " + choice + "\n")

    # 1. cd 2. ls 3. change status 4. put (get for client) 5. get (put for client) 6. mget 7. mput 8. quit
    if choice == '1':
        print("\nCurrent working dir is " + os.getcwd() + ".\n")
        pathName = input("Please enter name of directory you would like to change to:\n")
        cd(pathName)
    elif choice == '2':
        pathName = input("Please enter name of path you would like to look at:\n")
        ls(pathName)
    elif choice == '3':
        status = conn.recv(1024).decode()
    elif choice == '4':
        filename = input("Please enter name of file you would like to send:\n")
        conn.send(filename.encode())
        put(filename)
    elif choice == '5':
        print("Receiving file from client...\n")
        filename = conn.recv(1024).decode()
        get(filename, "GET.txt")
    elif choice == '6':
        mput()
    elif choice == '7':
        print("Receiving files from client...\n")
        filelist = conn.recv(1024).decode()
        mget(filelist)
    elif choice == '8':
        conn.close()
        print("Connection has been closed.")
        break