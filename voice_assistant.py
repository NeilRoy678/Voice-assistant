import audioop
from asyncio.protocols import DatagramProtocol
from hashlib import new
import math
import re
from typing import Text
import pyttsx3
import speech_recognition as sr
import python_weather
import asyncio
import webbrowser
import datetime 
import os

import subprocess
import time
import sys   
from PyQt5.QtGui import QFont,QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtCore  import * 
from PyQt5 import QtWidgets
from PyQt5 import QtCore
#from test import authenticate_google, get_date, get_events
import wolframalpha

import os.path
from ssl import SSLCertVerificationError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pytz
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june","july", "august", "september","october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]
class Worker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal()
    def __init__(self) -> None:
        super().__init__()
        self.flag = True

    def audio(self,text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        
    def start(self):
        self.progress.emit("Hello I am your virtual assistant")
        self.audio("Hello I am your virtual assistant")
        
    def get_commands(self):

        r = sr.Recognizer()
        language = "en"
        with sr.Microphone() as source:
                print("SPEAK")
                #self.progress.emit("speak")
                r.pause_threshold = 1
                audio = r.listen(source)
                try:
                    voice_data = r.recognize_google(audio,language = language)
                    print("recognizing..")
                    self.progress.emit("recognizing....")
                    print(voice_data)   
                    self.progress.emit(f"me {voice_data}")
                    
                except Exception as e:
                    #MainWindow.commands()
                    #self.obj.commands()
                    voice_data = self.get_commands()
        return voice_data

        
    async def getweather(self,city):
        # declare the client. format defaults to metric system (celcius, km/h, etc.)
        client = python_weather.Client()

        # fetch a weather forecast from a city
        weather = await client.find(city)

        # returns the current day's forecast temperature (int)
        print("Todays Temperature is : "+ str(weather.current.temperature)+ " Degree celsius")
        self.progress.emit("Todays Temperature is :"+ str(weather.current.temperature)+ " Degree celsius" + "It is " + weather.current.sky_text)
        self.audio("Todays Temperature is : "+ str(weather.current.temperature)+ " Degree celsius " + "It is" + weather.current.sky_text)
       
        #print(weather.current.sky_text)
        # get the weather forecast for a few days

        # close the wrapper once done
        await client.close()
    def apps(self,text,res):

        if "youtube" in res:
            self.progress.emit("Opening Youtube")
            self.audio("Opening Youtube")
            
            webbrowser.open("https://www.youtube.com/")
        elif "google" in res:
            self.progress.emit("Opening Google")
            self.audio("Opening Google")
            webbrowser.open("https://www.google.com/")
        elif "twitter" in res:
            self.progress.emit("Opening Twitter")
            self.audio("Opening Twitter")
            webbrowser.open("https://twitter.com/home")
        elif "stack" in res and "overflow" in res:
            self.progress.emit("Opening Stackoverflow")
            self.audio("Opening Stackoverflow")
            webbrowser.open("https://stackoverflow.com")  
        elif "camera" in res:
            self.progress.emit("Opening Camera")
            os.system('start explorer shell:appsfolder\Microsoft.WindowsCamera_8wekyb3d8bbwe!App')
        elif "calculator" in res:
            self.progress.emit("Opening Calculator")
            self.audio("Opening Calculator")
            os.system('start explorer shell:appsfolder\Microsoft.WindowsCalculator_8wekyb3d8bbwe!App')
        elif "steam" in res:
            self.progress.emit("Opening Steam")
            self.audio("Opening Steam")
            subprocess.call('C:\\Program Files (x86)\\Steam\\steam.exe')
        elif "photo" in res:
            self.progress.emit("Opening Photos")
            self.audio("Opening Photos")
            os.system('start explorer shell:appsfolder\Microsoft.Windows.Photos_8wekyb3d8bbwe!App')
        
            
        # elif "epic games":
        # elif "Maps":

        elif "Notepad":
            self.progress.emit("Opening Notepad")
            self.audio("Opening Notepad")
            os.system("Notepad")

    def get_events(self,day, service):
        # Call the Calendar API
        try:
            date = datetime.datetime.combine(day, datetime.datetime.min.time())
            end = datetime.datetime.combine(day, datetime.datetime.max.time())
            utc = pytz.UTC
            date = date.astimezone(utc)
            end = end.astimezone(utc)
            events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end.isoformat(),
                                                singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')
                self.progress.emit("No Upcoming Events Found")
                self.audio("No Upcoming Events Found")
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                self.progress.emit(event["summary"])
                self.audio(event["summary"])
                print(start, event['summary'])
        except:
            self.audio("Sorry Didnt Get that")

    def get_date(self,text):
        text = text.lower()
        today = datetime.date.today()

        if text.count("today") > 0:
            return today
        day = -1
        day_of_week = -1
        month = -1
        year = today.year

        for word in text.split():
            if word in MONTHS:
                month = MONTHS.index(word) + 1
            elif word in DAYS:
                day_of_week = DAYS.index(word)
            elif word.isdigit():
                day = int(word)
            else:
                for ext in DAY_EXTENTIONS:
                    found = word.find(ext)
                    if found > 0:
                        try:
                            day = int(word[:found])
                        except:
                            pass
        if month < today.month and month != -1:  # if the month mentioned is before the current month set the year to the next
            year = year+1

    # This is slighlty different from the video but the correct version
        if month == -1 and day != -1:  # if we didn't find a month, but we have a day
            if day < today.day:
                month = today.month + 1
            else:
                month = today.month

        # if we only found a dta of the week
        if month == -1 and day == -1 and day_of_week != -1:
            current_day_of_week = today.weekday() 
            dif = day_of_week - current_day_of_week

            if dif < 0:
                dif += 7
                if text.count("next") >= 1:
                    dif += 7

            return today + datetime.timedelta(dif)

        if day != -1:  # FIXED FROM VIDEO
            return datetime.date(month=month, day=day, year=year)
    def authenticate_google():
            """Shows basic usage of the Google Calendar API.
            Prints the start and name of the next 10 events on the user's calendar.
            """
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret_875910665888-tv3dr3o0d6i58624f1dp87061dkmb400.apps.googleusercontent.com.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            service = build('calendar', 'v3', credentials=creds)
            return service
    def main(self):
        #service = authenticate_google()
        self.start()
        voice_data = ""
        maths = ["integration"]
        #print(self.flag)
        while True:
            
            voice_data = self.get_commands().lower()

            res = []
            res = voice_data.split()
            print(res)
            

            if "weather" in res:
                self.progress.emit("Which City")
                self.audio("Which City")
                city = self.get_commands()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.getweather(city))

            elif "event" in res or "events" in res:
                
                res = voice_data.split(' ')
                new_text = res[0]
                for i in res[2:]:
                    new_text = new_text+ " " + i
                print(new_text)
                self.get_events(self.get_date(new_text),service)
            elif "time" in res:
                time_ = time.strftime("%I:%M %p")
                print(time_[1:])
                if time_[0] == 0:
                    self.progress.emit(f"Time is {time_[1:]}")
                    self.audio(time_[1:])
                else:
                    self.progress.emit(f"Time is  {time_}")
                    self.audio(time_)    

            elif "date" in res:
                
                data = datetime.datetime.now().strftime("Today is %d %b 20%y")
                self.progress.emit(f"{data}")
                print(data)
                self.audio(data)

            elif "what" in res or "how"in res or "why" in res or "when" in res or "who" in res:
                new_text= res[0]
                for i in res[1:]:
                    new_text = new_text + "+" + i
                self.progress.emit("Here is what i found")
                self.audio("Here is what i Found")
                webbrowser.open(f"https://www.google.com/search?channel=trow5&client=firefox-b-d&q={new_text}")
                
            elif "create" in res and "note" in res:
                self.progress.emit("What should i write")
                self.audio("What should i write")
                #time = datetime.datetime.now()

                note_text = self.get_commands()
                note = open('note.txt','a')
                note.write("\n")
                #note.write(str(time))
                #note.write(" :- ")
                note.write(note_text)
                note.close()

            elif "read" in res and "note" in res: 
                note = open('note.txt','r')
                text = note.read()
                print(text)
                self.progress.emit(f"{text}")
                self.audio(text)

            elif "open" in res:
                try:
                    text = res[1]
                    self.apps(text,res)
                except:
                    self.progress.emit("Sorry Didnt get that")
                    self.audio("Sorry Didnt get that")    
            elif "exit" in res:
                self.progress.emit("Exiting have a nice day")
                self.audio("Exiting have a nice day")
                
                break

            elif "search" in res and "youtube" in res:
                self.progress.emit("What should I Search")
                self.audio("What should I Search")
                text = self.get_commands()
                res = text.split(' ')
                new_text= res[0]
                for i in res[1:]:
                    new_text = new_text + "+" + i
                webbrowser.open(f"https://www.youtube.com/results?search_query={new_text}")
           
            elif "calculate" in res:

                    app_id = " 6PYWL5-76K5Q972UV"
                    client = wolframalpha.Client(app_id)
                    #indx = query.lower().split().index('calculate')
                    
                    question = client.query(' '.join(res[1:]))
                    answer = next(question.results).text
                    print("The answer is " + answer)
                    self.progress.emit("Then Answer is " + answer)
                    self.audio("The answer is " + answer)

             


        self.finished.emit()
