import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import threading
import time
from datetime import date
import calendar
import requests
import json
import qrcode
import geocoder
import urllib.parse

transactionId = '61ba5406-fad6-4ae5-ac2b-477b55b6b2f6'

def getAccounts(access):
    url = "http://ncrdev-dev.apigee.net/digitalbanking/db-accounts/v1/accounts"
    payload={}
    headers = {
    'Authorization': 'Bearer ' + access,
    'transactionId': transactionId,
    'Accept': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()

def getAuthenticate(username, password):
    url = "http://ncrdev-dev.apigee.net/digitalbanking/oauth2/v1/token"
    payload='grant_type=password&username='+username+'&password=' + password
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'transactionId': transactionId,
    'institutionId': '00516',
    'Accept': 'application/json',
    'Authorization': 'Basic YUpaR3l1TmhIMDc4MWhYZ3pGWFl6WGp1ZlRKUEZrVjI6R3U0Y3NUV0N5UzBZVVFWTw=='
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    #print(response.text)
    #runFirst = json.dumps(response.text)
    #runFirst = json.loads(runFirst)
    emptyDict = response.json() 
    return emptyDict['access_token']

def genQR(master):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L ,
        box_size=20,
        border=4,
    )
    dictionary = {"u": master.username,"p":master.password,"amt":master.ChangeAmount}
    json_object = json.dumps(dictionary, indent = 4)   
    qr.add_data(json_object)
    qr.make(fit=True)
    master.qr_img = qr.make_image(fill_color="black", back_color="white")
    master.qr_img.save("QR.png")

def mapRequest(master):
    g = geocoder.ip('me')
    centerSearch = str(g.latlng[0]) + "," + str(g.latlng[1])
    center = "\"" + str(g.latlng[0]) + "," + str(g.latlng[1]) + "\""
    zoom = 12
    size = "400x400"
    key = "AIzaSyC1YvHmJqbzSCpLIJ9dJz-CP5SKnxxeqm4"
    findATM = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=ATM&inputtype=textquery&fields=formatted_address&locationbias=circle:8000@" + centerSearch + "&key=" + key
    response = requests.get(findATM)
    address = response.json()['candidates'][0]['formatted_address']
    markers = "color:blue%7Clabel:A%7C " + response.json()['candidates'][0]['formatted_address']
    markerHere = "color:red%7Clabel:%7C " + center
    response = requests.get("https://maps.googleapis.com/maps/api/staticmap?center=" + center + "&zoom=" + str(zoom) + "&size=" + size + "&markers=" + markers + "&markers=" + markerHere + "&key=" + key)
    if response.status_code == 200:
        with open("./map.jpg", 'wb') as f:
            f.write(response.content)
            return address

class ATM(Tk):
    def __init__(self):
        Tk.__init__(self)
        #self.resizable(False,False)
        self.initImage()
        self.frame = None #Frame shown in window
        self.geometry("450x800")
        self.title("NCR ATMPal")
        self.switch_frame(frameWelcome)
        self.username = ""
        self.password = ""
        self.amount = 0
        self.qr_img = None
        self.check_balance = 0
        self.invest_balance = 0
        self.loan_balance = 0
        self.access_token = 0
        self.account = {}
    #Switches frame on window
    def switch_frame(self, frameClass):
        newFrame = frameClass(self)
        if self.frame is not None:
            self.frame.pack_forget()
            x = threading.Thread(target=self.frame.destroy, args=())
        self.frame = newFrame
        self.frame.pack(fill=BOTH, expand=True)
    def initImage(self):
        login = Image.open("resources/login.png")
        login = login.resize((250, 60), Image.ANTIALIAS) ## The (250, 250) is (height, width
        im_login = ImageTk.PhotoImage(login)
        self.login_img = im_login
        submit = Image.open("resources/submit.png")
        submit = submit.resize((250, 60), Image.ANTIALIAS) ## The (250, 250) is (height, width
        im_submit = ImageTk.PhotoImage(submit)
        self.submit_img = im_submit
        submit_small = submit.resize((200,45), Image.ANTIALIAS)
        im_submit_small = ImageTk.PhotoImage(submit_small)
        self.submit_small_img = im_submit_small
        select = Image.open("resources/selectatm.png")
        select = select.resize((250, 60), Image.ANTIALIAS)
        im_select = ImageTk.PhotoImage(select)
        self.select_img = im_select
        find = Image.open("resources/findatm.png")
        find = find.resize((250, 60), Image.ANTIALIAS)
        im_find = ImageTk.PhotoImage(find)
        self.find_img = im_find
        deposit = Image.open("resources/deposit.png")
        deposit = deposit.resize((200,50), Image.ANTIALIAS)
        im_deposit = ImageTk.PhotoImage(deposit)
        self.deposit_img = im_deposit
        withdraw = Image.open("resources/withdraw.png")
        withdraw = withdraw.resize((200,50), Image.ANTIALIAS)
        im_withdraw = ImageTk.PhotoImage(withdraw)
        self.withdraw_img = im_withdraw
        ncr = Image.open("resources/ncr.png")
        ncr = ncr.resize((200, 50), Image.ANTIALIAS)
        im_ncr = ImageTk.PhotoImage(ncr)
        self.ncr_img = im_ncr
        cancel = Image.open("resources/cancel.png")
        cancel = cancel.resize((200,50), Image.ANTIALIAS)
        im_cancel = ImageTk.PhotoImage(cancel)
        self.cancel_img = im_cancel
        finish = Image.open("resources/finish.png")
        finish = finish.resize((200,50), Image.ANTIALIAS)
        im_finish = ImageTk.PhotoImage(finish)
        self.finish_img = im_finish


