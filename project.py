import threading
import sys
import types
import re
import time
import socket
import selectors


from typing import Dict
import argparse
import os
import sys

#consts

FORMAT = "utf-8"


connection_id_position = 0

parser = argparse.ArgumentParser()

parser.add_argument("--serverport", type = int, default = 1234, dest = "serverport", help = "The port needed for input")

parser.add_argument("--verbose", action = "store_true", help = "Toggle switch")

args = parser.parse_args()




def user_interface_display(): 

    print("\nChat Application User Interface & Available Commands")
    print("\n\nExpected input: Numbers 1-8:")

    print("\n1 - help: Displays list of commands along with brief explanation.")
    
    print("\n2 - myip: Displays IP Address of this program's device.")
    
    print("\n3 - myport: Displays the port of which the current program is listening to.")
    
    print("\n4 - connect <destination> <port no>: Attempts to establish a TCP connection")
    print("\n    given an IP Address(destination) and port number(port no). Success or ")
    print("\n    failure of this command will be displayed on both ends of this program.")
    
    print("\n5 - list: Displays a list containing all connections involving this program.")
    
    print("\n6 - terminate <connection id>: Command ends connection given the connection")
    print("\n    number. Format: [6 2] will end the 2nd connnection.")
    
    print("\n7 - send <connection id> <message>: Format: [7 2 Hello] will attempt to send")
    print("\n    the message to the device with the 2nd connection.")

    print("\n8 - exit: Command will close all connections and exit the program.")




def get_IP_Address(): 

    #collect ip address and compare it to default, if it is not then return the ip address 

    try:

        host_name = socket.gethostname()

        ip_address = socket.gethostbyname(host_name)

        default_address = '127.0.0.1'

        if ip_address is not default_address:

            return ip_address
    
    except:

        print("\nError detecting IP Address of current device.")




def get_ServerPort():  


    #initial_server_port = 2222
    
    #if len(sys.argv) != 2:

    #print(len(sys.argv))

    if args.verbose:

        initial_server_port = sys.argv[2]   #store port number in variable and return it

    elif not args.verbose:

        if not 1 < len(sys.argv) <= 3:
            
            #want to collect 2 interesting elements from terminal, port number needed

            print("\nIncorrect input.")

            #exit()

            initial_server_port = sys.argv[1]   #store port number in variable and return it 

    initial_server_port = args.serverport
    
    return initial_server_port




def initialize_server(_ip_address, _port_number, list_of_connections): 

    server_socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #socket object IPv4, TCP    

    server_socket_obj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #allows for the address to be reused so that the server socket can bind to the port/address after server is deleted


    server_socket_obj.bind((_ip_address, int(_port_number)))

    #binds the server socket with the ip address and the port number CONVERTED TO INT

    server_socket_obj.listen(5)

    #server socket in listening mode so that it can accept new connections

    print(f"\nListening on IP Address: {_ip_address}      Port Number: {_port_number}")
        
    while True:
        
        #wait for a client to connect

        _client, _address = server_socket_obj.accept()

        #print a message to indicate new connection has been established

        print(f"\n\nAccepted connection from IP Address: {_address[0]}      Port Number: {_address[1]}.")

        #add new client to list of connections

        list_of_connections.append((_client, _address))

        #send a message to new client to confirm connection

        #_client.send(f"\nConnected to: {get_IP_Address()} Port Number: {get_ServerPort()}".encode())  #ERROR

        #Spawn a new thread to handle client's messages

        _ip_address = get_IP_Address()

        client_thread = threading.Thread(target = client_processing, args = (_client, _address, list_of_connections))
                                        
        client_thread.start()

        print(f"\nPlease input command: ")




def get_list(list_of_connections): 

    information_list = "\nID:\t\tIP Address:\t\tPort Number:"

    for i, (c, a) in enumerate(list_of_connections):

        information_list += f'\n{i + 1}\t\t{a[0]}\t\t{a[1]}'

    print(information_list)




def client_processing(_client, _address, list_of_connections): 

    try:

        while True:

            #receieve data from client

            data = _client.recv(1024).decode()

            #if client sends an empty message, disconnect

            if not data:

                break

            #print received message and sender interaction

            print(f"\n-------------------------")
            print(f"Message received:")
            print(f"Senders IP Address: {_address[0]}")
            print(f"Port Number: {_address[1]}")
            print(f"Message: \{data}")
            print(f"-------------------------\n")

            print("\nPlease input command: ")
    
    except ConnectionResetError:

        print(f"\nConnection with IP Address: {_address[0]}      Port Number: {_address[1]} terminated by remote host.")

        _client.close()

        try: 

            list_of_connections.remove((_client, _address))

            print(f"\nConnection with IP Address: {_address[0]}      Port Number: {_address[1]} closed.")

            print("\nPlease input command")

        except ValueError:

            pass    #no connnection found, no need to do anything

    except ConnectionAbortedError:

        pass    #need to catch error, no need to print

    except Exception as e:

        print(f"\nError has occured: {e}")

    #Make sure to close connection and remove it from list of connections

    finally:

        _client.close()

        try:

            list_of_connections.remove((_client, _address))

            print(f"\nConnection with IP Address:{_address[0]}      Port Number: {_address[1]} closed.")

            print("HERE")

        except ValueError:

            pass    #If the connections is not found




