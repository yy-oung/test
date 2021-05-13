from __future__ import division
from gaze_tracking import GazeTracking
from flask import Flask, Response,render_template, Response
from eye import Eye
from calibration import Calibration
import pyaudio
import cv2
import speech_recognition as sr
import numpy as np
import time
import datetime
import sys
import os
import dlib

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "./haarcascade_frontalface_default.xml") # 얼굴찾기 haar 파일
#eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +"./haarcascade_eye.xml") # 눈찾기 haar 파일
 
num = 3
app = Flask(__name__)
camera = cv2.VideoCapture(0)  # use 0 for web camera


@app.route('/')
def index():
    """Video streaming home page."""
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    templateData = {
            'title':'Image Streaming',
            'time': timeString
            }
    return render_template('index2.html', **templateData)

#안면인식
def gen_frames():
    camera = cv2.VideoCapture(0)
    time.sleep(0.2)
    lastTime = time.time()*1000.0


#시선추적
    gaze = GazeTracking()


    while True:

        ret, image = camera.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
       
        faces = faceCascade.detectMultiScale(gray,scaleFactor=1.3,minNeighbors=5)

        delt = time.time()*1000.0-lastTime
        s = str(int(delt))
        #print (delt," Found {0} faces!".format(len(faces)) )
        lastTime = time.time()*1000.0

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.circle(image, (int(x+w/2), int(y+h/2)), int((w+h)/3), (255, 255, 255), 3)
            cv2.putText(image, s, (10, 25),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        now = datetime.datetime.now()
        timeString = now.strftime("%Y-%m-%d %H:%M")
        cv2.putText(image, timeString, (10, 45),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        #cv2.imshow("Frame", image)

        #시선추적
        gaze.refresh(image)
        image = gaze.annotated_frame()

        text = ""

        if gaze.is_right():
            text = "Looking right"
        elif gaze.is_left():
            text = "Looking left"
        elif gaze.is_center():
            text = "Looking center"

        cv2.putText(image, text, (10,65), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 0, 0), 2)
        cv2.imshow("Demo", image)



        key = cv2.waitKey(1) & 0xFF


     # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
   
        ret, buffer = cv2.imencode('.jpg', image)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5


audio1 = pyaudio.PyAudio()

def genHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o


#뭐라 말했는지 음성인식
@app.route('/upload/')
def uploaduj():
    transcript=""
    recognizer =  sr.Recognizer()        
    with sr.Microphone() as source:
        print('Speak Anything : ')
        audio = recognizer.listen(source)
    try:
        transcript = recognizer.recognize_google(audio,language='ko-KR')
        print('You said : {}'.format(transcript))
    except:
        print('Sorry could not recognize yur voice')           

#특정 키워드를 말할 때 예를 들어 정답
    cheat = 0
    if transcript.find('정답') != -1 :
        cheat=1

    return render_template('index2.html', transcript=transcript, cheat=cheat)



#오디오 스트리밍 서버였는디
@app.route('/audio')
def audio():
    # start Recording
    def sound():

        CHUNK = 1024
        sampleRate = 44100
        bitsPerSample = 16
        channels = 2
        wav_header = genHeader(sampleRate, bitsPerSample, channels)

        stream = audio1.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,input_device_index=1,
                        frames_per_buffer=CHUNK)
        print("recording...")
        #frames = []
        first_run = True
        while True:
           if first_run:
               data = wav_header + stream.read(CHUNK)
               first_run = False
           else:
               data = stream.read(CHUNK)
           yield(data)

    return Response(sound())


if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True)

