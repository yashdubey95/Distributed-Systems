# Name: Yash Shreesh Dubey
# UTA ID: 1001670330

# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 17:05:30 2020

@author: yashd
"""


#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import json


def receive():
    """Handles receiving of messages."""
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_clnt_GUI.py """
    flag = 0 # To check if the server is sending the User Status or Just a Message
    while True:
        try:
#            print('After try flag = {}'.format(flag))
            if flag == 0:
                msg = client_socket.recv(BUFSIZ).decode("utf8")
#                print(type(msg), msg)
                if msg == 'Available':
                    flag += 1
                    msg = ''
                elif msg == 'Duplicate':
                    msg_list.insert(tkinter.END, 'Trying Again')
            
                else:
                    msg_list.insert(tkinter.END, msg) # Displaying Message on Client GUI
            else:
                n = b'' # Variable that stores the User Dict after being sent by serfver through json
                n += client_socket.recv(BUFSIZ)
#                print(n)
                n_dict = json.loads(n.decode('utf-8')) # Converting the json user dict to a real dict
#                print('Converting Dict',type(n_dict), n_dict)
                client_names.delete(0,tkinter.END)
                for key in n_dict:
                    client_names.insert(tkinter.END, '{}: {}'.format(key, n_dict[key])) # Updating the User Status 
#                print(' Before dict flag = {}'.format(flag))
                flag = 0
#                print('After dict flag = {}'.format(flag))
            
            
        except OSError:  # Possibly client has left the chat.
            break

    

def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_clnt_GUI.py """
    msg = my_msg.get() # Getting Message From the ENtry Field
#    print(msg)
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8")) # Sending Message to the Client
#    print('msg after send',msg)
    if msg == "{quit}": # User Input to Quit the Client Server Manually
        client_socket.close()
        top.destroy()


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    """ Code Referenced From: https://github.com/schedutron/CPAP/blob/master/Chap5/chat_clnt_GUI.py """
#    my_msg.set("{quit}")
#    send()
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
