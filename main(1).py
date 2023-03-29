from typing_extensions import Self
from urllib.request import urlopen
import base64
import os
import sys
import time
from ctypes import *
from loguru import logger
import cv2
import numpy as np
import urllib.request
import json
import paho.mqtt.client as mqtt
import yaml
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

library = cdll.LoadLibrary(
    "/usr/lib/libface_offline_sdk.so")

logger.add("./log/face_ai_box.{time:YYYY-MM-DD}.log", rotation="00:00")

params_error = {
    "errno": -1002,
    "msg": "param error",
    "data": {
        "log_id": "0"
    }
}

get_img_error = {
    "errno": -999,
    "msg": "get image fail, Please confirm that the image address is valid!",
    "data": {
        "log_id": "0"
    }
}


def getImgBase64(image_url):
    try:
        if image_url:
            resp = urllib.request.urlopen(image_url)
            return base64.b64encode(resp.read()).decode()
        else:
            return ''
    except Exception as error:
        print(error)
        logger.error(image_url + "图片获取失败")
        return ''


def user_add(user_id, group_id, img_url):
    image_base64 = getImgBase64(img_url)
    if image_base64 is '':
        return get_img_error
    else:
        image_p = c_char_p(bytes(image_base64, 'utf-8'))
        user_id_p = c_char_p(bytes(user_id, 'utf-8'))
        group_id_p = c_char_p(bytes(group_id, 'utf-8'))
        res = library.user_add(user_id_p, group_id_p, image_p)
        res_json = json.loads(res.decode('UTF-8'))
        return res_json


def user_update(user_id, group_id, img_url):
    image_base64 = getImgBase64(img_url)
    if image_base64 is '':
        return get_img_error
    else:
        image_p = c_char_p(bytes(image_base64, 'utf-8'))
        user_id_p = c_char_p(bytes(user_id, 'utf-8'))
        group_id_p = c_char_p(bytes(group_id, 'utf-8'))
        res = library.user_update(user_id_p, group_id_p, image_p)
        res_json = json.loads(res.decode('UTF-8'))
        return res_json


def user_delete(user_id, group_id):
    user_id_p = c_char_p(bytes(user_id, 'utf-8'))
    group_id_p = c_char_p(bytes(group_id, 'utf-8'))
    res = library.user_delete(user_id_p, group_id_p)
    res_json = json.loads(res.decode('UTF-8'))
    return res_json


def group_add(group_id):
    group_id_p = c_char_p(bytes(group_id, 'utf-8'))
    res = library.group_add(group_id_p)
    res_json = json.loads(res.decode('UTF-8'))
    return res_json


def group_delete(group_id):
    group_id_p = c_char_p(bytes(group_id, 'utf-8'))
    res = library.group_delete(group_id_p)
    res_json = json.loads(res.decode('UTF-8'))
    return res_json


# 人脸组比�?:N
def identify(group_id, img_url):
    image_base64 = getImgBase64(img_url)
    if image_base64 is '':
        return get_img_error
    else:
        image_p = c_char_p(bytes(image_base64, 'utf-8'))
        group_id_p = c_char_p(bytes(group_id, 'utf-8'))
        res = library.identify(group_id_p, image_p)
        res_json = json.loads(res.decode('UTF-8'))
        return res_json


# 人脸库对�?:N
def identify_with_all(img_url):
    image_base64 = getImgBase64(img_url)
    if image_base64 is '':
        return get_img_error
    else:
        image_p = c_char_p(bytes(image_base64, 'utf-8'))
        res = library.identify_with_all(image_p)
        res_json = json.loads(res.decode('UTF-8'))
        return res_json


def get_device_id():
    return library.get_device_id().decode('UTF-8')


def load_config():
    if not os.path.exists('config.yaml'):
        logger.error('config.yaml is not exists')
        sys.exit(0)
    file = open('config.yaml', 'r', encoding='utf-8')
    datas = yaml.load(file, Loader=yaml.FullLoader)
    if datas is None:
        logger.error('配置文件错误!配置文件为空')
        sys.exit(0)
    if 'mqtt-server' not in datas:
        logger.error('配置文件参数错误!缺失[mqtt-server]')
        sys.exit(0)
    if 'ip' not in datas['mqtt-server']:
        logger.error('配置文件参数错误!缺失[mqtt-server][ip]')
        sys.exit(0)
    if 'port' not in datas['mqtt-server']:
        logger.error('配置文件参数错误!缺失[mqtt-server][port]')
        sys.exit(0)

    ip = datas['mqtt-server']['ip']
    port = datas['mqtt-server']['port']
    username = None
    password = None
    if 'username' in datas['mqtt-server']:
        username = datas['mqtt-server']['username']
    if 'password' in datas['mqtt-server']:
        password = datas['mqtt-server']['password']
    return ip, port, username, password


def init():
    library.user_add.restype = c_char_p
    library.user_update.restype = c_char_p
    library.user_delete.restype = c_char_p
    library.group_add.restype = c_char_p
    library.group_delete.restype = c_char_p
    library.identify.restype = c_char_p
    library.identify_with_all.restype = c_char_p
    library.get_device_id.restype = c_char_p
    sdk_init_res = library.face_sdk_init()

    if sdk_init_res != 0:
        logger.error("SDK初始化失�?错误代码:" + str(sdk_init_res))
        sys.exit(0)
    logger.info("SDK初始化成�?")

