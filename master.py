"""A script that send requests from the user to the workers on the network"""
import socket   #for socket communication
import json     #for sending and receiving objects
import threading
import utils


def main():
    """Main function of the code"""
    #setting the default port for incoming requests
    requests_port = 12339
    #get list of workers
    workers = utils.get_ports()

    #create a locker for the workers
    workers_lock = threading.Lock()

    #creating thread for keyboard handling
    input_handler = threading.Thread(target=handle_keyboard_input,
                                     name="input_handler",
                                     args=(workers, workers_lock))
    
    #creating thread for network handling
    network_handler = threading.Thread(target=handle_network_requests,
                                       name="network_handler",
                                       args=(workers, workers_lock, requests_port))

    #start threads
    input_handler.start()
    network_handler.start()

    #waits for a user request for shutdown
    input_handler.join()

def handle_network_requests(workers, workers_lock, requests_port):
    """Waits for incoming connections and process the requests"""
    #tries to bind to received port
    network_socket = utils.get_socket(requests_port, True)
    if not network_socket:
        return

    utils.print_info("Now listening for incoming requests.")
    while True:
        #accept connection
        network_socket.listen()

        utils.print_info("Received one connection request. Accepting it.")

        (request_socket, address) = network_socket.accept()

        utils.print_info("Processing request.")

        #process incoming request
        #process_network_request(request_socket, address, workers_lock, workers)

        #close request socket
        request_socket.close()


    return

def handle_keyboard_input(workers, workers_lock):
    """Handles the user keyboar_input"""
    #main handling loop
    while True:
        #reading loop
        while True:
            try:
                input_data = int(input("(0)ping\n(1)kill\n(2)list\n(4)exit \t:   "))
                break
            except KeyboardInterrupt:
                utils.print_warning("\nShutting master node down.")
                return
            except ValueError:
                utils.print_error("Please, enter a valid option.")

        #treating keyboard input
        if input_data == 0:
            #for each worker
            if workers_lock.acquire(blocking=False):#get lock
                utils.print_info("Pinging workers.")
                for worker in workers:
                    ping_worker(worker)
                workers_lock.release()#release lock
            else:
                utils.print_info("Workers are busy. Try again later.")

        #kill workers
        elif input_data == 1:
            #for each worker
            if workers_lock.acquire(blocking=False):#get lock
                utils.print_info("Killing workers.")
                for worker in workers:
                    kill_worker(worker)
                workers_lock.release()#release lock
            else:
                utils.print_info("Workers are busy. Try again later.")

        #print workers info
        elif input_data == 2:
            utils.print_info(workers)

        #exit
        elif input_data == 4:
            utils.print_warning("Shutting master node down.")
            return
        else:
            utils.print_error("Please, enter a valid option.")
    return

def ping_worker(worker):
    """pings a worker"""
    #utils.print_info("Pinging worker: " + str(worker))
    send_request(worker, utils.new_request_dict("PING", 1010, '', '', 'Testing.'))

def kill_worker(worker):
    """kills a worker"""
    #utils.print_info("Killing worker: " + str(worker))
    send_request(worker, utils.new_request_dict("SHUTDOWN", 1010, '', '', 'Testing.'))


def send_request(worker, request_data):
    """sends data to a worker"""
    #encapsula
    sending_data = json.dumps(request_data)

    #opening socket
    worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Setting timeout
    worker_socket.settimeout(5)

    #trying to connect
    try:
        worker_socket.connect(('localhost', worker))
    except ConnectionError:
        #utils.print_warning("No worker at " + str(worker)+ ".")
        return

    #encode data
    encoded_data = sending_data.encode()

    #send header and waits for ack
    if not send_header(worker_socket, len(encoded_data)):
        worker_socket.close()
        return

    #send data
    worker_socket.send(encoded_data)

    #wait for response
    received_data = bytes()
    try:
        while 1:
            data_chunk = worker_socket.recv(1024)
            if not data_chunk:
                break
            received_data = data_chunk

    except socket.timeout:
        utils.print_error("Worker \'" + str(worker) + "\' did not respond after 5 seconds.")
        return
    if not received_data:
        utils.print_error("Connection closed from worker while expecting ack.")
        worker_socket.close()
        return

    #treat received data
    if request_data["action"] == "PING":
        utils.print_success("Ping response: "+received_data.decode())

    #
    if request_data["action"] == "SHUTDOWN":
        utils.print_success("Shutdown response:"+received_data.decode())

    #closing socket
    worker_socket.close()

def send_header(worker_socket, size):
    """sends a header for the worker and waits for ack"""
    #send the header
    header = json.dumps({"header":"True", "size":size})

    #send header
    worker_socket.send(header.encode())

    #wait for ack
    try:
        ack = worker_socket.recv(1024)
    except socket.timeout:
        utils.print_error("Timed out waiting for ACK from worker.")
        return
    if not ack:
        utils.print_error("Worker disconnected master was waiting for ACK.")
    elif ack.decode() != "ACK":
        utils.print_error("Invalid message while expectiong for ACK.")
        return False

    return True

if __name__ == '__main__':
    main()
