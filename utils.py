"""a few functions used both by the workers and master"""
import csv
import sys
import socket

class Bcolor():
    """enumerating some conts"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_warning(message):
    """prints an error message"""
    print(Bcolor.WARNING + str(message) + Bcolor.ENDC)

def print_error(message):
    """prints an error message"""
    print(Bcolor.FAIL + str(message) + Bcolor.ENDC)

def print_success(message):
    """prints a success message"""
    print(Bcolor.OKGREEN + str(message) + Bcolor.ENDC)

def print_info(message):
    """prints a success message"""
    print(Bcolor.OKBLUE + str(message) + Bcolor.ENDC)


def new_request_dict(action, source, field1, field2, data):
    """Return a dict in the wanted format"""
    return_dict = {}
    return_dict["header"] = "True"
    return_dict["action"] = action #[ "RESIZE" | "SHUTDOWN" | "PING"]
    return_dict["source"] = source #[ $URL | 'DATA' | $KEY ]
    return_dict["field1"] = field1 #[ '' | $TARGET_WIDTH]
    return_dict["field2"] = field2 #[ '' | $TARGET_HEIGHT]
    return_dict["data"] = data   #[ '' | $PING_DATA |$IMAGE]
    return return_dict

def get_ports():
    """Returns a list with all the ports located in the .csv file passed as argument"""
    #Checking argument
    if len(sys.argv) != 2:
        print_error("Missing filename.\nUsage:\t$" + sys.argv[0]+" <filename>")
        exit(-1)
    #Opening file
    with open(sys.argv[1], 'r') as csvfile:
        #reading content
        spamreader = csv.reader(csvfile, delimiter=',')
        ports = []
        #saving to list
        for row in spamreader:
            for val in row:
                ports.append(int(val))
    #returning it
    return ports

def get_socket(port, verbose=False):
    """returns a socket binded to given port"""
    #opening the socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Commom TCP socket
    try:
        #binding to the right port
        serversocket.bind(('localhost', port))
    except OSError:
        if verbose:
            print_error("Failed to bind to port " + str(port))
        return False

    #return that shit
    return serversocket
