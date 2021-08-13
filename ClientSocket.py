# from _typeshed import Self
import socket
import tkinter as tk 
from tkinter import ttk 
from tkinter import messagebox
from datetime import datetime
import json

HOST_IP = "127.0.0.1"
PORT = 6000
FORMAT = "utf8"

FONT = ("Arial", 15,"bold")

SIGNUP = "signup"
LOGIN = "login"
LOGOUT = "logout"
SEARCH = "search"
GETIP ="getip"
CONNECT="connect"
ADMIN_USERNAME = 'admin'
ADMIN_PSWD = '123'

class Covid19App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("500x300")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(width = False, height = False)
        container = tk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        self.frames = {}
        for F in (StartPage, HomePage):
            frame = F(container, self)
            self.frames[F] = frame 
            frame.grid(row = 0, column = 0, sticky = "nsew")
        self.showFrame(StartPage)
    
    def showFrame(self, container):
        frame = self.frames[container]
        if container == HomePage:
            self.geometry("1200x600")
        # elif container == IPGET:
        #     self.geometry("500x300")
        else:
            self.geometry("500x300")
        frame.tkraise()

    def on_closing(self):
        
        if messagebox.askokcancel("Quit", "Do you wanna quit?"):
            self.destroy()
            try:
                option = LOGOUT
                client.sendall(option.encode(FORMAT))
            except:
                pass

    def logIn(self,curFrame,sck):
        try:
            user = curFrame.entry_user.get()
            pswd = curFrame.entry_pswd.get()
            if user == "" or pswd == "":
                curFrame.label_notice["text"] = "Fields cannot be empty"
                return 
            option = LOGIN
            sck.sendall(option.encode(FORMAT))
            sck.sendall(user.encode(FORMAT))
            print("Input:", user)
            sck.recv(1024)
            print("s responded")
            sck.sendall(pswd.encode(FORMAT))
            print("Input:", pswd)
            accepted = sck.recv(1024).decode(FORMAT)
            print("Accepted: "+ accepted)
            if accepted == "1":
                self.showFrame(HomePage)
                curFrame.label_notice["text"] = ""
            elif accepted == "2":
                curFrame.label_notice["text"] = "Invalid username or password"
            elif  accepted == "0":
                curFrame.label_notice["text"] = "User already logged in"

        except:
            curFrame.label_notice["text"] = "Error: Server is not responding"
            print("Error: Server is not responding")

    def signUp(self,curFrame, sck):
        try:
            user = curFrame.entry_user.get()
            pswd = curFrame.entry_pswd.get()
            if pswd == "":
                curFrame.label_notice["text"] = "Password cannot be empty"
                return 
            option = SIGNUP
            sck.sendall(option.encode(FORMAT))
            sck.sendall(user.encode(FORMAT))
            print("Input:", user)
            sck.recv(1024)
            print("Socket responded")
            sck.sendall(pswd.encode(FORMAT))
            print("Input:", pswd)
            accepted = sck.recv(1024).decode(FORMAT)
            print("Accepted: " + accepted)
            if accepted == "True":
                self.showFrame(HomePage)
                curFrame.label_notice["text"] = ""
            else:
                curFrame.label_notice["text"] = "Username already exists"

        except:
            curFrame.label_notice["text"] = "Error 404: Server is not responding"
            print("404")

    def logout(self,curFrame, sck):
        try:
            option = LOGOUT
            sck.sendall(option.encode(FORMAT))
            accepted = sck.recv(1024).decode(FORMAT)
            if accepted == "True":
                self.showFrame(StartPage)
        except:
            curFrame.label_notice["text"] = "Error: Server is not responding"

    def searchProvince(self, curFrame, sck):
        try:
            print(curFrame.label_notice["text"])
            curFrame.label_notice["text"] = ""
            province = curFrame.entry_search_province.get()    
            datee = curFrame.entry_search_day.get()
           
            formt = '%d-%m-%Y'
            try:
                check = bool(datetime.strptime(datee, formt))
            except ValueError:
                check = False
            if  check == False: 
                curFrame.label_notice["text"] = "Date is not valid (format must be dd-mm-yyyy)"
                return
            if province == "" or datee =="":
                curFrame.label_notice["text"] = "Fields cannot be empty"
                return

            option = SEARCH
            sck.sendall(option.encode(FORMAT))

            sck.sendall(province.encode(FORMAT))
            print("input:", province)
            sck.recv(1024)
            print("socket responded")
            sck.sendall(datee.encode(FORMAT))
            print("input:", datee)
            response = sck.recv(1024).decode(FORMAT)
            covidProvinceResult = json.loads(response)

            if (covidProvinceResult["status"] == "province 404"):
                print("no Province")
                curFrame.label_notice["text"] = "This province doesn't exist"
                return
              
            x = curFrame.tree_detail.get_children()
            for item in x:
                curFrame.tree_detail.delete(item)
            curFrame.tree_detail.insert('', 'end', text="1", values=(covidProvinceResult["body"]["Province"], covidProvinceResult["body"]["Infected"],
             covidProvinceResult["body"]["Treating"],covidProvinceResult["body"]["Other"], covidProvinceResult["body"]["Treated"],covidProvinceResult["body"]["Death"]))
            
            
            curFrame.frame_detail.pack()
        except:
            curFrame.label_notice["text"] = "Error:Server is not responding"