class MainWindow(QWidget):
    def __init__(self,parents = None)->None:
        super().__init__()
        self.flag = True
        self.progress = pyqtSignal(int)
        
        self.main_ui()

    def main_ui(self):
        
        self.Textbox = QTextEdit()
        self.Textbox.setMinimumHeight(500)
        self.setWindowTitle("Voice Assistant")
        self.Textbox.setMinimumWidth(500)
        self.Textbox.setFontPointSize(15)
        self.Textbox.setReadOnly(True)
        self.grid = QGridLayout()
        self.Textbox.resize(200,100)
        self.button = QPushButton("Start")
        self.button1 = QPushButton("Stop")
        self.button.clicked.connect(self.commands)
        #self.setGeometry(0, 0, 200, 100)
 
        # creating label
        self.label = QLabel(self)
         
        # loading image
        self.pixmap = QPixmap('assistant_logo.jpg')
        #self.pixmap = self.pixmap.scaledToWidth(64)
        self.pixmap = self.pixmap.scaledToHeight(128)
        # adding image to label
        self.label.setPixmap(self.pixmap)
        self.grid.addWidget(self.Textbox,3,0)
        self.grid.addWidget(self.button,4,0)
        self.grid.addWidget(self.label,3,1)
        

        self.setLayout(self.grid)

    def commands(self):
        self.flag = True
        self.Textbox.clear()
        self.worker = Worker()
        self.thread = QThread()
        
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.main)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportprogress)
        self.thread.start()
        self.button.setEnabled(False)
        

        self.thread.finished.connect(
            lambda: self.button.setEnabled(True)
        )
    def reportprogress(self,n):
        n = n.split(' ')
        string = ""
        if n[0]!= "me":
            string = ' '.join([str(i) for i in n])
            self.Textbox.append("Bot:" + string)
            self.Textbox.append("\n")
        else:
            string = ' '.join([str(i) for i in n[1:]])
            self.Textbox.append("Me:" + string)
            self.Textbox.append("\n")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    obj = MainWindow()
    obj.show()
    sys.exit(app.exec_())



            

    