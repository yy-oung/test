import numpy as np
import cv2
import socketio
import base64
imdata = 0

sio = socketio.Client()
@sio.event
def streaming(data):
    data = cv2.imdecode(np.frombuffer(base64.b64decode(data), dtype='uint8'), cv2.IMREAD_COLOR)
    print(data)
    global imdata
    imdata = data
sio.connect('http://127.0.0.1:52273')

while True:
    sio.on('streaming', streaming)
    cv2.imshow('test', imdata)
    if cv2.waitKey(1) > 0: break
cv2.destroyAllWindows()
sio.disconnect()

#ClientProject\main.py