# def connectToServer(self,curFrame,sck):
#     IP =curFrame.entry_IP.get()
#     server_address = (IP, PORT)
#     sck.connect(server_address)
#     try:
#         option = CONNECT
#         sck.sendall(option.encode(FORMAT))
#         accepted = "not"
#         accepted = sck.recv(1024).decode(FORMAT)
#         print("Accepted ")
#         if accepted == "ok":
#             self.showFrame(StartPage)
#             curFrame.label_notice["text"] = ""
#     except:
#         curFrame.label_notice["text"] = "Error: Server is not responding"
#         print("Error: Server is not responding")
# class IPGET(tk.Frame):
#     def __init__(self, parent, controller):
#         tk.Frame.__init__(self, parent)
#         self.configure(bg = "SkyBlue1")
#         label_title = tk.Label(self, text ="CHOOSE IP\n", font = FONT,fg='Black',bg="SkyBlue1")
#         label_title.pack()
#         client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         button_connect = tk.Button(self, text ="CONNECT TO SERVER",bg = "#20639b",fg ='floral white', command =lambda: controller.connectToServer(self,client))      
#         button_connect.configure(width=25)
#         self.entry_IP = tk.Entry(self,width = 35,bg = 'light yellow')
#         label_IP = tk.Label(self, text="ip ",fg = '#20639b', bg = "SkyBlue1", font = 'Arial 10 ')
#         self.label_notice = tk.Label(self,text = "", bg = "bisque2", fg ='red')
#         label_IP.pack()
#         self.entry_IP.pack()
#         self.label_notice.pack()
#         button_connect.pack()
#         global HOST_IP
#         HOST_IP = self.entry_IP.get()
    
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg = "SkyBlue1")
        label_title = tk.Label(self, text ="COVID19 INFORMATION\n", font = FONT,fg='Black',bg="SkyBlue1")
       
        label_title.pack()
        
    
        button_back = tk.Button(self, text ="BACK",bg = "#20639b",fg ='floral white', command = lambda: controller.logout(self,client))
       
        button_back.configure(width=15)
        
        self.entry_search_province = tk.Entry(self,width = 35,bg = 'light yellow')
       
        self.entry_search_day = tk.Entry(self,width = 35,bg = 'light yellow')
      
        label_province = tk.Label(self, text="province ",fg = '#20639b', bg = "SkyBlue1", font = 'Arial 10 ')
        label_day = tk.Label(self, text="date ",fg = '#20639b', bg = "SkyBlue1", font = 'Arial 10 ')
        button_search = tk.Button(self, text="SEARCH",bg="#20639b",fg='floral white', command=lambda: controller.searchProvince(self,client))
        button_search.configure(width = 20)
        
        self.label_notice = tk.Label(self,text = "", bg = "bisque2", fg ='red')
        label_province.pack()
        self.entry_search_province.pack()
        label_day.pack()
        self.entry_search_day.pack()
        button_search.pack()
        self.label_notice.pack()
        
        button_back.pack()
        
        self.frame_detail = tk.Frame(self, bg="steelblue1")
        
        self.label_name_province = tk.Label(self.frame_detail,bg="floral white", text="", font=FONT)

        self.tree_detail = ttk.Treeview(self.frame_detail)
        self.tree_detail["column"] = ("Province", "Infected", "Treating", "Other","Treated","Death")
        
        self.tree_detail.column("#0", width=0, stretch=tk.NO)
        self.tree_detail.column("Province", anchor='c')
        self.tree_detail.column("Infected", anchor='c')
        self.tree_detail.column("Treating", anchor='c')
        self.tree_detail.column("Other", anchor='c')
        self.tree_detail.column("Treated", anchor='c')
        self.tree_detail.column("Death", anchor='c')

        self.tree_detail.heading("0", text="", anchor='c')
        self.tree_detail.heading("Province", text="Province", anchor='c')
        self.tree_detail.heading("Infected", text="Infected", anchor='c')
        self.tree_detail.heading("Treating", text="Treating", anchor='c')
        self.tree_detail.heading("Other", text="Other", anchor='c')
        self.tree_detail.heading("Treated", text="Treated", anchor='c')
        self.tree_detail.heading("Death", text="Death", anchor='c')

        self.label_name_province.pack(pady=5)
       
        self.tree_detail.pack()
        

       
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="SkyBlue1")
        label_title = tk.Label(self, text = "USER LOGIN",font = FONT, fg = 'Black', bg = "SkyBlue1")
        label_user = tk.Label(self, text="username ",fg = '#20639b', bg = "SkyBlue1", font = 'Arial 10 ')
        label_pswd = tk.Label(self, text="password ",fg = '#20639b', bg = "SkyBlue1", font = 'Arial 10 ')

        self.label_notice = tk.Label(self,text = "", bg = "bisque2", fg ='red')
        self.entry_user = tk.Entry(self,width = 20, bg = 'light yellow')
        self.entry_pswd = tk.Entry(self,width = 20, bg = 'light yellow')
        
        button_log = tk.Button(self,text = "LOG IN", bg = "#20639b", fg = 'floral white', command = lambda: controller.logIn(self, client)) 
        button_log.configure(width = 10)
        button_sign = tk.Button(self,text = "SIGN UP", bg = "#20639b", fg = 'floral white', command = lambda: controller.signUp(self, client)) 
        button_sign.configure(width = 10)
        label_title.pack()
        label_user.pack()
        self.entry_user.pack()
        label_pswd.pack()
        self.entry_pswd.pack()
        self.label_notice.pack()
        button_log.pack()
        button_sign.pack()

   
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (HOST_IP, PORT)
client.connect(server_address)
app = Covid19App()

try:
    app.mainloop()
    
except:
    print("Error: Server is not responding")
    client.close()

finally:
    client.close()


