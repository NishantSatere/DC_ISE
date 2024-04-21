from timeit import default_timer as timer
from dateutil import parser
import threading
import datetime
import socket 
import time

# List of server addresses and ports to attempt connection
SERVER_ADDRESSES = [
    ('127.0.0.1', 8080),  # Primary server
    ('127.0.0.1', 8081),  # Backup server 1
    ('127.0.0.1', 8082)   # Backup server 2 (example)
]

# client thread function used to send time at client side
def startSendingTime(slave_client):
    while True:
        try:
            # Get local time before sending to server
            local_time = datetime.datetime.now()
            
            # Provide server with clock time at the client
            slave_client.send(str(local_time).encode())
            print("Local time sent to server:", local_time)
            print("Recent time sent successfully\n")

        except ConnectionError as e:
            print(f"Error sending local time to server: {e}")
            # Handle connection error by attempting to reconnect to another server
            slave_client = reconnectToServer()

        time.sleep(10)


# client thread function used to receive synchronized time
def startReceivingTime(slave_client):
    while True:
        try:
            # Receive synchronized time from the server
            synchronized_time_str = slave_client.recv(1024).decode()
            synchronized_time = parser.parse(synchronized_time_str)

            print("Synchronized time at the client is:", synchronized_time)

        except ValueError as e:
            print(f"Error decoding synchronized time: {e}")
        except ConnectionError as e:
            print(f"Error receiving synchronized time from server: {e}")
            # Handle connection error by attempting to reconnect to another server
            slave_client = reconnectToServer()

        time.sleep(10)


# Function to reconnect to server using the next available address and port
def reconnectToServer():
    for address, port in SERVER_ADDRESSES:
        try:
            print(f"Attempting to connect to server {address}:{port}")
            slave_client = socket.socket()		 
            slave_client.connect((address, port))
            print(f"Successfully connected to server {address}:{port}")
            return slave_client
        except ConnectionError as e:
            print(f"Connection failed to server {address}:{port}: {e}")
            continue
    
    print("All servers are currently unreachable.")
    return None


# function used to Synchronize client process time
def initiateSlaveClient():
    slave_client = None
    while not slave_client:
        slave_client = reconnectToServer()

    # Start sending local time to server
    print("Starting to send local time to server")
    send_time_thread = threading.Thread(target=startSendingTime, args=(slave_client,))
    send_time_thread.start()

    # Start receiving synchronized time from server
    print("Starting to receive synchronized time from server")
    receive_time_thread = threading.Thread(target=startReceivingTime, args=(slave_client,))
    receive_time_thread.start()


# Driver function
if __name__ == '__main__':
    # Initialize the Slave / Client
    initiateSlaveClient()
