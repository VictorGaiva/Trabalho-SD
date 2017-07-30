"""A script that listen for requests from given port"""
import sys      #system related task
import socket   #for socket communication
import json     #for sending and receiving objects
import utils

def main():
    """Main function for the code"""
    #init
    processed_requests_count = 0
    #master_key = -1
    worker_port = get_worker_port()
    utils.print_info("Starting worker at port " + str(worker_port))

    #getting the socket
    utils.print_info("Binding to port.")
    worker_socket = get_socket(worker_port)

    #start receiving requests
    utils.print_info("Now listening for requests.")
    while True:
        try:
            #accept connection
            worker_socket.listen()
            (request_socket, address) = worker_socket.accept()
            #start processing it
            if process_request(request_socket, worker_port) == -1:
                #received shutdown flag
                utils.print_warning(str(worker_port) + ":Master node requested for shutdown. bye")
                request_socket.close()
                break
            else:
                utils.print_success("Processed one request.")
                processed_requests_count += 1

        except KeyboardInterrupt:
            utils.print_warning("\nKeyboardInterrupt. Shutting worker down.")
            worker_socket.close()
            break
    return

def process_request(master_socket, worker_port):
    """Process the request from the network"""
    #data_string = json.dumps(data) #data serialized
    #data_loaded = json.loads(data) #data loaded
    #receive data
    return_val = 0

    #receive header
    received_data = master_socket.recv(1024)

    #processing request
    received_dict = json.loads(received_data.decode())

    #read the header
    if received_dict["header"] == "True":
        received_bytes = 0
        expected_bytes = received_dict["size"]
        received_data_buffer = bytes()

        #send ack
        master_socket.sendall("ACK".encode())

        while expected_bytes > received_bytes:
            data_chunk = master_socket.recv(1024)
            received_bytes += len(data_chunk)

            #if end of transmition
            if not data_chunk:
                utils.print_error("Connection closed from master while expecting more data.")
                break

            #concatenate data to buffer
            received_data_buffer += data_chunk

        received_dict = json.loads(received_data_buffer.decode())

        #ping signal
        if received_dict["action"] == "PING":
            sending_data = str(worker_port) + " says: pong."
            master_socket.sendall(sending_data.encode())
            return_val = 1
    else:
        #shutdown signal
        if received_dict["action"] == "SHUTDOWN":
            return_val = -1
            master_socket.sendall(str(worker_port) + ": Shutting down.")

    #closing socket
    master_socket.close()

    return return_val

def get_worker_port():
    """returns the worker port from the given argument"""
    #Checking argument
    if len(sys.argv) != 2:
        utils.print_error("Missing work port number.")
        utils.print_info("Usage:\t$" + sys.argv[0]+" <port>")
        exit(-1)
    #Checking argument type
    try:
        worker_port = int(sys.argv[1])
    except TypeError:
        utils.print_error("Argument must be a number.")
        utils.print_info("Usage:\t$" + sys.argv[0]+" <port>")
        exit(-1)
    except ValueError:
        utils.print_error("Argument must be a number.")
        utils.print_info("Usage:\t$" + sys.argv[0]+" <port>")
        exit(-1)
    return worker_port


def get_socket(worker_port):
    """returns a socket binded to given port"""
    #opening the socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Commom TCP socket
    try:
        #binding to the right port
        serversocket.bind(('localhost', worker_port))
    except OSError:
        utils.print_error("Failed to bind to port " + str(worker_port))
        exit(-1)
    #return that shit
    return serversocket

if __name__ == '__main__':
    main()
