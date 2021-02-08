#This will be the mock atm for making transactions with that will be run on the raspberry PI
import json
import requests
import PIL
from PIL import ImageTk, Image
import cv2
import tkinter as tk
from tkinter import *
import time
import threading

#authData = {} # holds access token
#username = "HACKATHONUSER217"
#password = "uga123"
#OUR TARGET ACCOUNT 
#targetAccount = "HACKATHONUSER218"
#password = "uga123"
transactionId = '61ba5406-fad6-4ae5-ac2b-477b55b6b2f6'


def scanQR():
    # set up camera object
    cap = cv2.VideoCapture(0)
    # QR code detection object
    detector = cv2.QRCodeDetector()
    while True:
        # get the image
        _, img = cap.read()
        # get bounding box coords and data
        data, bbox, _ = detector.detectAndDecode(img)
        # if there is a bounding box, draw one, along with the data
        if(bbox is not None):
            for i in range(len(bbox)):
                cv2.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(255,
                        0, 255), thickness=2)
            cv2.putText(img, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)
            if data:
                cap.release()
                cv2.destroyAllWindows()
                return data
        # display the image preview
        cv2.imshow("code detector", img)
        if(cv2.waitKey(1) == ord("q")):
            break
    # free camera object and exit
    cap.release()
    cv2.destroyAllWindows()


class Account:
    def __init__(self,id,institutionUserid,institutionId,accountNumber,availableBalance,username,access_token,institutionCustomerId):
        self.id = id
        self.i_u_d = institutionUserid
        self.institutionId = institutionId
        self.accountNumber = accountNumber
        self.availableBalance = availableBalance
        self.username = username
        self.access_token = access_token
        self.customer = institutionCustomerId

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
    return emptyDict
    #access_token, expires_in, refresh_token, refresh_token_expires_in, token_type