class frameWelcome(Frame):
    def __init__(self, master):
        Frame.__init__(self,master,bg="white")
        Label(self,image=master.ncr_img, width=300, bg="#51B948",font=('arial', '35', 'bold')).pack(fill="x",ipady=10)
        Message(self, text="Access your money securely and safely.",width = 250, font=('arial', '30', 'bold'),fg="black",bg="white").pack(pady=100)
        Button(self, image=master.login_img,command=lambda:master.switch_frame(frameLogin),font=('arial', '12'),borderwidth=0,activebackground="white",bg='white').pack(pady=100)

# Frame home
class frameHome(Frame):
    def __init__(self, master):
        Frame.__init__(self,master,bg="white")
        Label(self,image=master.ncr_img, width=300, bg="#51B948",font=('arial', '35', 'bold')).pack(fill="x",ipady=10)
        hello2 = Label(self, text=master.username,font=('arial', '24', 'bold'),bg="white")
        hello2.config(anchor=CENTER)
        hello2.pack()
        Label(self,text="ACCOUNT INFORMATION",font=('arial', '22'),fg="#616161",bg="white").pack(anchor="w",pady=25,padx=(10,0))
        Label(self,text="CHECKING 1234",font=('arial', '18'),bg="white").pack(anchor="w",padx=25)
        Label(self,text="Balance: -------------------------          %1.2f" %(master.check_balance),font=('arial', '16'),bg="white").pack(anchor="w",padx=25)
        Label(self,text="INVESTING 1234",font=('arial', '18'),bg="white").pack(anchor="w",pady=(50,0),padx=25)
        Label(self,text="Balance: -------------------------          %1.2f" %(master.invest_balance),font=('arial', '16'),bg="white").pack(anchor="w",padx=25)
        Label(self,text="LOANS 1234",font=('arial', '18'),bg="white").pack(anchor="w",pady=(50,0),padx=25)
        Label(self,text="Balance: -------------------------          %1.2f" %(master.loan_balance),font=('arial', '16'),bg="white").pack(anchor="w",padx=25)
        Button(self, image=master.select_img,command=lambda:master.switch_frame(frameMap),font=('arial', '12'),borderwidth=0,activebackground="white",bg='white').pack(pady=(210,0))


# Frame for selecting action to perform at the ATM
class frameMap(Frame):
    def __init__(self,master):
        self.address = ""
        Frame.__init__(self,master,bg="white")
        Label(self,image=master.ncr_img, width=300, bg="#51B948",font=('arial', '35', 'bold')).pack(fill="x",ipady=10)
        Button(self, text="Back", command=lambda:master.switch_frame(frameHome),font=('arial', '12'),borderwidth=0,activebackground="white",bg='white').pack(anchor="w")
        prompt = Message(self, text="Nearest ATM Machine:", font=('arial', '24'),width=400,bg="white").pack(pady=50)
        self.initMap(master)
        Label(self,image=master.map).pack()
        Label(self,text=self.address,bg="white",font=('arial', '12')).pack()
        Button(self, image=master.select_img,command=lambda:master.switch_frame(frameATMAction),font=('arial', '12'),borderwidth=0,activebackground="white",bg='white').pack(pady=(25,0))
    def initMap(self,master):
        self.address = mapRequest(master)
        login = Image.open("map.jpg")
        login = login.resize((400,400), Image.ANTIALIAS) ## The (250, 250) is (height, width
        im_login = ImageTk.PhotoImage(login)
        master.map = im_login

class frameATMAction(Frame):
    def __init__(self, master):
        Frame.__init__(self,master,bg="white")
        Label(self,image=master.ncr_img, width=300, bg="#51B948",font=('arial', '35', 'bold')).pack(fill="x",ipady=10)
        Button(self, text="Back", command=lambda:master.switch_frame(frameMap),font=('arial', '12'),borderwidth=0,activebackground="white",bg='white').pack(anchor="w")
        Message(self, text="Select your ATM action below.",width=250, font=('arial', '24'),bg="white").pack(pady=50)
        Button(self, image=master.deposit_img,command=lambda:master.switch_frame(frameDepositAction),font=('arial', '12'),borderwidth=0,activebackground="white",bg='white').pack(pady=10)
        Button(self, image=master.withdraw_img,command=lambda:master.switch_frame(frameWithdrawAction),font=('arial', '12'),borderwidth=0,activebackground="white",bg='white').pack(pady=10)

