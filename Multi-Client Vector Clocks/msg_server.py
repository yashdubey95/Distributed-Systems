# Name: Yash Shreesh Dubey
# UTA ID: 1001670330

# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 15:26:15 2020
@author: yashd
"""


#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import json
from time import sleep

names_dict = {'A': 'Disconnected', 'B': 'Disconnected', 'C': 'Disconnected'} # Initially Populated User Dictionary

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_serv.py"""
    while True:
        client, client_address = SERVER.accept() # Accepting a Connection
        print("%s:%s has connected." % client_address)
        client.send(bytes("Greetings from the cave! Now type your name and press enter!", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start() # Creating another sub-thread


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_serv.py"""
    global names_dict # Stores the USer Status
    flag = True # Flag to keep the appropriate flow of the program.
    while flag:
        flag = False
        name = client.recv(BUFSIZ).decode("utf8") # Gets the name of the Clients
        if name in names_dict: # Check if Username is valid or not
            if names_dict[name] == 'Disconnected': # Check if the Username is already Connected or not
                names_dict[name] = 'Connected'
                welcome = '\nWelcome %s! If you ever want to quit, type {quit} to exit.' % name
                Thread(target=handle_conn, args=(client,name,welcome)).start() # Creating a sub-thread
            else:
                alert = '\nClient %s is already Connected! Please try a different Name...' % name
                client.send(bytes(alert,"utf8"))
                flag = True
                continue
                
        else:
            alert = '\nThe Username %s is not a Valid one! Please select the Username: A, B or C.' % name
            client.send(bytes(alert,"utf8"))
            flag = True
            continue

    
            
def handle_conn(client,name,welcome):
    """ Sub Function belonging to the handle_client() """
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_serv.py"""
    global names_dict
    print(name)
    client.send(bytes(welcome, "utf8"))
    msg = "\n%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    client.send(bytes('Name', 'utf8'))
    sleep(1)            
    client.send(bytes(name, 'utf8'))
    clients[client] = name # Store name of the respective user for this client.
    client_names.delete(0,tkinter.END)
    for key in names_dict:
        client_names.insert(tkinter.END, '{}: {}'.format(key, names_dict[key])) # Updating the User Status
    broadcast(bytes('Available', 'utf8'))
    b = json.dumps(names_dict).encode('utf-8') # Sending the USer Status to the Client
    brodacast_names(b)
    
    while True:
        if all(x=='Connected' for x in names_dict.values()): # Check if all the clients are Connected/Active
            msg = client.recv(BUFSIZ).decode('utf8') # Receive Messages from Clients
            
            if msg == "{quit}": # If the Client inputs {quit} the connection will be disconnected
                client.close() # Close the Connection
                del clients[client]
                names_dict[name] = 'Disconnected' # Update the Dictionary
                
                client_names.delete(0,tkinter.END)
                for key in names_dict:
                    client_names.insert(tkinter.END, '{}: {}'.format(key, names_dict[key])) # Display the current user status on GUI
                extra = 19 - utf8len('Available') # Amount of Extra Padding Required
                pad = '\n' * extra # Padding
                broadcast(bytes('Available'+ pad, 'utf8'))
                b = json.dumps(names_dict) # Creating a Json Dump of the current state of names_dict to broadcast to clients
                extra = 63 - utf8len(b) # Amount of Extra Padding Required
                brodacast_names(bytes(b+pad, 'utf8'))
                break
            
            else:
                print(msg)
                server_vector_clock = json.loads(msg) # Loading the vector clock and receipient received from the client
                print('server_vector_clock', server_vector_clock[0], type(server_vector_clock[0]), server_vector_clock[1], type(server_vector_clock[1]))
                for key, value in clients.items(): 
                    if server_vector_clock[0] == value: # Finding the port address for the receiving client.  
                        oto_client = key
                
                stoc_vec_clock = [name, server_vector_clock[1]] # Creating a data structure to send vector clock to its intended receipient
                extra = 19 - utf8len('{}'.format(stoc_vec_clock)) # Amount of Extra Padding Required
                pad = '\n' * extra # Padding
                sleep(0.5)
                oto_client.sendall(bytes(json.dumps(stoc_vec_clock)+ pad, 'utf8')) # Sending the vector clock
                msg_list.insert(tkinter.END, '\n{}: {} ==> {}'.format(name, server_vector_clock[1], server_vector_clock[0])) # Printing the Transaction on Server GUI
            
def utf8len(s):
    return len(s.encode('utf-8')) # Returns the size in bytes of a string.

def brodacast_names(msg): #  Function to Broadcast the current User Status
    for sock in clients:
        sock.send(msg)

def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_serv.py"""

    for sock in clients:
        sock.sendall(bytes(prefix, "utf8")+msg)

""" Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_serv.py"""
""" Code Referenced From: https://www.tutorialspoint.com/python/python_gui_programming.htm """
        
# Message Server GUI Code USing Tkinter Library

clients = {}
addresses = {}

HOST = ''
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

top = tkinter.Tk()
top.title("Chatter")

client_label = tkinter.Label(top, text = 'Messages: \t \t \t User Status:')
client_label.pack()

messages_frame = tkinter.Frame(top)
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Text(messages_frame, height=15, width=30, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT)
msg_list.pack()
messages_frame.pack()
client_names = tkinter.Listbox(messages_frame, height=15, width=30)
client_names.pack()

for key in names_dict:
        client_names.insert(tkinter.END, '{} \t : {}'.format(key, names_dict[key]))



if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    tkinter.mainloop()
    ACCEPT_THREAD.join()
    
    SERVER.close()
    