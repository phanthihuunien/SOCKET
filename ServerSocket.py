import socket
import threading
import pyodbc
import sys

from tkinter import *
import tkinter as tk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import ttk

PORT = 65432
HOSTNAME="DESKTOP-OMT3G09"
HOST = "127.0.0.1"
HEADER = 64
FORMAT = "utf8"
DISCONNECT = "x"

#define sever name and database name
SEVER_NAME = HOSTNAME +'\SQLEXPRESS'
DATABASE_NAME='SOCKET'
FORMAT = "utf8"

#option
SIGNUP = "signup"
LOGIN = "login"
LOGOUT = "logout"
SEARCH = "search"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
LARGE_FONT = ("Arial", 15,"bold")

def ConnectToDataBase():
    cnxn = pyodbc.connect(driver='{SQL Server}', host='DESKTOP-OMT3GO9\SQLEXPRESS', database='SOCKET',trusted_connection='yes')
    cursor = cnxn.cursor()
    return cursor
#https://docs.microsoft.com/vi-vn/sql/connect/python/pyodbc/step-3-proof-of-concept-connecting-to-sql-using-pyodbc?view=sql-server-2016
def InsertNewAccount(user,password):
    cursor = ConnectToDataBase()
    cursor.execute( "insert into TaiKhoan(TenDangNhap,MatKhau) values(?,?);",(user, password))
    cursor.commit()

Active_Account = []
ID = []
Ad = []

def checkClientSignUp(username):
    if username == "admin":
        return False
    cursor=ConnectToDataBase()
    cursor.execute("select TenDangNhap from TaiKhoan")
    for row in cursor:
        parse = str(row) 
        parseCheck = parse[2:]
        parse = parseCheck.find("'")
        parseCheck = parseCheck[:parse]
        if parseCheck == username:
            return False
    return True

def clientSignUp(sck, addr):

    user = sck.recv(1024).decode(FORMAT)
    print("username:--" + user + "--")

    sck.sendall(user.encode(FORMAT))

    password = sck.recv(1024).decode(FORMAT)
    print("password:--" + password + "--")

    accepted = checkClientSignUp(user)
    print("accept:", accepted)
    sck.sendall(str(accepted).encode(FORMAT))

    if accepted:
        InsertNewAccount(user, password)
        Ad.append(str(addr))
        ID.append(user)
        account = str(Ad[Ad.__len__() - 1]) + "-" + str(ID[ID.__len__() - 1])
        Active_Account.append(account)

    print("end-logIn()")
    print("")

def Check_Active_Account(username):
    for row in Active_Account:
        parse = row.find("-")
        parseCheck = row[(parse+1):]
        if parseCheck == username:
            return False
    return True

def Remove_Active_Account(connect, addr):
    for row in Active_Account:
        parse = row.find("-")
        parse_check = row[:parse]
        if parse_check == str(addr):
            parse= row.find("-")
            Ad.remove(parse_check)
            username = row[(parse + 1):]
            ID.remove(username)
            Active_Account.remove(row)
            connect.sendall("True".encode(FORMAT))

def check_clientLogIn(username, password):
    cursor = ConnectToDataBase()
    cursor.execute("select T.TenDangNhap from TaiKhoan T")
    if Check_Active_Account(username) == False:
        return 0
    # check if admin logged in
    if username == "admin" and password == "123":
        return 1
    
    for row in cursor:
        parse = str(row)
        parseCheck = parse[2:]
        parse = parseCheck.find("'")
        parseCheck = parseCheck[:parse]
        if parseCheck == username:
            cursor.execute("select T.MatKhau from TaiKhoan T where T.TenDangNhap=(?)",(username))
            parse = str(cursor.fetchone())
            parseCheck = parse[2:]
            parse = parseCheck.find("'")
            parseCheck = parseCheck[:parse]
            if password == parseCheck:
                return 1
    return 2

def clientLogIn(sck):
    user = sck.recv(1024).decode(FORMAT)
    print("username:--" + user +"--")

    sck.sendall(user.encode(FORMAT))
    password = sck.recv(1024).decode(FORMAT)
    print("password:--" + password + "--")
    
    accepted = check_clientLogIn(user, password)
    if accepted == 1:
        ID.append(user)
        account = str(Ad[Ad.__len__() - 1]) + "-" + str(ID[ID.__len__() - 1])
        Active_Account.append(account)
    
    print("accept:", accepted)
    sck.sendall(str(accepted).encode(FORMAT))
    print("end-logIn()")
    print("")

