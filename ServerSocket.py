import socket
import threading
import pyodbc
import os
from datetime import datetime
import time

from bs4 import BeautifulSoup
import requests
import json
from tkinter import *
import tkinter as tk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import ttk
import json

PORT = 6000
HOSTNAME=socket.gethostname()#"DESKTOP-OMT3G09"
HOST_IP = "127.0.0.1"#socket.gethostbyname(HOSTNAME)
FORMAT = "utf8"

SEVER_NAME = HOSTNAME +'\SQLEXPRESS'
DATABASE_NAME='SOCKET'
FORMAT = "utf8"

SIGNUP = "signup"
LOGIN = "login"
LOGOUT = "logout"
SEARCH = "search"
CONNECT="connect"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST_IP, PORT))
s.listen(1)
FONT = ("Arial", 15,"bold")

def ConnectToDataBase():
    cnxn = pyodbc.connect(driver='{SQL Server}', host=HOSTNAME+'\SQLEXPRESS', database='SOCKET',trusted_connection='yes')
    cursor = cnxn.cursor()
    return cursor
#https://docs.microsoft.com/vi-vn/sql/connect/python/pyodbc/step-3-proof-of-concept-connecting-to-sql-using-pyodbc?view=sql-server-2016
def InsertNewAccount(user,password): #insert new account into database when signing up
    cursor = ConnectToDataBase()
    cursor.execute( "insert into TaiKhoan(TenDangNhap,MatKhau) values(?,?);",(user, password))
    cursor.commit()

Active_Account = []
ID = []
Ad = []


def CheckClientSignUp(username):
    cursor = ConnectToDataBase()
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
    user = sck.recv(1024).decode(FORMAT)#receive username from client
    print("username:" + user)
    sck.sendall(user.encode(FORMAT))#send respond
    password = sck.recv(1024).decode(FORMAT)#receive password from client
    print("password:" + password)

    accepted = CheckClientSignUp(user)#validate username  

    print("accept:", accepted)
    sck.sendall(str(accepted).encode(FORMAT))#send respond to client that account be accepted or not
    if accepted:
        InsertNewAccount(user, password)#insert new acount to database
        Ad.append(str(addr))
        ID.append(user)
        account = str(Ad[Ad.__len__() - 1]) + "_" + str(ID[ID.__len__() - 1])
        Active_Account.append(account)

    print("End_LogIn()")

def Check_Active_Account(username): #kiem tra co dang hoat dong khong khi co mot client khac log in vao
    for row in Active_Account:
        parse = row.find("_")
        parseCheck = row[(parse+1):]
        if parseCheck == username:
            return False
    return True

def Remove_Active_Account(connect, addr): #remove account khoi nhung tk dang hoat dong khi log out.
    for row in Active_Account:
        parse = row.find("_")
        parse_check = row[:parse]
        if parse_check == str(addr):
            parse= row.find("_")
            Ad.remove(parse_check)
            username = row[(parse + 1):]
            ID.remove(username)
            Active_Account.remove(row)
            connect.sendall("True".encode(FORMAT))


def check_clientLogIn(username, password):#kiem tra thong tin log in voi database
    cursor = ConnectToDataBase()
    cursor.execute("select T.TenDangNhap from TaiKhoan T")
    if Check_Active_Account(username) == False:
        return 0 #khi tai khoan dang hoat dong, khong the dang nhap cung 1 tai khoan nhieu noi
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
                return 1#dang nhap ok
    return 2#sai mk hoac pass


def clientLogIn(sck):
    user = sck.recv(1024).decode(FORMAT) #nhan username tu client
    print("username:" + user)

    sck.sendall(user.encode(FORMAT))#phan hoi sau khi nhan username
    password = sck.recv(1024).decode(FORMAT)#nhan pass tu client
    print("password:" + password)
    
    accepted = check_clientLogIn(user, password)#kiem tra mk, pass ok hay k
    if accepted == 1:
        ID.append(user)
        account = str(Ad[Ad.__len__() - 1]) + "_" + str(ID[ID.__len__() - 1])
        Active_Account.append(account) #them vao list nhung tai khoan dang hoat dong
    
    print("Accept:", accepted)
    sck.sendall(str(accepted).encode(FORMAT))#gui thong tin accept hay khong qua client
    print("End-LogIn()")
    print("")


def UpdateData():
    start = time.time()
    while True:
        if ((time.time() - start) > 1800):
            Get_Json_File()
            start = time.time()


