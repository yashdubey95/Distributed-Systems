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

names_dict = {'Yash': 'Disconnected', 'Vrushabh': 'Disconnected'} # Initially Populated User Dictionary


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
    flag = True # Flag to keep the appropriate flow of the program.
    while flag:
        flag = False
        name = client.recv(BUFSIZ).decode("utf8")
        if name in names_dict:
            if names_dict[name] == 'Disconnected':
                names_dict[name] = 'Connected'
                welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
                Thread(target=handle_conn, args=(client,name,welcome)).start()
            else:
                welcome = 'Client %s is already Connected! Please try a different Name || If you ever want to quit, type {quit} to exit.' % name
                client.send(bytes(welcome,"utf8"))
                client.send(bytes('Duplicate',"utf8"))
                flag = True
                continue
                
        else:
            names_dict[name] = 'Connected'
            welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
            Thread(target=handle_conn, args=(client,name,welcome)).start()

    
            
def handle_conn(client,name,welcome):
    """ Sub Function belonging to the handle_client() """
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_serv.py"""
    global names_dict
    
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name
    print(clients)
    client_list.delete(0,tkinter.END)
    for key in names_dict:
        client_list.insert(tkinter.END, '{}: {}'.format(key, names_dict[key])) # Updating the User Status
#    client_list.insert(tkinter.END, names_dict)
    broadcast(bytes('Available', 'utf8'))
    b = json.dumps(names_dict).encode('utf-8') # Sending the USer Status to the Client
    brodacast_names(b)
    
    flag = True # Another Flag for Appropriate Flow
    while True:
        
        msg = client.recv(BUFSIZ) # Accepts the Client Message Stream
        if flag:
            client.send(bytes('Select one of the three or Quit if Done:', 'utf8'))
            client.send(bytes('\n A. 1 -to- 1', 'utf8'))
            client.send(bytes('\n B. 1 -to- N', 'utf8'))
            client.send(bytes('\n C. 1 -to- all', 'utf8'))
            flag = False
            continue
        
        if msg == bytes("{quit}", "utf8"): # If the Client inputs {quit} the connection will be disconnected
            print('Quit')
            client.close()
            del clients[client]
            names_dict[name] = 'Disconnected'
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            client_list.delete(0,tkinter.END)
            for key in names_dict:
                client_list.insert(tkinter.END, '{}: {}'.format(key, names_dict[key]))
#            client_list.insert(tkinter.END, names_dict)
            broadcast(bytes('Available', 'utf8'))
            b = json.dumps(names_dict).encode('utf-8')
            brodacast_names(b)
            break
        
        elif msg == bytes('A', 'utf8'):
            """ Function for Unicast """
            client.send(bytes('Select a User to Send Message: ', 'utf8'))
            user = client.recv(BUFSIZ)
            client.send(bytes('Ready to Unicast: ', 'utf8'))
            unicast_msg = client.recv(BUFSIZ)
            print(user)
            print(clients)
            print(type(clients))
            for key, value in clients.items(): 
                 if user == bytes(value,'utf8'): 
                     oto_client = key
            
            try:
                print(name)
                
                oto_client.send(bytes(name+": ",'utf8')+unicast_msg)
                client.send(bytes(name+": ",'utf8')+unicast_msg)
            except:
                notif = 'The User %s is Not Active Currently' % user.decode('ASCII') 
                client.send(bytes(notif,'utf8'))
                
            flag = True
            continue
            
        elif msg == bytes('B', 'utf8'):
            """ Function for Multicast """
            client.send(bytes('Select Users to Send Message: ', 'utf8'))
            user = client.recv(BUFSIZ).decode('ASCII')
            client.send(bytes('Ready to Multicast: ', 'utf8'))
            multicast_msg = client.recv(BUFSIZ)
            print(user)
            user_list = user.split(" ")
            print(user_list)
            oton_clients = []
            for user in user_list:
                for key, value in clients.items(): 
                     if user == value: 
                         oton_clients.append(key)
            
            oton_users = []
            
            for sock in oton_clients:
                print(clients[sock])
                oton_users.append(clients[sock])
                sock.send(bytes(name+": ",'utf8')+multicast_msg)
            
            client.send(bytes(name+": ",'utf8')+multicast_msg)
    
            rem_list = list(set(user_list)-set(oton_users))
            print('Rem_list',rem_list)
            if len(rem_list) > 0:
                notif = 'The User(s) {} is/are Not Active Currently'.format(rem_list)
                client.send(bytes(notif,'utf8'))
            flag = True
            continue
        
        elif msg == bytes('C', 'utf8'):
            client.send(bytes('Ready to Broadcast: ', 'utf8'))
            msg = client.recv(BUFSIZ)
            broadcast(msg, name+": ")
            flag = True
        else:
            client.send(bytes('Please Select a Correct Option or Quit if Done'))
            flag = True
            continue
    


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
client_list = tkinter.Listbox(top, height= 1600, width = 160, yscrollcommand=scrollbar.set)
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
    