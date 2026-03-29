"""
Author: Alfred Ranz Navarro
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""


# TODO: Import the required modules (Step ii)
# socket, threading, sqlite3, os, platform, datetime
import socket
import threading
import sqlite3
import os
import platform
import datetime



# TODO: Print Python version and OS name (Step iii)
print("node: ", platform.node())
print("os: ", platform.python_version())


# TODO: Create the common_ports dictionary (Step iv)
# Add a 1-line comment above it explaining what it stores
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}

DB_NAME = "scan_history.db"
# this dictionary contains ports usually found in devices. Each port lets us differentiate between different kinds of traffic such as where emails or webpages go and come from.

# TODO: Create the NetworkTool parent class (Step v)
# - Constructor: takes target, stores as private self.__target
# - @property getter for target
# - @target.setter with empty string validation
# - Destructor: prints "NetworkTool instance destroyed"
class NetworkTool:
    def __init__(self, target):
        self.__target = target

    @property
    def target(self):
        return self.__target
    
    @target.setter
    def target(self, target):
        if(target.strip()):
            self.__target = target
            print("Successful variable set!")
        else:
            print("Error: Target cannot be empty!")
    def __del__(self):
        print("Network instance destroyed.")
# Q3: What is the benefit of using @property and @target.setter?
# TODO: Your 2-4 sentence answer here... (Part 2, Q3)
# ------ ANSWER -------
# @property and @target.setter allows us to have a cleaner syntax while implementing getters and setters.
# In Java, when accessing variables such as the example above, the way to do it is to create methods and then
# call those methods everytime you use them in code. However, this creates a clutter and makes your code harder
# to debug in the future. The pythonic way to do it, referring to the Zen of python, is that 'simple is better
# than complex'. Through @property and @target.setter, we are able to access the class variables by using a 
# dot operator and then the variable.
# ---------------------

# Q1: How does PortScanner reuse code from NetworkTool?
# TODO: Your 2-4 sentence answer here... (Part 2, Q1)

# TODO: Create the PortScanner child class that inherits from NetworkTool (Step vi)
# - Constructor: call super().__init__(target), initialize self.scan_results = [], self.lock = threading.Lock()
# - Destructor: print "PortScanner instance destroyed", call super().__del__()
class PortScanner(NetworkTool):

    def __init__(self, target):
        super().__init__(target)
        self._target = target
        self.scan_results = []
        self.lock = threading.Lock()

    def __del__(self):
        super().__del__()

    


# - scan_port(self, port):
#     Q4: What would happen without try-except here?
#     TODO: Your 2-4 sentence answer here... (Part 2, Q4)
#     ------- ANSWER --------
#       Without a try-except at this part of the code, errors thrown when doing operations on the socket
#       will not be caught. For example, if socket.connect.ex(...) does not connect to the port successfully,
#       the program will crash instead of handling the error gracefully. 
#     -----------------------
#     - try-except with socket operations
#     - Create socket, set timeout, connect_ex
#     - Determine Open/Closed status
#     - Look up service name from common_ports (use "Unknown" if not found)
#     - Acquire lock, append (port, status, service_name) tuple, release lock
#     - Close socket in finally block
#     - Catch socket.error, print error message
    def scan_port(self, port):
            try: 
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.target, port))
                
                if result == 0:
                    status = "Open"
            
                else:
                    status = "Closed"
                
                service_name = common_ports.get(port, "Unknown")

                with self.lock: 
                    self.scan_results.append((port, status, service_name))
                        
            except socket.error: 
                print(f"Error scanning port {port}: {e}")
            finally: 
                sock.close()
# - get_open_ports(self):
#     - Use list comprehension to return only "Open" results
    def get_open_ports(self):
        return [col for col in self.scan_results if col[1] == "Open"]
#     Q2: Why do we use threading instead of scanning one port at a time?
#     TODO: Your 2-4 sentence answer here... (Part 2, Q2)
#       ------- ANSWER -------
#       With threading, tasks are done side by side instead of the usual sequential way. 
#       By using threading to scan multiple ports in one go, the time to perform everything 
#       becomes shortened ultimately compared to scanning port by port
#       ----------------------
    
# - scan_range(self, start_port, end_port):
#     - Create threads list
#     - Create Thread for each port targeting scan_port
#     - Start all threads (one loop)
#     - Join all threads (separate loop)
    def scan_range(self, start_port, end_port):
        try: 
            threads = []
            for port in range(start_port, end_port+1):
                t = threading.Thread(target=self.scan_port, args=(port, ))
                threads.append(t)
            
            for t in threads:
                t.start()
            for t in threads: 
                t.join()
        except Exception as e:
            print(f"Error! {e}")


# TODO: Create save_results(target, results) function (Step vii)
# - Connect to scan_history.db
# - CREATE TABLE IF NOT EXISTS scans (id, target, port, status, service, scan_date)
# - INSERT each result with datetime.datetime.now()
# - Commit, close
# - Wrap in try-except for sqlite3.Error
def save_results(target, results):
    conn = None
    try: 
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans ( 
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT,
                    port INTEGER,
                    status TEXT,
                    service TEXT,
                    scan_date TEXT
            )
                    """)
        
        for result in results:
            data = (target, *result, str(datetime.datetime.now()))
            cursor.execute("""
            INSERT INTO scans(target, port, status, service, scan_date) VALUES (?, ?, ?, ?, ?)
                        """, data)
        conn.commit()
        
        cursor.close()
    except sqlite3.Error as err: 
        print(f"Error! {err}")
    finally:
        conn.close()
        

