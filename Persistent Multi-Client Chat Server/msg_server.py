# Name: Yash Shreesh Dubey
# UTA ID: 1001670330

# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 16:55:59 2020

@author: yashd
"""


#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import json
import collections
from datetime import datetime
import pickle

names_dict = {'Yash': 'Disconnected', 'Vrushabh': 'Disconnected'} # Initially Populated User Dictionary
main_message_queue = collections.defaultdict(list) # Messaging Queue Created by the Server of the structure Key = Client Name and Value = List containing a list of Messages

try:
    dbfile = open('mainMessageQueuePickle', 'rb')  # Opening the Pickle File that contains the saved state of Messaging Queue    
    main_message_queue = pickle.load(dbfile) # Loading the Messaging Queue From the Pickle File
    dbfile.close()

except:
    pass

def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_serv.py"""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Greetings from the cave! Now type your name and press enter!", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_serv.py"""
    global names_dict # Stores the USer Status
    global main_message_queue
    flag = True # Flag to keep the appropriate flow of the program.
    while flag:
        flag = False
        name = client.recv(BUFSIZ).decode("utf8")
        if name in names_dict:
            if names_dict[name] == 'Disconnected':
                names_dict[name] = 'Connected'
                main_message_queue[name]
                welcome = '\nWelcome %s! If you ever want to quit, type {quit} to exit.' % name
                Thread(target=handle_conn, args=(client,name,welcome,main_message_queue)).start()
            else:
                welcome = '\nClient %s is already Connected! Please try a different Name || If you ever want to quit, type {quit} to exit.' % name
                client.send(bytes(welcome,"utf8"))
                client.send(bytes('Duplicate',"utf8"))
                flag = True
                continue
                
        else:
            names_dict[name] = 'Connected'
            main_message_queue[name]
            welcome = '\nWelcome %s! If you ever want to quit, type {quit} to exit.' % name
            Thread(target=handle_conn, args=(client,name,welcome,main_message_queue)).start()

    
            
def handle_conn(client,name,welcome,main_message_queue):
    """ Sub Function belonging to the handle_client() """
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_serv.py"""
    global names_dict
    print(name)
    client.send(bytes(welcome, "utf8"))
    msg = "\n%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name
    client_list.delete(0,tkinter.END)
    for key in names_dict:
        client_list.insert(tkinter.END, '{}: {}'.format(key, names_dict[key])) # Updating the User Status
    broadcast(bytes('Available', 'utf8'))
    b = json.dumps(names_dict).encode('utf-8') # Sending the USer Status to the Client
    brodacast_names(b)
    
    flag = True # Another Flag for Appropriate Flow
    while True:
        
        if flag:    # First Prompting the User to make a Choice between Sending or Checking Messages.
            client.send(bytes('\nSelect one of the two or type {quit} if Done:', 'utf8'))
            client.send(bytes('\n1. Send Messages', 'utf8'))
            client.send(bytes('\n2. Check Messages', 'utf8'))
            msg = client.recv(BUFSIZ)
            flag = False
        
        elif msg == bytes('1', 'utf8'): # If the User Selects Sending Prompt the for Selecting One of the Methods: Unicast, Multicast or Broadcast
            client.send(bytes('\nA. 1 -to- 1', 'utf8'))
            client.send(bytes('\nB. 1 -to- N', 'utf8'))
            client.send(bytes('\nC. 1 -to- all', 'utf8'))
            msg = client.recv(BUFSIZ)
        
        elif msg == bytes('2','utf8'): # If the User Selects Checking
            if not main_message_queue[name]: # Check if the Messaging Queue is Empty for that User
                client.send(bytes('\nThere Are No New Messages to Show', 'utf8'))
                flag = True
            else:
                for message in main_message_queue[name]: # If not empty; Loop through the messages and Display them one by one on the Client Window
                    transmit = '\n<%s> %s: %s' % (message[0].ctime(), message[1], message[2].decode('ASCII'))
                    client.send(bytes(transmit, 'utf8'))
                main_message_queue[name] = [] # Empty the Messaging Queue for that User after Displaying the Messages.
                flag = True
                
        
        elif msg == bytes("{quit}", "utf8"): # If the Client inputs {quit} the connection will be disconnected
            dbfile = open('mainMessageQueuePickle', 'wb') # Opening the Pickle file

            pickle.dump(main_message_queue, dbfile) # Saving the Current State of the Messaging Queue in the Pickle File after a Client has Left the Server.  
            dbfile.close()
            
            client.close()
            del clients[client]
            names_dict[name] = 'Disconnected'
            broadcast(bytes("\n%s has left the chat." % name, "utf8"))
            client_list.delete(0,tkinter.END)
            for key in names_dict:
                client_list.insert(tkinter.END, '{}: {}'.format(key, names_dict[key]))
            broadcast(bytes('Available', 'utf8'))
            b = json.dumps(names_dict).encode('utf-8')
            brodacast_names(b)
            break
        
        elif msg == bytes('A', 'utf8'):
            """ Function for Unicast """
            client.send(bytes('\nSelect a User to Send Message: ', 'utf8'))
            user = client.recv(BUFSIZ)
            client.send(bytes('\nReady to Unicast: ', 'utf8'))
            unicast_msg = client.recv(BUFSIZ)
            
            if user.decode('ASCII') in names_dict:
                main_message_queue[user.decode('ASCII')].append([datetime.now(),name,unicast_msg])
            else:
                notif = '\nNo Record Found of User %s in the User Database ' % user.decode('ASCII') 
                client.send(bytes(notif,'utf8'))
               
#            print(main_message_queue)
            flag = True
            
        elif msg == bytes('B', 'utf8'):
            """ Function for Multicast """
            client.send(bytes('\nSelect Users to Send Message: ', 'utf8'))
            user = client.recv(BUFSIZ).decode('ASCII')
            client.send(bytes('\nReady to Multicast: ', 'utf8'))
            multicast_msg = client.recv(BUFSIZ)

            user_list = user.split(" ")

            for user in user_list:
                if user in names_dict:
                    main_message_queue[user].append([datetime.now(),name,multicast_msg])
                else:
                    notif = '\nNo Record Found of User %s in the User Database ' % user.decode('ASCII') 
                    client.send(bytes(notif,'utf8'))
#            print(main_message_queue)        
            flag = True
        
        elif msg == bytes('C', 'utf8'):
            """ Function for Broadcast """
            client.send(bytes('\nReady to Broadcast: ', 'utf8'))
            broadcast_msg = client.recv(BUFSIZ)
            for user in names_dict.keys():
                if name != user:
                    main_message_queue[user].append([datetime.now(),name,broadcast_msg])
#            print(main_message_queue)        
            flag = True
        
        else:
            client.send(bytes('\nPlease Select a Correct Option or Type {quit} if Done','utf8'))
            flag = True

        

def brodacast_names(msg):
    for sock in clients:
        sock.send(msg)

def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_serv.py"""

    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)

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
top.title("Server")
top.geometry("320x320") 

lbl = tkinter.Label(top,text = "Displaying Users and their Status:") 
scrollbar = tkinter.Scrollbar(top)
client_list = tkinter.Listbox(top, height= 800, width = 160, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
lbl.pack()
client_list.pack()

for key in names_dict:
        client_list.insert(tkinter.END, '{} \t : {}'.format(key, names_dict[key]))



if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    tkinter.mainloop()
    ACCEPT_THREAD.join()
    
    SERVER.close()
    