def client_connect(_ip_address, _port_number, list_of_connections):

    try:

        func_port = _port_number

    except ValueError:

        print(f"\nInvalid Port Number: {func_port}")

        return
    
    #check if connection already exists

    ip_address = get_IP_Address()

    for ipaddr, portnum in list_of_connections:

        if ip_address == ipaddr and _port_number == portnum:

            print(f"\nYou are already connected to IP Address: {_ip_address}      Port Number: {_port_number}")

            return
    
    #check if host and port correspond to self

    if _ip_address == ip_address and _port_number == get_ServerPort():

        print("\nYou cannot connect to yourself.")

        return
    
    #create a new client socket and attempt to connect to remote host

    _client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:

        print(f"\nAttempting to connect to IP Address: {_ip_address}      Port Number: {_port_number}...")

        _client.connect((_ip_address, _port_number))

    #handle errors during connect

    except (ConnectionRefusedError, TimeoutError):

        print(f"\nConnection to IP Address: {_ip_address}      Port Number: {_port_number} failed.")

        _client.close()

        return

    except socket.gaierror:

        print(f"\nInvalid IP Address: {_ip_address}")

        _client.close()

        return
    
    #add client to list of connections and spawn a thread to handle messages

    list_of_connections.append((_client, (_ip_address, _port_number)))

    #_client.send(f"\nConnected to {get_IP_Address()} : {get_ServerPort}".encode())  #ERROR

    client_thread = threading.Thread(target = client_processing, args = (_client,(_ip_address, _port_number), list_of_connections))

    client_thread.start()

    #print a message to indicate connection was successful

    print(f"\nConnected to IP Address: {_ip_address}    Port Number: {_port_number}.")




def send_message(index, message, list_of_connections):

    try:

        #get client and address associated with specified connection ID

        _client, _address = list_of_connections[index]

    except IndexError:

        print(f'\nError Sending message: Connection ID {connection_id_position} not found in list_of_connections.')

        return
    
    #prevent messages of over 100 characters

    if len(message) > 100:

        print("\nError: Message is too long. (Maximum is 100 characters.)")

        return
    
    #send the message to the client

    _client.send(f"{message}".encode())

    #print message to indicate message was sent successfully

    print(f"\nMessage sent to {index + 1}.")




def terminate_connection(connection_id_position: int, list_of_connections): 

    #check if specified connection ID is valid

    if connection_id_position < 0 or connection_id_position >= len(list_of_connections):

        print(f'\nError terminating connection: Connection ID {connection_id_position} not found in list_of_connections.')

        return
    
    #Get client and address associated with the specified connection ID

    _client, _address = list_of_connections[connection_id_position]

    #close the connection

    _client.close()

    if(_client, _address) in list_of_connections:

        list_of_connections.remove((_client, _address))

        #print message to indicate termination

        print(f"\nConnection with IP Address:{_address[0]}      Port Number: {_address} terminated.")




def cleanup(list_of_connections):

    #accesss the socket in the key pairs in list of connections and close them

    for i in list_of_connections.items():

        i[1][2].close()

        exit()




if __name__ == "__main__": 

    list_of_connections = []

    #dictionary key values

    #expected variables should be: connection ID | IP Address | Port Number | Socket Object | Connection Type (server/client)

    initial_server_port = get_ServerPort()

    initial_ip_address = get_IP_Address()

    server_thread_object = threading.Thread(target = initialize_server, args = [initial_ip_address, initial_server_port, list_of_connections])

    server_thread_object.start()

    if args.verbose:

        print("")

        #sys.stdout = open(os.devnull, 'w')

        #client_connection(initial_ip_address, int(initial_server_port), list_of_connections)

        #time.sleep(3)

        #terminate_connection("1", list_of_connections, not_terminated = True)

        #sys.stdout = sys.__stdout__
    
    time.sleep(1)

    user_interface_display()

    while True: #command interface 

        question = "\nPlease input command: "

        user_input = ""

        user_input = input(question)

        if (re.search(r"\s", user_input)):

            user_input_slice = user_input.split(" ")
        
        else:

            user_input_slice = user_input

        if user_input == "help":       #help

            user_interface_display()
        

        elif user_input == "myip":     #myip

            print("\nYour IP Address is: ", initial_ip_address)
        
        
        elif user_input == "myport":     #myport

            print(f"\nYour port is: {initial_server_port}")
        
        
        elif user_input_slice[0] == "connect":     #connect

            if args.verbose:

                ip_substring = "192.168.86.21"

                port_substring = int(initial_server_port)

                client_connect(ip_substring, port_substring, list_of_connections)
            
            else:

                ip_substring = user_input_slice[1]

                port_substring = int(user_input_slice[2])

                client_connect(ip_substring, port_substring, list_of_connections)

        

        elif user_input == "list":     #list

            get_list(list_of_connections)
        
        

        elif user_input_slice[0] == "terminate":     #terminate

            try:

                index = int(user_input_slice[1]) - 1

            except(ValueError, IndexError):

                print("\nInvalid connection ID.")

                continue

            sliced_connection_id = index  

            terminate_connection(sliced_connection_id, list_of_connections)

        

        elif user_input_slice[0] == "send":     #send

            try:
                index = int(user_input_slice[1]) - 1

            except ValueError:

                print("\nInvalid Connection ID.")

                continue

            message = " ".join(user_input_slice[2:])

            send_message(index, message, list_of_connections)

        

        elif user_input == "exit":     #exit
            
            print("\nProgram will terminate.")
            
            cleanup(list_of_connections)

            exit()

