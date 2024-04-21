import socket
import datetime
import threading
import time

client_data = {}

def startReceivingClockTime(connector, address):
    while True:
        try:
            # Receive clock time from a connected client
            clock_time_string = connector.recv(1024).decode().strip()
            
            if clock_time_string:
                clock_time = datetime.datetime.strptime(clock_time_string, "%Y-%m-%d %H:%M:%S.%f")

                # Calculate time difference with server's current time
                clock_time_diff = datetime.datetime.now() - clock_time

                # Update client data dictionary
                client_data[address] = {
                    "clock_time": clock_time,
                    "time_difference": clock_time_diff,
                    "connector": connector
                }

                print(f"Client Data updated with: {address}, Clock Time: {clock_time}")

            else:
                print(f"Received empty or invalid clock time from {address}")

        except ValueError as e:
            print(f"Error decoding clock time from {address}: {e}")
        except ConnectionError as e:
            print(f"Connection error with client {address}: {e}")

        time.sleep(10)



def startConnecting(master_server):
    while True:
        # Accept incoming connections from clients
        master_slave_connector, addr = master_server.accept()
        slave_address = f"{addr[0]}:{addr[1]}"
        print(f"Connected with client: {slave_address}")

        # Start a thread to receive clock time from this client
        thread = threading.Thread(target=startReceivingClockTime, args=(master_slave_connector, slave_address))
        thread.start()

def getAverageClockDiff():
    time_difference_list = [client["time_difference"] for client in client_data.values()]
    sum_of_clock_difference = sum(time_difference_list, datetime.timedelta(0))

    if len(client_data) > 0:
        average_clock_difference = sum_of_clock_difference / len(client_data)
        return average_clock_difference
    else:
        return datetime.timedelta(0)

def synchronizeAllClocks(sync_delay=10):
    while True:
        print("New synchronization cycle started.")
        print(f"Number of clients to be synchronized: {len(client_data)}")

        # Calculate the average clock difference
        average_clock_difference = getAverageClockDiff()

        if average_clock_difference:
            # Calculate synchronized time using the average clock difference
            print("Calculating synchronized time...")
            synchronized_time = datetime.datetime.now() + average_clock_difference

            # Print and broadcast synchronized time to all connected clients
            print(f"Global Synchronized Time: {synchronized_time}")
            for client_addr, client in client_data.items():
                try:
                    client['connector'].send(str(synchronized_time).encode())
                    print(f"Synchronized time sent to client {client_addr}")
                except Exception as e:
                    print(f"Error sending synchronized time to {client_addr}: {e}")

        else:
            print("No clients connected. Synchronization not applicable.")

        print("\n")

        # Introduce a delay before the next synchronization cycle
        time.sleep(sync_delay)


def printGlobalTime():
    while True:
        # Print the current synchronized time of the master node
        global_synchronized_time = datetime.datetime.now() + getAverageClockDiff()
        print(f"Current Global Synchronized Time: {global_synchronized_time}")
        time.sleep(10)  # Adjust the interval for printing the time

def initiateClockServer(port=8081):
    master_server = socket.socket()
    master_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    master_server.bind(('', port))
    master_server.listen(10)

    print("Clock server started...")
    print(f"Listening for connections on port {port}\n")

    # Start a thread to accept client connections
    connect_thread = threading.Thread(target=startConnecting, args=(master_server,))
    connect_thread.start()

    # Start a thread for synchronization
    sync_thread = threading.Thread(target=synchronizeAllClocks)
    sync_thread.start()

    # Start a thread to print the global synchronized time
    print_thread = threading.Thread(target=printGlobalTime)
    print_thread.start()

if __name__ == '__main__':
    initiateClockServer()