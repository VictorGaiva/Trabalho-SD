#worker-script
import os,sys   #system related task
import socket   #for socket communication

import socket   #for network communication
import cPickle  #for sending and receiving objects
import json     #for sending and receiving objects


import csv

def main():
	#get list of workers
	Workers = getWorkers()

	while 1:
		try:
			inputData = int(raw_input("0:ping, 1:kill, 2:exit ->"))
		except KeyboardInterrupt:
			print("\nShutting master node down.")
			break
		
		if(inputData == 0):
			for Worker in Workers:
				pingWorker(Worker)
		elif(inputData == 1):
			for Worker in Workers:
				killWorker(Worker)
		elif(inputData == 2):
			print("Shutting master node down.")
			break

	#print(response)


#returns a list with the ports the workers are using !!CHANGE THIS IF IN PRODUCTION
def getWorkers():
	#Checking argument
	if(len(sys.argv) != 2):
		print("Missing filename.\nUsage:\t$" + sys.argv[0]+" <filename>")
		exit(-1)
	#Opening file
	with open(sys.argv[1], 'rb') as csvfile:
		#reading content
		spamreader = csv.reader(csvfile, delimiter=',')
		workersList = []
		#saving to list
		for row in spamreader:
			for val in row:
				workersList.append(int(val))
	#returning it
	return workersList

def pingWorker(Worker):
	#doing request
	print("Pinging worker: " + str(Worker))
	sendRequest(Worker, "PING", 1010, '', '', 'Testing.',True)

def killWorker(Worker):
	#doing request
	print("Killing worker: " + str(Worker))
	sendRequest(Worker, "SHUTDOWN", 1010, '', '', 'Testing.')


def sendRequest(Worker, Action, Source, Field1, Field2, Data, waitResponse=False):
	requestDict = newRequestDict(Action, Source, Field1, Field2, Data)
	#encapsula
	sendingData = json.dumps(requestDict)

	#opening socket
	workerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	#Setting timeout
	workerSocket.settimeout(5)
	
	#trying to connect
	try:
		workerSocket.connect(('localhost', Worker))
	except Exception as e:
		print("Failed to connect to worker on port: "+str(Worker))
		return
	
	#send data
	workerSocket.sendall(sendingData)

	receivedDataBuffer = ""
	#waiting for response if necessary
	if(waitResponse):
		try:
			#receive all data
			while 1:
				dataChunk = workerSocket.recv(1024)
				if not dataChunk: break
				print(dataChunk)
				receivedDataBuffer += dataChunk
		except socket.timeout:
			print("Worker \'" + str(Worker) + "\' did not respond after 5 seconds.")

	#closing socket
	workerSocket.close()



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