def getAccounts(authData):
    url = "http://ncrdev-dev.apigee.net/digitalbanking/db-accounts/v1/accounts"
    payload={}
    headers = {
    'Authorization': 'Bearer ' + authData['access_token'],
    'transactionId': transactionId,
    'Accept': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()

#I NEED TO USE INSTITUTION CUSTOMER ID TO ALLOW TRANSFERS
def createTransfer(acctOne, recipient):
    url = "http://ncrdev-dev.apigee.net/digitalbanking/db-transfers/v1/transfers"
    payload="{\n    \"fromAccountHolderId\": \"" + acctOne.customer + "\",\n    \"fromAccountId\": \"rf5ao6Qclwsth9OfOvUb-EeV1m2BfmTzUEALGLQ3ehU\",\n    \"toAccountHolderId\": \"" + recipient + "\",\n    \"amount\": {\n        \"amount\": 50.0\n    }\n}"
    headers = {
    'Authorization': 'Bearer ' + acctOne.access_token,
    'transactionId': transactionId,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    #print(response.text)
    return response.json()['status']


def getChecking(authData):
    url = "http://ncrdev-dev.apigee.net/digitalbanking/db-accounts/v1/accounts/rf5ao6Qclwsth9OfOvUb-EeV1m2BfmTzUEALGLQ3ehU"
    payload={}
    headers = {
    'Authorization': 'Bearer ' + authData['access_token'],
    'transactionId': transactionId,
    'Accept': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()

def createRecipient(authData):
    url = "http://ncrdev-dev.apigee.net/digitalbanking/db-recipients/v1/recipients"
    payload="{\n    \"memberNumber\": \"WORLD\",\n    \"accountNumber\": \"00000019022\",\n    \"accountType\": \"CHECKING\",\n    \"passCode\": \"foo\",\n    \"email\": \"di.api.qal1@gmail.com\",\n    \"nickName\": \"buddy\"\n}"
    headers = {
    'transactionId': transactionId,
    'Authorization': 'Bearer ' + authData['access_token'],
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()['Recipients']
def getRecipients(authData):
    url = "http://ncrdev-dev.apigee.net/digitalbanking/db-recipients/v1/recipients"
    headers = {
    'transactionId': transactionId,
    'Authorization': 'Bearer ' + authData['access_token'],
    'Content-Type': 'application/json'
    }
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()['Recipients'][0]['id']

    

#main loop for script
#intializing User Account     def __init__(id,institutionUserid,institutionId,accountNumber,availableBalance,username,access_token):
"""
authData = getAuthenticate("HACKATHONUSER217","uga123")
acctOneData = getChecking(authData)
userAccount = Account(acctOneData['id'],acctOneData['institutionUserId'],acctOneData['institutionId'],acctOneData['accountNumber'],acctOneData['availableBalance'],"HACKATHONUSER217",authData['access_token'],acctOneData['institutionCustomerId'])
#This will act as the outside world/unlimited bank
authData = getAuthenticate("HACKATHONUSER218","uga123")
acctOneData = getChecking(authData)
worldAccount = Account(acctOneData['id'],acctOneData['institutionUserId'],acctOneData['institutionId'],acctOneData['accountNumber'],acctOneData['availableBalance'],"HACKATHONUSER218",authData['access_token'],acctOneData['institutionCustomerId'])
authData['access_token'] = userAccount.access_token
#print(userAccount.username + " " + userAccount.i_u_d + " " + str(userAccount.availableBalance['amount']))
#print(worldAccount.username + " " + worldAccount.i_u_d + " " + str(worldAccount.availableBalance['amount']))
#createRecipient(authData)
#createTransfer(userAccount,getRecipients())
"""
def makeATransaction(username,password,amount):
    authData = getAuthenticate(username,password)
    acctOneData = getChecking(authData)
    userAccount = Account(acctOneData['id'],acctOneData['institutionUserId'],acctOneData['institutionId'],acctOneData['accountNumber'],acctOneData['availableBalance'],"HACKATHONUSER217",authData['access_token'],acctOneData['institutionCustomerId'])
    #This will act as the outside world/unlimited bank
    #authData = getAuthenticate("HACKATHONUSER218","uga123")
    #acctOneData = getChecking(authData)
    #worldAccount = Account(acctOneData['id'],acctOneData['institutionUserId'],acctOneData['institutionId'],acctOneData['accountNumber'],acctOneData['availableBalance'],"HACKATHONUSER218",authData['access_token'],acctOneData['institutionCustomerId'])
    authData['access_token'] = userAccount.access_token
    #print(userAccount.username + " " + userAccount.i_u_d + " " + str(userAccount.availableBalance['amount']))
    createRecipient(authData)
    if(createTransfer(userAccount,getRecipients(authData)) == "SUCCESS"):
        return int(userAccount.availableBalance['amount']) + int(amount)
    else:
        return ""

"""
val = input("Welcome to your ATM press any key to continue")
val = input("Are you here to deposit or withdraw via QR code? (y/n)") 
if (val == 'y'):
    print("Scan your QR code now:")
    data = json.loads(scanQR())
    makeATransaction(data['u'],data['p'],data['amt'])
else:
    print("Have a great day!")
"""

class ATM(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.initImage()
        self.title("NCR ATM")
        self.geometry("1600x1200") 
        self.frame = None
        self.switch_frame(frameWelcome)
        self.username = ""
        self.amt = 0
        self.accountBal = 350
    #Switches frame on window
    def switch_frame(self, frameClass):
        newFrame = frameClass(self)
        if self.frame is not None:
            self.frame.pack_forget()
            x = threading.Thread(target=self.frame.destroy, args=())
        self.frame = newFrame
        self.frame.pack(fill=BOTH, expand=True)
    def initImage(self):
        ncr = PIL.Image.open("resources/ncr.png")
        ncr = ncr.resize((500, 150), PIL.Image.ANTIALIAS)
        im_ncr = ImageTk.PhotoImage(ncr)
        self.ncr_img = im_ncr
        scan = PIL.Image.open("resources/scan.png")
        scan = scan.resize((400, 100), PIL.Image.ANTIALIAS)
        im_scan = ImageTk.PhotoImage(scan)
        self.scan_img = im_scan
        mandep = PIL.Image.open("resources/mandep.png")
        mandep = mandep.resize((400,100), PIL.Image.ANTIALIAS)
        im_mandep = ImageTk.PhotoImage(mandep)
        self.mandep_img = im_mandep
        manwith = PIL.Image.open("resources/manwith.png")
        manwith = manwith.resize((400,100), PIL.Image.ANTIALIAS)
        im_manwith = ImageTk.PhotoImage(manwith)
        self.manwith_img = im_manwith


class frameWelcome(Frame):
    def __init__(self, master):
        Frame.__init__(self,master,bg="#51B948")
        Label(self,image=master.ncr_img,font=('arial', '50'),bg="#51B948").pack(pady=50)
        Button(self,image=master.scan_img,command=lambda:self.scanQR(master),borderwidth=0,bg="#51B948",activebackground="#51B948").pack(pady=10)
        Button(self,image=master.mandep_img,command=lambda:self.scanQR(master),borderwidth=0,bg="#51B948",activebackground="#51B948").pack(pady=10)
        Button(self,image=master.manwith_img,command=lambda:self.scanQR(master),borderwidth=0,bg="#51B948",activebackground="#51B948").pack(pady=10)

    def scanQR(self,master):
        data = json.loads(scanQR())
        master.username = data['u']
        master.accountBal = data['amt']
        makeATransaction(data['u'],data['p'],data['amt'])
        master.switch_frame(finishFrame)

class finishFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self,master,bg="#51B948")
        Label(self, text="Transaction Summary for", font=('arial', '48'),width=400,bg="#51B948",fg="white").pack(pady=(50,0))
        Label(self,text=master.username,font=('arial', '48'),width=400,bg="#51B948",fg="white").pack(pady=(0,50))
        Label(self,text="Previous Balance",font=('arial', '48'),bg="#51B948",fg="white").pack()
        Label(self,text="$350.00",font=('arial', '48'),bg="#51B948",fg="white").pack()
        Label(self,text="New Balance",font=('arial', '48'),bg="#51B948",fg="white").pack()
        Label(self,text="$%1.2f" %(350+float(master.accountBal)),font=('arial', '48'),bg="#51B948",fg="white").pack()


if __name__ == "__main__":
    app=ATM()
    app.mainloop(0)





