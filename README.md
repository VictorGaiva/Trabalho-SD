# Trabalho-SD
##How to test
Run the worker.py script passing a file with a list of avaiable ports
```sh
python3 worker.py workers.csv
```
You can start as many workers as there is in the list of avaiable ports

Now you need to start the master node. To do that you must run the script and give it the same file with the avaiable ports so it can now where to look for workers
```sh
python3 master.py workers.csv
```
The default port the master is listening for incoming requests through the network is 12339

You can tell the master to do somethings like pinging the workers, test them and kill them. The commands are listed when you start the script.

##DO NOT
Don't kill the master with CTRL+C when it tells it is going to try binding to the port again in a few seconds.

You either press CTRL+C once or give it the exit command and wait. After 5 seconds it will shutdown
