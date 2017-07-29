"""A script that listen for requests from given port"""
import sys      #system related task
import socket   #for socket communication
import json     #for sending and receiving objects


def main():
    """Main function for the code"""
    #init
    processed_requests_count = 0
    #master_key = -1
    worker_port = get_worker_port()

    #getting the socket
    worker_socket = get_socket(worker_port)

    #start receiving requests
    while True:
        #accept connection
        worker_socket.listen(1)
        (worker_socket, addres) = worker_socket.accept()
        #start processing it
        try:
            if process_request(worker_socket, worker_port) == -1:
                #received shutdown flag
                print(str(worker_port) + ":Master node requested for shutdown. bye")
                worker_socket.close()
                break
            else:
                processed_requests_count += 1

        except KeyboardInterrupt:
            print("KeyboardInterrupt. Shutting worker down.")
            worker_socket.close()
            break
    return

def process_request(master_socket, worker_port):
    """Process the request from the network"""
    #data_string = json.dumps(data) #data serialized
    #data_loaded = json.loads(data) #data loaded
    #receive data

    while 1:
        data_chunk = master_socket.recv(1024)
        #if end of transmition
        if not data_chunk:
            break
        #concatenate data to buffer
        print(len(data_chunk))
        received_data_buffer += data_chunk

    #processing request
    received_dict = json.loads(received_data_buffer)

    return_val = 0

    #error prevention
    if not received_dict:
        print(str(worker_port) + ":Error. Received object is " + type(received_dict))
    else:
        #Processing the data

        #shutdown signal
        if received_dict["Action"] == "SHUTDOWN":
            return_val = -1
            master_socket.sendall(str(worker_port) + ": Shutting down.")

        if received_dict["Action"] == "PING":
            print(str(worker_port) + ": " + received_dict["Data"])
            master_socket.sendall(str(worker_port) + ": Pong.")
            return_val = 1

    #closing socket
    master_socket.close()

    return return_val

def get_worker_port():
    """returns the worker port from the given argument"""
    #Checking argument
    if len(sys.argv) != 2:
        print("Missing work port number.\nUsage:\t$" + sys.argv[0]+" <port>")
        exit(-1)
    #Checking argument type
    try:
        worker_port = int(sys.argv[1])
    except TypeError:
        print("Argument must be a number.\nUsage:\t$" + sys.argv[0]+" <port>")
        exit(-1)
    return worker_port


def get_socket(worker_port):
    """returns a socket binded to given port"""
    #opening the socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Commom TCP socket
    try:
        #binding to the right port
        serversocket.bind(('localhost', worker_port))
    except ConnectionError:
        print("\nFailed to bind to port " + str(worker_port))
        exit(-1)
    #return that shit
    return serversocket

def new_request_dict(action, source, field1, field2, data):
    """Return a dict in the wanted format"""
    return_dict = {}
    return_dict["action"] = action #[ "RESIZE" | "SHUTDOWN" | "PING"]
    return_dict["source"] = source #[ $URL | 'DATA' | $KEY ]
    return_dict["field1"] = field1 #[ '' | $TARGET_WIDTH]
    return_dict["field2"] = field2 #[ '' | $TARGET_HEIGHT]
    return_dict["data"] = data   #[ '' | $PING_DATA |$IMAGE]
    return return_dict

if __name__ == '__main__':
    main()
