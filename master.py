"""A script that send requests from the user to the workers on the network"""
import socket   #for socket communication
import json     #for sending and receiving objects
import threading
import os
import time
import PIL
import utils

def main():
    """Main function of the code"""
    #setting the default port for incoming requests
    requests_port = 12339

    #get list of workers
    workers = utils.get_ports()

    #create a lockers for the workers
    workers_lock = threading.Lock()
    shutdown_signal = threading.Event()

    #create the cache directory
    check_cache()

    #creating thread for network handling
    network_handler = threading.Thread(target=handle_network_requests,
                                       name="network_handler",
                                       args=(workers, workers_lock, requests_port, shutdown_signal))

    #start threads
    network_handler.start()

    #start taking care of keyboard inputs
    handle_keyboard_input(workers, workers_lock, shutdown_signal)

    #if returned from keyboard handling, wait for network_handler to shutdown
    network_handler.join()

def handle_keyboard_input(workers, workers_lock, shutdown_signal):
    """Handles the user keyboar_input"""
    #main handling loop
    while True:
        #reading loop
        while True:
            try:
                utils.print_success("(0)ping\n(1)kill\n(2)list\n(3)test\n(4)exit")
                input_data = int(input())
                break
            except KeyboardInterrupt:
                utils.print_warning("\nShutting master node down.")
                shutdown_signal.set()
                signal_network_handler()
                return
            except ValueError:
                utils.print_error("Please, enter a valid option.")

        #treating keyboard input
        if input_data == 0:
            #ping each worker
            if workers_lock.acquire(blocking=False):#get lock
                utils.print_info("Pinging workers.")
                #if there are no workers alive
                if for_each_worker(workers, "PING", True) == 0:
                    utils.print_warning("Not active worker on the network.")
                workers_lock.release()#release lock
            else:
                utils.print_info("Workers are busy. Try again later.")

        elif input_data == 1:
            #kill workers
            if workers_lock.acquire(blocking=False):#get lock
                utils.print_info("Killing workers.")
                #if there are no workers alive
                if for_each_worker(workers, "KILL", True) == 0:
                    utils.print_warning("Not active worker on the network.")
                workers_lock.release()#release lock
            else:
                utils.print_info("Workers are busy. Try again later.")

        #print workers info
        elif input_data == 2:
            utils.print_info(workers)

        #test workers
        elif input_data == 3:
            #test workers
            if workers_lock.acquire(blocking=False):#get lock
                utils.print_info("Testing workers.")
                #if there are no workers alive
                if for_each_worker(workers, "TEST", True) == 0:
                    utils.print_warning("Not active worker on the network.")
                workers_lock.release()#release lock
            else:
                utils.print_info("Workers are busy. Try again later.")

        #exit
        elif input_data == 4:
            shutdown_signal.set()
            signal_network_handler()
            utils.print_warning("Shutting master node down.")
            return
        else:
            utils.print_error("Please, enter a valid option.")
    return

def for_each_worker(workers, action, sequential=False, data=''):
    """Makes action for each worker in list. If\
       sequential flag is on, do in a loop,\
       else, do in separated threads"""
    count = 0

    #for testing purposes
    if action == "TEST":
        data = []
        import glob
        for fle in glob.glob("./test_files/sci.space/*"):
            with open(fle) as file_data:
                data.append(file_data.read())
        utils.print_success(len(data))
        action = "PROCESS"
        sequential = False

    #if sequential
    if sequential:
        #for each worker
        for worker in workers:
            #send a request
            if send_request(worker, utils.new_request_dict(action, 1010, '', '', '')):
                count += 1

    #in threads
    else:
        #count how many workers are alive
        workers_alive = for_each_worker(workers, "PING", True)
        count = workers_alive

        #if there is no one to process requests
        if workers_alive == 0:
            utils.print_error("No active workers on the network to process request.")
            return workers_alive

        #check if there is data
        if data == '':
            utils.print_error("No data to process. Forgot the parameter?")
            return workers_alive

        #if you want the workers to process the data
        if action == "PROCESS":
            #make an array which will hold the threads
            worker_handler_threads = []

            #make an array which will hold the result of the data processing
            processed_data = []

            #split the list of data to distribute to the workers
            chunk_size = int(len(data)/workers_alive) + (len(data) % workers_alive > 0)
            pre_processed_count = 0
            json_chunks = []
            while pre_processed_count < len(data):
                #end of data
                if (pre_processed_count + chunk_size) > len(data):
                    chunk = data[pre_processed_count : int(len(data)%chunk_size)]
                    json_chunks.append(json.dumps(chunk))
                #else
                else:
                    chunk = data[pre_processed_count:pre_processed_count+chunk_size]
                    json_chunks.append(json.dumps(chunk))
                #increase count
                pre_processed_count += chunk_size

            #test
            utils.print_success(str(workers_alive))
            utils.print_success(str(len(json_chunks)))

    return count
def handle_network_requests(workers, workers_lock, requests_port, shutdown_signal):
    """Waits for incoming connections and process the requests"""
    #tries to bind to received port
    tries = 0
    while True:
        network_socket = utils.get_socket(requests_port, False)

        #verify if there is a shutdown signal
        if shutdown_signal.is_set():
            utils.print_info("Shuting down network handler.")
            #if the socket is open, close it before leaving
            if network_socket:
                network_socket.close()
            return
        #if got the socket, get out of the loop
        if network_socket:
            break

        #if it didn't get the socket
        elif not network_socket:
            #exit if there were 5 tries or more
            if tries >= 5:
                utils.print_error("Network handler failed to bind after 5 tries.\
                                   Shuting down network handler.")
                return
            #else, try again after 5 seconds
            tries += 1
            utils.print_warning("Network handler failed to bind. Trying again in 5 seconds.")
            time.sleep(5)

    if shutdown_signal.is_set():
        utils.print_info("Shuting down network handler.")
        return

    #utils.print_info("Now listening for incoming requests.")
    while True:
        #accept connection
        network_socket.listen()

        (request_socket, address) = network_socket.accept()

        utils.print_info("Received one connection request.")

        if shutdown_signal.is_set():
            utils.print_info("Shuting down network handler.")
            break

        utils.print_info("Processing request.")

        #process incoming request
        #process_network_request(request_socket, address, workers_lock, workers)

        #close request socket
        request_socket.close()

    network_socket.close()
    return



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
        return False

    #encode data
    encoded_data = sending_data.encode()

    #send header and waits for ack
    if not send_header(worker_socket, len(encoded_data)):
        worker_socket.close()
        return False

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
        return False
    if not received_data:
        utils.print_error("Connection closed from worker while expecting ack.")
        worker_socket.close()
        return False

    #close socket
    worker_socket.close()

    #return received data
    return received_data.decode()

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

def check_cache():
    """Checks if there is an cache directory. If there isn't, make one"""
    if not os.path.isdir("./cache"):
        try:
            os.mkdir("./cache")
            utils.print_info("Created new cache dir.")
        except OSError:
            utils.print_error("Error in creating cache dir.")

    else:
        utils.print_info("Cache dir already exists.")

def signal_network_handler():
    """Makes a dummy connection to itself so that the
       network handler thread sees the shutdown signal"""
    #opening socket
    network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #trying to connect
    try:
        network_socket.connect(('localhost', 12339))
    except ConnectionError:
        utils.print_info("Network handler already down.")
        return

    network_socket.close()


if __name__ == '__main__':
    main()
