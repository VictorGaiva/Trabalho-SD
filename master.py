"""A script that send requests from the user to the workers on the network"""
import sys      #system related task
import socket   #for socket communication
import json     #for sending and receiving objects
import csv
import utils

def main():
    """Main function of the code"""
    #get list of workers
    workers = utils.get_ports()

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
            utils.print_info("Pinging workers.")
            for worker in workers:
                ping_worker(worker)
        elif input_data == 1:
            #for each worker
            utils.print_info("Killing workers.")
            for worker in workers:
                kill_worker(worker)
        elif input_data == 2:
            utils.print_info(workers)
        elif input_data == 3:
            #reload
            utils.print_info("Reloading workers list.")
            workers = utils.get_ports()
            utils.print_success("Done")
        elif input_data == 4:
            utils.print_warning("Shutting master node down.")
            break
        else:
            utils.print_error("Please, enter a valid option.")
    #print(response)



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
