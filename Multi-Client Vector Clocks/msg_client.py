# Name: Yash Shreesh Dubey
# UTA ID: 1001670330

# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 15:25:30 2020

@author: yashd
"""


#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import json

vector_clock = [0, 0, 0] # Vector Clock Initialization
indices = {'A': 0, 'B': 1, 'C': 2} # Vector Clock Indices wrt Username 

def receive():
    """Handles receiving of messages."""
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_clnt_GUI.py """
    flag = 0 # To check if the server is sending the User Status or Just a Message
    notdisconnected = True # Flag to check if any user has disconnected in between the process
    while True:
        try:
            if flag == 0: # Regular Message
                if notdisconnected:
                    msg = client_socket.recv(BUFSIZ).decode("utf8") # Receiving Message from Server
             
                    if msg == 'Available': # Checking if the Server will send User Status next or not.
                        flag = 1
                        msg = ''
                    
                    elif msg == 'Name': # Checking if the Server will send Username next or not.
                        
                        flag = 2
                        msg = ''
                    else:
                        msg_list.insert(tkinter.END, msg) # Displaying Message on Client GUI
            elif flag == 2: # Server sending Username of the client
                name = b''
                name += client_socket.recv(BUFSIZ)
                name = name.decode('utf8')
                flag = 0
            elif flag == 1: # Server Sending User Status
                n = b'' # Variable that stores the User Dict after being sent by serfver through json
                n += client_socket.recv(BUFSIZ)
                n_dict = json.loads(n.decode('utf-8')) # Converting the json user dict to a real dict
                client_names.delete(0,tkinter.END)
                for key in n_dict:
                    client_names.insert(tkinter.END, '{}: {}'.format(key, n_dict[key])) # Updating the User Status 
                flag = 0
                
                if all(x=='Connected' for x in n_dict.values()): # Checking if all the Users are Connected.
                    flag = 3
                    initiate(n_dict, name) # Initiating the Messaging Process between Clients
            
            else:
                msg_vec_clock = client_socket.recv((19)) # Receiving Vector Clock from the Server.
                if msg_vec_clock.decode('utf8') == 'Available\n\n\n\n\n\n\n\n\n\n': # Checking if a client disconnected in between process
                    flag = 1
                    print('After Availalble')
                    notdisconnected = False
                    continue
                rec_vec_clock = json.loads(msg_vec_clock.decode('utf-8')) #Loading the Received Vector Clock
                sender, sub_vec_clock = rec_vec_clock[0], rec_vec_clock[1]
                vector_clock[indices[name]] += 1 # Updating the Vector Clock after receivng
                vector_clock[0] = sub_vec_clock[0] if vector_clock[0] < sub_vec_clock[0] else vector_clock[0] # Updating the Vector Clock after receivng
                vector_clock[1] = sub_vec_clock[1] if vector_clock[1] < sub_vec_clock[1] else vector_clock[1] # Updating the Vector Clock after receivng
                vector_clock[2] = sub_vec_clock[2] if vector_clock[2] < sub_vec_clock[2] else vector_clock[2] # Updating the Vector Clock after receivng
                msg_list.insert(tkinter.END, '\n {} ==> {}'.format(sender, vector_clock)) # Displaying the Updated Vector Clock on Client GUI
                if all(x=='Connected' for x in n_dict.values()): # Checking if all the Users are Connected.
                    flag = 3
                    initiate(n_dict, name)
                    
        except OSError:  # Possibly client has left the chat.
            break

def initiate(n_dict, name): # Function that Initiates the Vector Clock Messaging Service.
    import random
    from time import sleep
    global vector_clock, indices
    sleep(random.randint(2,10)) # Sleep for a random amount of Seconds betn 2 - 10
    receiver = random.choice(list(n_dict.keys()-name)) # Select a random Receiver
    vector_clock[indices[name]] += 1 # Update the Vector Clock
    msg_list.insert(tkinter.END, '\n{} ==> {}'.format(vector_clock, receiver)) # Displaying the Updated Vector Clock on Client GUI
    vec_list = [receiver, vector_clock] # List that hold the Vector Clock and Receiver name
    vec_msg = json.dumps(vec_list).encode('utf-8') # Creating a Json Dump of the above list
    client_socket.send(vec_msg) # Sending the JSON Dump to the server.
    sleep(1)
    

def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_clnt_GUI.py """
    msg = my_msg.get() # Getting Message From the ENtry Field
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8")) # Sending Message to the Client
    if msg == "{quit}": # User Input to Quit the Client Server Manually
        client_socket.close()
        top.destroy()


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_clnt_GUI.py """
    client_socket.send(bytes("{quit}", "utf8"))
    client_socket.close()
    top.destroy()
    
    
def quit(top): # Manual Quit Button, Other than X
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_clnt_GUI.py """
    client_socket.send(bytes("{quit}", "utf8"))
    client_socket.close()
    top.destroy()

""" Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_clnt_GUI.py """
""" Code Referenced From: https://www.tutorialspoint.com/python/python_gui_programming.htm """

# Code for GUI using TKinter Library
top = tkinter.Tk()
top.title("Chatter")

client_label = tkinter.Label(top, text = '\t\tMessages: \t \t \t \t \t \t \tUser Status:')
client_label.pack()

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("Type your messages here.")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Text(messages_frame, height=15, width=60, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT)
msg_list.pack()
messages_frame.pack()

client_names = tkinter.Listbox(messages_frame, height=15, width=30)
client_names.pack()
entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

b2 = tkinter.Button(top, text = 'Quit', command =lambda : quit(top))
b2.pack()
#
top.protocol("WM_DELETE_WINDOW", on_closing)

#----Now comes the sockets part----

if __name__ == '__main__':
    BUFSIZ = 1024
    ADDR = ('127.0.0.1', 33000)
    
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(ADDR)
    
    receive_thread = Thread(target=receive)
    receive_thread.start()
    tkinter.mainloop()  # Starts GUI execution.
