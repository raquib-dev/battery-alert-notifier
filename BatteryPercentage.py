# python script showing battery details
import os
import psutil
import shutil
import datetime
from time import sleep
import sys
from plyer import notification
from dotenv import load_dotenv

load_dotenv()

import tkinter
app = tkinter.Tk()

live = "Live"
maximum = int(os.getenv('maximum',90))
minimum = int(os.getenv('minimum',20))
interval = int(os.getenv('interval',15))

def createFolder(directory,file_name,data):

    date_time=datetime.datetime.now()
    curtime1=date_time.strftime("%d/%m/%Y %H:%M:%S")
    curtime2=date_time.strftime("%d-%m-%Y")
    directory = directory + str(curtime2) + '/'
    # print(directory)
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)

        # deleting old log files
        old_date = (datetime.datetime.now() + datetime.timedelta(days=-5)).date()
        file_list = os.listdir('Log')
        for file in file_list:
            try:
                file_date = datetime.datetime.strptime(file, '%d-%m-%Y').date()
            except:
                shutil.rmtree('Log/'+file)
            if file_date <= old_date:
                shutil.rmtree('Log/'+file)

        f= open(directory+str(file_name)+".txt","a+")
        f.write(curtime1 +" "+ str(data) +"\r\n")
        f.close()

    except OSError:
        print ('Error: Creating directory. ' +  directory)

while True :

    try:
        
        # returns a tuple
        battery = psutil.sensors_battery()

        # determine if application is a script file or frozen exe
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)

        icon_path = f'{application_path}/logo.ico'

        if battery.percent >= maximum and battery.power_plugged == True :
            
            if notification.is_notification_active():
                notification.close()

            notification.notify(title='Battery Alert Notification',message=f'Battery full {battery.percent}% - Unplug your charger',app_name='AusNotifier',timeout=10,app_icon=icon_path)
            createFolder('Log/',live,f"Your Battery is fully charged - {battery.percent}% . Please unplug you charger !!")

        elif battery.percent <= minimum and battery.power_plugged == False :

            notification.notify(title='Battery Alert Notification',message=f'Battery Low {battery.percent}% - Connect your charger',app_name='AusNotifier',timeout=10,app_icon=icon_path)
            createFolder('Log/',live,f"Battery Low {battery.percent}% - Connect your charger")

        elif battery.percent >= maximum :
            createFolder('Log/',live,f"Your Battery Almost fully Charged . Battery Percentage is {battery.percent}% .")
        else:
            createFolder('Log/',live,f"Your Battery not yet charged above {maximum}% . Battery Percentage is {battery.percent}% .")

    except Exception as e:
        createFolder('Log/',live,f"Error - {e}")
    
    sleep(30)