def clientSearch(sck):#request tim kiem infor từ client
    Get_Json_File()#get file từ web
    province = sck.recv(1024).decode(FORMAT)#nhan ten tinh tu client
    print("Province:" + province)
    sck.sendall(province.encode(FORMAT))#phan hoi
    date = sck.recv(1024).decode(FORMAT)#nhan ngay muon tim
    print("Date:" + date)
    provinceCheck =   GetProvinceData(date, province)
    provinceCheck = json.dumps(provinceCheck.__dict__, ensure_ascii=False)
    sck.sendall(provinceCheck.encode(FORMAT))
    print("End-Search()")

# def clientConnect(sck):
#     accepted = "ok"
#     sck.sendall(accepted.encode(FORMAT))

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
        elif option == SEARCH:
            clientSearch(connect)
        # elif option == CONNECT:
        #     clientConnect(connect)
    Remove_Active_Account(connect, addr)
    connect.close()
    print("end-thread")


def RunServer():
    try:
        print(HOST_IP)
        print("Waiting for Client")

        Update = threading.Thread(target= UpdateData)#update data trong khi dang run
        Update.daemon = True
        Update.start()

        while True:
            print("Loading...")
            connect, addr = s.accept()
            clientThread = threading.Thread(target = handle_client, args = (connect, addr))
            clientThread.daemon = True 
            clientThread.start()
            print("End Main-loop")
    except KeyboardInterrupt:
        print("Error")
        s.close()
    finally:
        s.close()
        print("End")

def Get_Json_File():
    url = 'https://vi.wikipedia.org/wiki/B%E1%BA%A3n_m%E1%BA%ABu:D%E1%BB%AF_li%E1%BB%87u_%C4%91%E1%BA%A1i_d%E1%BB%8Bch_COVID-19/S%E1%BB%91_ca_nhi%E1%BB%85m_theo_t%E1%BB%89nh_th%C3%A0nh_t%E1%BA%A1i_Vi%E1%BB%87t_Nam#cite_note-1'

    response = requests.get(url)

    soup =  BeautifulSoup(response.text, 'html.parser')

    table = soup.find('tbody')
    count = 1
    res = []
    for row in table.find_all('tr'):
        i = 1
        province, infected, treating, other, treated, death = '', '', '', '', '', ''
        for cell in row.find_all('td'):
            if i == 1:
                province = cell.text[0:(len(cell.text) - 1)]
            elif i == 2:
                infected = cell.text[0:(len(cell.text) - 1)]
            elif i == 3:
                treating = cell.text[0:(len(cell.text) - 1)]
            elif i == 4:
                other = cell.text[0:(len(cell.text) - 1)]
            elif i == 5:
                treated = cell.text[0:(len(cell.text) - 1)]
            else:
                death = cell.text[0:(len(cell.text) - 1)]
            i += 1
        if count > 2 and count <= 65:
            data = {'Province': province, 'Infected': infected, 'Treating': treating, 'Other': other, 'Treated': treated, 'Death': death}
            res.append(data)
        count += 1
    date = datetime.now().strftime("%d-%m-%Y")
    with open(date + '.json', 'w', encoding= 'utf-8') as f:
        json.dump(res, f, indent= 4, ensure_ascii= False)
    f.close()

def UpdateData():
    start = time.time()
    while True:
        if ((time.time() - start) > 1800):
            Get_Json_File()
            start = time.time()

def GetProvinceData(date, province):
    if (os.path.isfile(date + '.json')):
        data = json.load(open(date + '.json', encoding= 'utf-8'))
        for i in data:
            if i["Province"] == province:
                return Response("200", i)
        return Response("province 404", {})
    else:
        return Response("file 404", {})

class Response:
  def __init__(self, status, body):
    self.status = status
    self.body = body

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
    
    def on_closing(self):
        if messagebox.askokcancel("Quit!", "Do you wanna quit?"):
            self.destroy()
        s.close()

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
        
        label_title = tk.Label(self, text="\nSERVER LOGIN\n", font = FONT, fg ='Black',bg = "SkyBlue1").grid(row = 0,column = 1)
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
        label_title = tk.Label(self, text ="\n ACTIVE ACCOUNT\n", font = FONT,fg = '#20639b',bg = "SkyBlue1").pack()
        
        self.conent =tk.Frame(self)
        self.data = tk.Listbox(self.conent, height = 10, width = 40, bg ='floral white',activestyle = 'dotbox', font = "Arial",fg ='#20639b')
        
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
            


sThread = threading.Thread(target = RunServer)
sThread.daemon = True 
sThread.start()

app = CovidAdmin()
app.mainloop()