def run():
    broker, port, username, password = load_config()
    MqttClient(ip=broker, port=port, username=username, password=password)
    library.destroy_sdk()


class MqttClient:
    def __init__(self, ip, port, username=None, password=None) -> None:
        self.ip = ip
        self.port = port
        self.device_id = get_device_id()
        logger.info('获取机器mId成功!mId:' + self.device_id)
        client_id = self.device_id
        self.report_topic = "DAQ/MB/V2/" + self.device_id + "/Data"
        self.will_topic = "DAQ/MB/V2/" + self.device_id + "/Will"
        self.cmd_sub_topic = "DAQ/MB/V2/" + self.device_id + "/Cmd"
        self.client = mqtt.Client(client_id, transport='tcp')
        self.server_conenet(client=self.client, username=username, password=password)

    # 订阅回调函数
    def on_connect(self, client, userdata, flags, rc):
        logger.info('connected to mqtt with resurt code ' + str(rc))
        client.subscribe(self.cmd_sub_topic)  # 订阅主题

    def send_msg(self, oper, seq, msg):
        msg.update(oper=oper)
        msg.update(seq=seq)
        msg.update(mId=self.device_id)
        msg.update(timestamp=int(time.time()))
        logger.info(json.dumps(msg))
        self.client.publish(self.report_topic, json.dumps(msg))

    def on_message(self, client, userdata, msg):
        """
        接收客户端发送的消息
        :param client: 连接信息
        :param userdata:
        :param msg: 客户端返回的消息
        :return:
        """
        try:

            msg = json.loads(msg.payload.decode('utf-8'))
            mId = msg.get('mId')
            oper = msg.get('oper')
            seq = msg.get('seq')
            data = dict(msg.get('data'))
            if mId is None or oper is None or seq is None or data is None or mId != self.device_id:
                logger.error('基础参数有误,mId,oper,seq,data之一缺失')
            else:
                if oper == 101:
                    userId = data.get('userId')
                    groupId = data.get('groupId')
                    imgUrl = data.get('imgUrl')
                    if userId is None or groupId is None or imgUrl is None:
                        logger.error('操作' + str(oper) + '内部参数有误,传入参数�? + json.dumps(data))
                        self.send_msg(oper, seq, params_error)
                    else:
                        res = user_add(userId, groupId, imgUrl)
                        self.send_msg(oper, seq, res)
                elif oper == 102:
                    userId = data.get('userId')
                    groupId = data.get('groupId')
                    imgUrl = data.get('imgUrl')
                    if userId is None or groupId is None or imgUrl is None:
                        logger.error('操作' + str(oper) + '内部参数有误,传入参数�? + json.dumps(data))
                        self.send_msg(oper, seq, params_error)
                    else:
                        res = user_update(userId, groupId, imgUrl)
                        self.send_msg(oper, seq, res)
                elif oper == 103:
                    userId = data.get('userId')
                    groupId = data.get('groupId')
                    if userId is None or groupId is None:
                        logger.error('操作' + str(oper) + '内部参数有误,传入参数�? + json.dumps(data))
                        self.send_msg(oper, seq, params_error)
                    else:
                        res = user_delete(userId, groupId)
                        self.send_msg(oper, seq, res)
                elif oper == 104:
                    groupId = data.get('groupId')
                    if groupId is None:
                        logger.error('操作' + str(oper) + '内部参数有误,传入参数�? + json.dumps(data))
                        self.send_msg(oper, seq, params_error)
                    else:
                        res = group_add(groupId)
                        self.send_msg(oper, seq, res)
                elif oper == 105:
                    groupId = data.get('groupId')
                    if groupId is None:
                        logger.error('操作' + str(oper) + '内部参数有误,传入参数�? + json.dumps(data))
                        self.send_msg(oper, seq, params_error)
                    else:
                        res = group_delete(groupId)
                        self.send_msg(oper, seq, res)
                elif oper == 201:
                    imgUrl = data.get('imgUrl')
                    if imgUrl is None:
                        logger.error('操作' + str(oper) + '内部参数有误,传入参数�? + json.dumps(data))
                        self.send_msg(oper, seq, params_error)
                    else:
                        res = identify_with_all(imgUrl)
                        self.send_msg(oper, seq, res)
                elif oper == 202:
                    imgUrl = data.get('imgUrl')
                    groupId = data.get('groupId')
                    if imgUrl is None:
                        logger.error('操作' + str(oper) + '内部参数有误,传入参数�? + json.dumps(data))
                        self.send_msg(oper, seq, params_error)
                    else:
                        res = identify(groupId, imgUrl)
                        self.send_msg(oper, seq, res)
        except Exception as error:
            logger.error(error)

    # 服务监听
    def server_conenet(self, client, username=None, password=None):
        client.on_connect = self.on_connect  # 启用订阅模式
        client.on_message = self.on_message  # 接收消息
        if username is not None:
            client.username_pw_set(username=username, password=password)
        client.will_set(self.will_topic, "last will message", 0, False)
        client.connect(self.ip, self.port, 60)  # 链接
        # client.loop_start()   # 以start方式运行，需要启动一个守护线程，让服务端运行，否则会随主线程死亡
        client.loop_forever()  # 以forever方式阻塞运行�?

    # 服务停止
    def server_stop(client):
        client.loop_stop()  # 停止服务�?
        sys.exit(0)


if __name__ == '__main__':
    init()
    run()
