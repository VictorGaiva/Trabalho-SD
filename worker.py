"""A script that listen for requests from given port"""
import sys      #system related task
import json     #for sending and receiving objects
import PIL
import utils

def main():
    """Main function for the code"""
    #init
    processed_requests_count = 0
    #master_key = -1

    #getting a available port number
    available_ports = get_worker_port()

    if isinstance(available_ports, int):
        #tries to bind to received port
        worker_socket = utils.get_socket(available_ports, True)
        if not worker_socket:
            return
        #saves the port number
        worker_port = available_ports
    else:
        #keep trying to bind to a port until gets some
        for port in available_ports:
            worker_socket = utils.get_socket(port)
            if worker_socket:
                worker_port = port
                break
        if not worker_socket:
            utils.print_error("Couldn't bind to any port in the file")
            return

    #start receiving requests
    utils.print_info("Worker started at port " + str(worker_port))
    while True:
        try:
            #accept connection
            worker_socket.listen()
            (request_socket, address) = worker_socket.accept()

            #start processing it
            retval = process_request(request_socket, worker_port)

            #close socket
            request_socket.close()

            if retval == -1:
                #received shutdown flag
                utils.print_warning(str(worker_port) + ":Master node requested for shutdown. bye")
                worker_socket.close()
                break
            elif retval == 1:
                utils.print_success("Processed one request.")
                processed_requests_count += 1
            else:
                utils.print_error("Failed to process one request.")

        except KeyboardInterrupt:
            utils.print_warning("\nKeyboardInterrupt. Shutting worker down.")
            worker_socket.close()
            break
    return

def process_request(master_socket, worker_port):
    """Process the request from the network"""
    return_val = 0

    #receive header
    received_data = master_socket.recv(1024)

    #processing request
    received_dict = decode_dict(received_data)

    #error in header
    if not received_dict or "header" not in received_dict:
        utils.print_error("Error in received header.")
        return 0

    #read the header
    if received_dict["header"]:

        #send ack
        master_socket.sendall("ACK".encode())

        #get response
        received_data = receive_request(master_socket, received_dict["size"])

        #decode data
        received_dict = decode_dict(received_data)

        #error on package
        if not received_dict or "action" not in received_dict:
            utils.print_error("Error in received package.")
            return 0

        #do the processing
        (processed_data, flags) = do_process_data(worker_port, received_dict)

        #send data
        master_socket.sendall(processed_data.encode())

        #set flag
        return_val = flags

    #non-header package received
    else:
        utils.print_error("Unrecognized request.")

    return return_val

def do_process_data(worker_port, request):
    """Find what action is need on the request e return\
       the resulting processed request with a flag"""
    flags = 0
    sending_data = ''
    #ping signal
    if request["action"] == "PING":
        sending_data = str(worker_port) + "->Pong."
        flags = 1

    #word count
    elif request["action"] == "WORD_COUNT":
        sending_data = word_count(request["data"])
        flags = 1

    #shutdown signal
    elif request["action"] == "SHUTDOWN":
        sending_data = str(worker_port) + "->Shutting down."
        flags = -1
    return (sending_data, flags)

def get_worker_port():
    """returns the worker port from the given argument"""
    #Checking argument
    if len(sys.argv) != 2:
        utils.print_error("Missing work port number.")
        utils.print_info("Usage:\t$" + sys.argv[0]+" <port|avaliable_ports.csv>")
        exit(-1)

    #Checking argument type
    try:
        #file
        if sys.argv[1].endswith(".csv"):
            #parse each val from string to int
            avaliable_ports_ = utils.get_ports()
            avaliable_ports = []
            #make the list
            for port in avaliable_ports_:
                avaliable_ports.append(int(port))
            #return it
            return avaliable_ports
        else:
            #if is not a file, parse the string
            worker_port = int(sys.argv[1])
    except TypeError:
        utils.print_error("Argument must be a number.")
        utils.print_info("Usage:\t$" + sys.argv[0]+" <port|avaliable_ports.csv>")
        exit(-1)
    except ValueError:
        utils.print_error("Argument must be a number.")
        utils.print_info("Usage:\t$" + sys.argv[0]+" <port|avaliable_ports.csv>")
        exit(-1)
    return worker_port


def receive_request(master_socket, size):
    """waits for data from given socket"""
    received_bytes = 0
    expected_bytes = size
    received_data_buffer = bytes()

    #wait to receive all bytes
    while expected_bytes > received_bytes:
        data_chunk = master_socket.recv(1024)
        received_bytes += len(data_chunk)

        #if end of transmition
        if not data_chunk:
            utils.print_error("Connection closed from master while expecting more data.")
            break

        #concatenate data to buffer
        received_data_buffer += data_chunk

    return received_data_buffer

def decode_dict(received_data):
    """Decodes the received data into a dict"""
    try:
        received_dict = json.loads(received_data.decode())
    except json.decoder.JSONDecodeError:
        utils.print_error("Error trying to decode json data.")
        return False
    return received_dict

def resize_image(image_data, target_width=0, target_height=0):
    """Resizes an image to the target width or height"""
    basewidth = 300
    img = PIL.Image.open('fullsized_image.jpg')
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
    img.save('resized_image.jpg')

def word_count(text_data):
    """A simple word counting algorithm which receives a text string\
       and returns a dictionary with the number of times each word appears"""
    #error prevention
    if text_data == '':
        return json.dumps({})

    from collections import defaultdict

    #turn json into list
    text_list = json.loads(text_data)

    #list of words of each text
    processed_text_list = []

    #remove ponctuation and make all the letters lower case in the text
    for text_ in text_list:
        processed_text_list.append(''.join(c if c.isalnum() else ' ' for c in text_.lower()).split())

    #preparing the returning variable
    result = defaultdict(int)

    #do the counting
    for processed_text in processed_text_list:
        for word in processed_text:
            result[word] += 1

    #turning data into a json file
    json_result = json.dumps(result)

    #returning data
    return json_result

if __name__ == '__main__':
    main()
