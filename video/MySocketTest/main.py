import cv2
import time
import base64
import socketio

sio = socketio.Client()
sio.connect('http://127.0.0.1:52273')

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

while True:
    time.sleep(0.1)
    ret, frame = cap.read()
    result, frame = cv2.imencode('.jpg', frame, encode_param)
    b64data = base64.b64encode(frame)
    sio.emit('streaming', b64data)
    if cv2.waitKey(1) > 0: break
sio.disconnect()

#MySocketTest\main.py