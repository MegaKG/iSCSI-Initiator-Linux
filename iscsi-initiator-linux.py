#!/usr/bin/env python3
import subprocess
from tkinter import *
import datetime

PORTALS = []


def runcommand(COMMAND):
 try:
    return subprocess.check_output(COMMAND, shell=True).decode("utf-8")
 except:
     return False

def discover(IP):
 #Discover the Portals
 DISCOVERCOMMAND = "iscsiadm -m discovery -t sendtargets -p <IP>"
 results = runcommand(DISCOVERCOMMAND.replace('<IP>',IP))

 #Add to Portals Table
 global PORTALS
 for item in results.split('\n'):
     if item != '':
        PORTALS.append(item)

def disconnectfrom(CMD):
    COM = "iscsiadm -m node -T <PORTAL> -p <IP>:3260 -u"
    IP = CMD.split(':')[0]
    PORTAL = CMD.split(' ')[1]

    COM = COM.replace('<PORTAL>',PORTAL)
    COM = COM.replace('<IP>',IP)
    A = runcommand(COM)  

    COM = "iscsiadm -m node -o delete -T <PORTAL>"

    COM = COM.replace('<PORTAL>',PORTAL)
    B = runcommand(COM)
    return str(A) + '  ' + str(B) 

def connectto(CMD):
    COM = "iscsiadm --mode node --targetname <PORTAL> --portal <IP>:3260 --login"
    IP = CMD.split(':')[0]
    PORTAL = CMD.split(' ')[1]

    COM = COM.replace('<PORTAL>',PORTAL)
    COM = COM.replace('<IP>',IP)

    return runcommand(COM)



def mainwindow():
    root = Tk()


    #The Discovery Part
    findportalframe = Frame(root)

    L = Label(findportalframe,text='IP: ')
    L.grid(row=0,column=0)

    ENT = Entry(findportalframe,width=15)
    ENT.grid(row=0,column=1)

    def getipanddiscover():
        DAT = ENT.get()
        discover(DAT)
    GETB = Button(findportalframe,text='Add',command=getipanddiscover)
    GETB.grid(row=0,column=3)

    #The Available Portals
    availableportalframe = Frame(root)
    Available = Listbox(availableportalframe,width=100)
    Available.grid(row=0,column=0)

    MSG = StringVar()
    L = Label(availableportalframe,textvariable=MSG)
    L.grid(row=2,column=0)
    MSG.set('Ready')

    def getiqn(INPHRASE):
        return INPHRASE.split(' ')[1]

    

    DONE = []
    def synclist():
        nonlocal DONE
        STATUS = runcommand('iscsiadm -m session')
        for i in PORTALS:
            if i not in DONE:
                if STATUS != False:
                    if getiqn(i) in STATUS:
                        Available.insert(END,i + ' ' + 'CONNECTED')
                    else:
                        Available.insert(END,i + ' ' + 'READY')
                
                else:
                   Available.insert(END,i + ' ' + 'READY')
                DONE.append(i)
    
    def getselection():
        
        SELECTION = int(Available.curselection()[0])

        nonlocal DONE
        DONE = []
        Available.delete(0,END)

        LONGSTRING = PORTALS[SELECTION]
        DAT = connectto(LONGSTRING)
        if 'success' in DAT:
            MSG.set(str(datetime.datetime.now()) + ' Connection Successful')
        else:
            MSG.set(str(datetime.datetime.now()) + ' Connection Failed')

    def getselection2():
        SELECTION = int(Available.curselection()[0])
        nonlocal DONE
        DONE = []
        Available.delete(0,END)
        LONGSTRING = PORTALS[SELECTION]
        DAT = disconnectfrom(LONGSTRING)
        MSG.set( str(datetime.datetime.now()) + ' ' + str(DAT))

    GO = True
    def kill():
        nonlocal GO
        GO = False

    BF = Frame(availableportalframe)
    CONB = Button(BF,text="Connect",command=getselection)
    CONB.grid(row=0,column=0)
    UNCONB = Button(BF,text="Disconnect",command=getselection2)
    UNCONB.grid(row=0,column=1)
    QUIT = Button(BF,text='Quit',command=kill)
    QUIT.grid(row=0,column=2)


    BF.grid(row=1,column=0)

    #The Main Window
    root.title("Python iSCSI Initaitor")
    findportalframe.grid(row=0,column=0)
    availableportalframe.grid(row=1,column=0)


    
    import time
    while GO:
        root.update()
        availableportalframe.update()
        time.sleep(0.1)
        synclist()

    root.destroy()

if __name__ == '__main__':
    mainwindow()