def handle_client(connect, addr):
    while True:
        option = connect.recv(1024).decode(FORMAT)
        if option == LOGIN:
            Ad.append(str(addr))
            clientLogIn(connect)
        elif option == SIGNUP:
            clientSignUp(connect, addr)
        elif option == LOGOUT:
            Remove_Active_Account(connect, addr)

    Remove_Active_Account(connect, addr)
    connect.close()
    print("end-thread")


def runServer():
    try:
        print(HOST)
        print("Waiting for Client")

        while True:
            print("enter while loop")
            connect, addr = s.accept()
            clientThread = threading.Thread(target = handle_client, args=(connect, addr))
            clientThread.daemon = True 
            clientThread.start()
            print("end main-loop")
    except KeyboardInterrupt:
        print("error")
        s.close()
    finally:
        s.close()
        print("end")
# defind GUI-app class
class CovidAdmin(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("COVID19 SERVER")
        self.geometry("400x200")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(width = False, height = False)

        container = tk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}
        for F in (StartPage,HomePage):
            frame = F(container, self)

            self.frames[F] = frame 

            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.showFrame(StartPage)


    def showFrame(self, container):
        
        frame = self.frames[container]
        if container == HomePage:
            self.geometry("500x300")
        else:
            self.geometry("500x300")
        frame.tkraise()

    # close-programe function
    def on_closing(self):
        if messagebox.askokcancel("Quit!", "Do you wanna quit?"):
            self.destroy()

    def logIn(self,curFrame):

        user = curFrame.entry_user.get()
        pswd = curFrame.entry_pswd.get()

        if pswd == "":
            curFrame.label_notice["text"] = "Password can't be empty"
            return 

        if user == "admin" and pswd == "123":
            self.showFrame(HomePage)
            curFrame.label_notice["text"] = ""
        else:
            curFrame.label_notice["text"] = "Invalid username or password"


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg = "SkyBlue1")
        
        label_title = tk.Label(self, text="\nLOG IN FOR SERVER\n", font = LARGE_FONT, fg ='Black',bg = "SkyBlue1").grid(row = 0,column = 1)
        label_user = tk.Label(self, text="\tUSERNAME ",fg='#20639b',bg="deep sky blue",font='Arial 10 bold').grid(row = 1,column = 0)
        label_pswd = tk.Label(self, text="\tPASSWORD ",fg='#20639b',bg="deep sky blue",font='Arial 10 bold').grid(row = 2,column = 0)

        self.label_notice = tk.Label(self,text = "", bg = "linen",fg = 'red')
        self.entry_user = tk.Entry(self,width = 35,bg = 'light yellow')
        self.entry_pswd = tk.Entry(self,width = 35,bg = 'light yellow')

        button_log = tk.Button(self,text ="LOG IN",bg="#20639b",fg='floral white',command = lambda: controller.logIn(self))

        button_log.grid(row = 6,column = 1)
        button_log.configure(width = 10)
        self.label_notice.grid(row = 4,column = 1)
        self.entry_pswd.grid(row = 2,column = 1)
        self.entry_user.grid(row = 1,column = 1)

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) 
        self.configure(bg = "SkyBlue1")
        label_title = tk.Label(self, text ="\n ACTIVE ACCOUNT ON SEVER\n", font = LARGE_FONT,fg = '#20639b',bg = "SkyBlue1").pack()
        
        self.conent =tk.Frame(self)
        self.data = tk.Listbox(self.conent, height = 10, 
                  width = 40, 
                  bg ='floral white',
                  activestyle = 'dotbox', 
                  font = "Arial",
                  fg ='#20639b')
        
        button_log = tk.Button(self,text = "REFRESH",bg = "#20639b",fg ='floral white',command = self.Update_Client)
        button_back = tk.Button(self, text = "LOG OUT",bg = "#20639b",fg ='floral white' ,command = lambda: controller.showFrame(StartPage))
        button_log.pack(side = BOTTOM)
        button_log.configure(width = 10)
        button_back.pack(side = BOTTOM)
        button_back.configure(width = 10)
        
        self.conent.pack_configure()
        self.scroll= tk.Scrollbar(self.conent)
        self.scroll.pack(side = RIGHT, fill = BOTH)
        self.data.config(yscrollcommand = self.scroll.set)
        
        self.scroll.config(command = self.data.yview)
        self.data.pack()
        
    def Update_Client(self):
        self.data.delete(0, len(Active_Account))
        for i in range(len(Active_Account)):
            self.data.insert(i, Active_Account[i])
    


sThread = threading.Thread(target = runServer)
sThread.daemon = True 
sThread.start()

app = CovidAdmin()
app.mainloop()