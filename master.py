"""A script that send requests from the user to the workers on the network"""
import sys      #system related task
import socket   #for socket communication
import json     #for sending and receiving objects
import csv

def main():
    """Main function of the code"""
    #get list of workers
    workers = get_workers()

    while 1:
        try:
            input_data = int(input("0:ping, 1:kill, 2:exit ->"))
        except KeyboardInterrupt:
            print("\nShutting master node down.")
            break
        except TypeError:
            print("\nPlease, enter a valid option.")

        if input_data == 0:
            for worker in workers:
                ping_worker(worker)
        elif input_data == 1:
            for worker in workers:
                kill_worker(worker)
        elif input_data == 2:
            print("Shutting master node down.")
            break

    #print(response)


def get_workers():
    """Returns a list with all the ports located in the .csv file passed as argument"""
    #Checking argument
    if len(sys.argv) != 2:
        print("Missing filename.\nUsage:\t$" + sys.argv[0]+" <filename>")
        exit(-1)
    #Opening file
    with open(sys.argv[1], 'rb') as csvfile:
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
    print("Pinging worker: " + str(worker))
    send_request(worker, new_request_dict("PING", 1010, '', '', 'Testing.'), True)

def kill_worker(worker):
    """kills a worker"""
    print("Killing worker: " + str(worker))
    send_request(worker, new_request_dict("SHUTDOWN", 1010, '', '', 'Testing.'))


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
        print("Failed to connect to worker on port: "+str(worker))
        return

    #send data
    worker_socket.sendall(sending_data)

    received_data_buffer = ""
    #waiting for response if necessary
    if wait_response:
        try:
            #receive all data
            while 1:
                data_chunk = worker_socket.recv(1024)

                if not data_chunk:
                    break

                print(data_chunk)
                received_data_buffer += data_chunk
        except socket.timeout:
            print("Worker \'" + str(worker) + "\' did not respond after 5 seconds.")
            return

    #closing socket
    worker_socket.close()

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