class frameDepositAction(Frame):
    def __init__(self, master):
        Frame.__init__(self,master,bg="white")
        Label(self,image=master.ncr_img, width=300, bg="#51B948",font=('arial', '35', 'bold')).pack(fill="x",ipady=10)
        Button(self, text="Back", command=lambda:master.switch_frame(frameATMAction),font=('arial', '12'),borderwidth=0,activebackground="white",bg='white').pack(anchor="w")
        Message(self, text="Enter the amount you would like to deposit.",width = 350, font=('arial', '24'),bg="white").pack(pady=(50,0))
        deposit_amount = Entry(self,width=30)
        deposit_amount.pack(pady=25)
        Button(self, image=master.submit_small_img, command=lambda:self.setAmount(master,deposit_amount),borderwidth=0,activebackground="white",bg='white').pack(pady=25)
    def setAmount(self,master,entry):
        master.ChangeAmount = entry.get()
        master.switch_frame(frameQR)

class frameQR(Frame):
    def __init__(self,master):
        Frame.__init__(self,master,bg="white")
        Label(self,image=master.ncr_img, width=300, bg="#51B948",font=('arial', '35', 'bold')).pack(fill="x",ipady=10)
        self.initQR(master)
        Message(self, text="Please scan this QR code at the ATM you have selected.",width=300,font=('arial', '24'),bg="white").pack(pady=(50,10))
        Label(self,image=master.qr_img).pack()
        Button(self, image=master.finish_img, command=lambda:self.finish(master),font=('arial', '12'),borderwidth=0,activebackground="white",bg='white').pack(pady=(10,0))
        Button(self, image=master.cancel_img, command=lambda:master.switch_frame(frameATMAction),font=('arial', '12'),borderwidth=0,activebackground="white",bg='white').pack(pady=(10,0))
    def initQR(self,master):
        genQR(master)
        master.qr_img = Image.open("QR.png")
        master.qr_img = master.qr_img.resize((400,400),Image.ANTIALIAS)
        master.qr_img = ImageTk.PhotoImage(master.qr_img)
        #master.check_balance = int(master.amount) + int(master.check_balance)
    def finish(self,master):
        master.check_balance = int(master.ChangeAmount) + int(master.check_balance)
        master.switch_frame(frameHome)
    def cancel(self,master):
        master.switch_frame(frameHome)

class frameWithdrawAction(Frame):
    def __init__(self, master):
        Frame.__init__(self,master,bg="white")
        Label(self,image=master.ncr_img, width=300, bg="#51B948",font=('arial', '35', 'bold')).pack(fill="x",ipady=10)
        Button(self, text="Back", command=lambda:master.switch_frame(frameATMAction),font=('arial', '12'),borderwidth=0,activebackground="white",bg='white').pack(anchor="w")
        Message(self, text="Enter the amount you would like to withdraw.",width = 350, font=('arial', '24'),bg="white").pack(pady=(50,0))
        withdraw_amount = Entry(self,width=30)
        withdraw_amount.pack(pady=25)
        Button(self, image=master.submit_small_img, command=lambda:self.setAmount(master,withdraw_amount),borderwidth=0,activebackground="white",bg='white').pack(pady=25)
    def setAmount(self,master,entry):
        master.ChangeAmount = str(int(entry.get())*-1)
        master.switch_frame(frameQR)


class frameLogin(Frame):
    def __init__(self,master):
        Frame.__init__(self,master,bg="white")
        Label(self,image=master.ncr_img, width=300, bg="#51B948",font=('arial', '35', 'bold')).pack(fill="x",ipady=10)
        Message(self, text="Welcome",width = 350,  font=('arial', '30', 'bold'),bg="white").pack(pady=50)
        Label(self,text="Username",pady=10, font=('arial', '18'),bg="white").pack(pady=2)
        userInput = Entry(self,width=50)
        userInput.pack()
        Label(self,text="Password",pady=10, font=('arial', '18'),bg="white").pack(pady=2)
        passInput = Entry(self,width=50,show='*')
        passInput.pack()
        Button(self, image=master.submit_img,command=lambda:self.saveAndSwitch(master,userInput,passInput),font=('arial', '12'),borderwidth=0,activebackground="white",bg='white').pack(pady=50)
        Button(self,text="Back", borderwidth=0, activebackground="white",command=lambda:master.switch_frame(frameWelcome),bg="white",font=('arial', '12')).pack()
        self.invalid_login = Label(self,text="Invalid Login Information", font=('arial', '12', 'bold'))

    def saveAndSwitch(self,master,user,password):
        master.username = user.get()
        master.password = password.get()
        master.access_token = getAuthenticate(user.get(),password.get())
        master.account = getAccounts(master.access_token)
        master.check_balance = master.account['accounts'][0]['availableBalance']['amount']
        master.invest_balance = master.account['accounts'][1]['availableBalance']['amount']
        master.loan_balance = master.account['accounts'][2]['availableBalance']['amount']
        master.switch_frame(frameHome)

 #:) starting the app
if __name__ == "__main__":
    app = ATM()
    app.mainloop(0)