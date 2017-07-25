#worker-script
import os,sys   #system related task
import socket   #for socket communication

import socket   #for network communication
import cPickle  #for sending and receiving objects
import json     #for sending and receiving objects

processedRequestsCount = 0
masterKey = -1

def main():
	#init
	processedRequestsCount = 0
	masterKey = -1
	workerPort = getWorkerPort()
	
	#getting the socket
	workerSocket = getSocket(workerPort)

	#start receiving requests
	while True:
		#accept connection
		workerSocket.listen(1)
		(masterSocket, address) = workerSocket.accept()
		#start processing it
		if(processRequest(masterSocket) == -1):
			#received shutdown flag
			print(str(workerPort) + ":Master node requested for shutdown. bye")
			workerSocket.close()
			break
		else:
			processedRequestsCount += 1
			#print("Processed one request from master. " + str(processedRequestsCount) + " so far.")
	return

def processRequest(masterSocket):
	#data_string = json.dumps(data) #data serialized
	#data_loaded = json.loads(data) #data loaded
	#receive data
	receivedDataBuffer = ""
	while 1:
		dataChunk = masterSocket.recv(1024)
		#if end of transmition
		if not dataChunk: break
		#concatenate data to buffer
		receivedDataBuffer += dataChunk
	#closing socket
	masterSocket.close()

	#processing request
	receivedDict = json.loads(receivedDataBuffer)

	#error prevention
	if(not receivedDict):
		print(str(workerPort) + ":Error. Received object is " + type(receivedDict))
		return 0
	else:
		#shutdown signal
		if(receivedDict["Action"] == "SHUTDOWN"):
			return -1
		if(receivedDict["Action"] == "PING"):
			print(str(workerPort) + ":" + receivedDict["Data"])
	return 1

#returns the worker port from the given argument
def getWorkerPort():
	#Checking argument
	if(len(sys.argv) != 2):
		print("Missing work port number.\nUsage:\t$" + sys.argv[0]+" <port>")
		exit(-1)
	#Checking argument type
	try:
		workerPort = int(sys.argv[1])
	except Exception as e:
		print("Argument must be a number.\nUsage:\t$" + sys.argv[0]+" <port>")
		exit(-1)
	return workerPort

#returns a socket binded to given port
def getSocket(workerPort):
	#opening the socket
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Commom TCP socket
	try:
		#binding to the right port
		serversocket.bind(('localhost', workerPort))
	except Exception as e:
		print("\nFailed to bind to port " + str(workerPort))
		exit(-1)
	#return that shit
	return serversocket

def newRequestDict(Action, Source, Field1, Field2, Data):
	returnDict = {}
	returnDict["Action"] = Action #[ "RESIZE" | "SHUTDOWN" | "PING"]
	returnDict["Source"] = Source #[ $URL | 'DATA' | $KEY ]
	returnDict["Field1"] = Field1 #[ '' | $TARGET_WIDTH]
	returnDict["Field2"] = Field2 #[ '' | $TARGET_HEIGHT]
	returnDict["Data"]   = Data   #[ '' | $PING_DATA |$IMAGE]
	return returnDict

if __name__ == '__main__':
	main()