# TODO: Create load_past_scans() function (Step viii)
# - Connect to scan_history.db
# - SELECT all from scans
# - Print each row in readable format
# - Handle missing table/db: print "No past scans found."
# - Close connection
def load_past_scans():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM scans
                   """)
    results = cursor.fetchall()
    if not results:
        print("No past scans found.")
    else:
        for result in results: 
            print(f"[{result[4]}] {result[0]}: Port {result[1]} {result[3]}")
    cursor.close()
    conn.close()
    


# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    # TODO: Get user input with try-except (Step ix)
    # - Target IP (default "127.0.0.1" if empty)
    # - Start port (1-1024)
    # - End port (1-1024, >= start port)
    # - Catch ValueError: "Invalid input. Please enter a valid integer."
    # - Range check: "Port must be between 1 and 1024."
    try:
        target_ip = input("Enter Target IP Address: ")
        start_port = int(input("Enter Start Port: "))
        end_port = int(input("Enter End Port: "))
        # Fixed - use or
        if start_port > 1024 or start_port < 1 or end_port > 1024 or end_port < 1:
            raise ValueError("Port must be between 1 and 1024.")
    except ValueError as e: 
        print(f"Error: {e}")
    except IndexError as e: 
        print(f"Error: Ports must be between 1 and 1024!")
    
        
    # TODO: After valid input (Step x)
    # - Create PortScanner object
    # - Print "Scanning {target} from port {start} to {end}..."
    # - Call scan_range()
    # - Call get_open_ports() and print results
    # - Print total open ports found
    # - Call save_results()
    # - Ask "Would you like to see past scan history? (yes/no): "
    # - If "yes", call load_past_scans()
    scanner = PortScanner(target_ip)
    print(f"Scanning {target_ip} from port {start_port} to {end_port }")
    scanner.scan_range(start_port, end_port)
    ports = scanner.get_open_ports()
    print(f"----- Scan Results for {target_ip} -------")
    count = 0
    for port, status, service_name in scanner.scan_results: 
        print(f"Port {port}: {status} ({service_name})")
        if status == "Open":
            count+=1
    print(f"Total open ports found: {count}")
    save_results(target_ip, scanner.scan_results)
    
    while True:
        try:
            choice = input("Would you like to see results? ")
            if choice in ("no", "No"):
                break
            if choice not in ("yes", "Yes"):
                raise ValueError("Type yes or no")
            load_past_scans()
        except ValueError as e:
            print(f"Error: {e}")


# Q5: New Feature Proposal
# TODO: Your 2-3 sentence description here... (Part 2, Q5)
#   ------ ANSWER -------
#   I think one good feature we could add to this project is to also show 
#   what the ports are doing, whether they are used in another app.
#   This quickly resolves the problem I encountered when writing the assignment
#   where I had received mostly closed ports and wasn't sure why I did not have
#   any open ports anywhere.
#   ---------------------
# Diagram: See diagram_studentID.png in the repository root