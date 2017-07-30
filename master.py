"""A script that send requests from the user to the workers on the network"""
import sys      #system related task
import socket   #for socket communication
import json     #for sending and receiving objects
import csv
import utils

def main():
    """Main function of the code"""
    #get list of workers
    workers = get_workers()

    #main loop
    while True:
        #keyboard input loop
        while True:
            try:
                input_data = int(input("(0)ping\n(1)kill\n(2)list\n(3)reload\n(4)exit \t:   "))
                break
            except KeyboardInterrupt:
                utils.print_warning("\nShutting master node down.")
                return
            except ValueError:
                utils.print_error("Please, enter a valid option.")
        
        #treatin keyboard input
        if input_data == 0:
            #for each worker
            for worker in workers:
                ping_worker(worker)
        elif input_data == 1:
            #for each worker
            for worker in workers:
                kill_worker(worker)
        elif input_data == 2:
            utils.print_info(workers)
        elif input_data == 3:
            #reload
            utils.print_info("Reloading workers list.")
            workers = get_workers()
            utils.print_success("Done")
        elif input_data == 4:
            utils.print_warning("Shutting master node down.")
            break
        else:
            utils.print_error("Please, enter a valid option.")
    #print(response)


def get_workers():
    """Returns a list with all the ports located in the .csv file passed as argument"""
    #Checking argument
    if len(sys.argv) != 2:
        utils.print_error("Missing filename.\nUsage:\t$" + sys.argv[0]+" <filename>")
        exit(-1)
    #Opening file
    with open(sys.argv[1], 'r') as csvfile:
        #reading content
        spamreader = csv.reader(csvfile, delimiter=',')
        workers_list = []
        #saving to list
        for row in spamreader:
            for val in row:
                workers_list.append(int(val))
    #returning it
    return workers_list

def ping_worker(worker):
    """pings a worker"""
    utils.print_info("Pinging worker: " + str(worker))
    send_request(worker, utils.new_request_dict("PING", 1010, '', '', 'Testing.'), True)

def kill_worker(worker):
    """kills a worker"""
    utils.print_info("Killing worker: " + str(worker))
    send_request(worker, utils.new_request_dict("SHUTDOWN", 1010, '', '', 'Testing.'), True)


def send_request(worker, request_data, wait_response=False):
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
        utils.print_warning("Failed to connect to worker on port: "+str(worker))
        return

    #If waiting for response is necessary, first send a header saying that
    if wait_response:
        encoded_data = sending_data.encode()

        #send a small dict with the size of the next package
        header = json.dumps({"header":"True", "size":len(encoded_data)})

        #send header
        worker_socket.send(header.encode())

        #wait for ack
        ack = worker_socket.recv(1024)
        if ack.decode() != "ACK":
            utils.print_error("Failed to receive ack from worker.")
            worker_socket.close()
            return

        #send data
        worker_socket.send(encoded_data)

        #wait for response
        try:
            while 1:
                data_chunk = worker_socket.recv(1024)
                if not data_chunk:
                    break
                received_data = data_chunk

        except socket.timeout:
            utils.print_error("Worker \'" + str(worker) + "\' did not respond after 5 seconds.")
            return

        #treat received data
        if request_data["action"] == "PING":
            utils.print_success("Received ping: ")
            utils.print_success(received_data.decode())

    else:
        #send data
        worker_socket.sendall(sending_data.encode())

    #closing socket
    worker_socket.close()

if __name__ == '__main__':
    main()
