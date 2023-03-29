from cgi import print_arguments
from email.mime import image
from pydoc import cli
import random
import time
from paho.mqtt import client as mqtt_client
import base64
import json
import sys
import os
import time
from PIL import Image
from io import BytesIO
import cv2
import imageio
import matplotlib.pyplot as plt
import re
import np
import testModel as testModel
# broker = 'w1f3de21-internet-facing-d20ff3271ba3b92c.elb.ap-east-1.amazonaws.com'
broker = '175.178.117.244'
port = 1883
topic = "mytopic"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'heibaiyuanfen'
password = 'heibaiyuanfen890'

def connect_mqtt():
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(topic)
    else:
        print("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, msg):
        print(1)
        img_data=base64.b64decode(msg.payload) 
        print(1)
        payload = base64.b64decode(msg.payload)
        # data = payload

        # # image_url = os.path.join('D://%s.jpg' % int(time.time()))
        # # with open(image_url, 'wb') as f:
        # #     f.write(data)
        # base64_data = str(msg.payload).
        base64_data = re.sub('^data:image/.+;base64,', '', msg.payload.de code('utf-8'))
        print(base64_data)
        byte_data = base64.b64decode(base64_data)

        image_data = BytesIO(byte_data)
        print(image_data)
        img = Image.open(image_data)
        print(img)
        img.save("./test.png")
        # print(1)


        # nparr = np.frombuffer(img_data,np.uint8) 
        # print(1)
        # img=cv2.imdecode(nparr,cv2.COLOR_BGR2RGB)  
        # cv2.imwrite("result.jpg", img)
        # print(f"`{msg.payload}`")

def publish(client):
    msg_count = 0
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1
    
def run():
    client = connect_mqtt()
    RKNN_MODEL_PATH = 'class_20_25w.rknn'
    im_file = "/home/toybrick/Downloads/RKNNTest/model/ppp1.jpg"
    # #Create RKNN object
    rknn = testModel.RKNNLite()

    print('Loading RKNN model')
    ret = rknn.load_rknn(RKNN_MODEL_PATH)
    if ret != 0:
        print('load rknn model failed.')
        exit(ret)
    print('done')

    print('--> init runtime')
    # ret = rknn.init_runtime()
    ret = rknn.init_runtime()
    if ret != 0:
        print('init runtime failed.')
        exit(ret)
    print('done')

#     img = cv2.imread(im_file)
#     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (416, 416))

    # inference
    print('--> inference')
    outputs = rknn.inference(inputs=[img])
    print('done')

    input0_data = outputs[0]
    input1_data = outputs[1]

    print(len(input0_data[0][0]), len(input1_data[0][0]))

    input0_data = input0_data.reshape(testModel.SPAN, testModel.LISTSIZE, len(input0_data[0][0]), len(input0_data[0][0]))
    input1_data = input1_data.reshape(testModel.SPAN, testModel.LISTSIZE, len(input1_data[0][0]), len(input1_data[0][0]))

    input_data = []
    input_data.append(np.transpose(input0_data, (2, 3, 0, 1)))
    input_data.append(np.transpose(input1_data, (2, 3, 0, 1)))

    boxes, classes, scores = testModel.yolov3_post_process(input_data)
    #print(boxes)
    print(type(boxes),type(classes),type(scores))
    res =testModel.draw(img, boxes, classes, scores)
    cv2.imwrite("./1_3.jpg", res)
    rknn.release()
    
    client.loop_forever()

if __name__ == '__main__':
    run()