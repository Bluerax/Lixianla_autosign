# -*- coding: utf-8 -*-

import os
import requests
import json
from bs4 import BeautifulSoup
import base64
from urllib.parse import urlencode
import time
from urllib.parse import urljoin

token = os.environ['PushToken']
cookie = os.environ['Cookie']

requestUrl = os.environ['requestUrl']



apiUrl = "identify_GeneralCAPTCHA"
URL0 = "https://lixianla.com/"

def pushplus_push(token, title, content, topic):
    url = 'http://www.pushplus.plus/send'
    headers = {'Content-Type': 'application/json'}
    data = {
        'token': token,
        'title': title,
        'content': content,
        'topic': topic
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()


def sign(cookie):
    headers = {
        "Cookie": cookie,
        'accept': 'text/plain, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6',
        'dnt': '1',
        'referer': 'https://lixianla.com/',
        'sec-ch-ua': '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-requested-with': 'XMLHttpRequest',
    }

    session = requests.session()
    fa = session.get(
        URL0, headers=headers
    )
    #print(fa.text)
    soup1 = BeautifulSoup(fa.text, 'html.parser')
    url1 = soup1.find('button', {'class': 'btn btn-primary ft'}).get('data-modal-url')
    check = soup1.find('li', {'id': 'sg_sign'}).get('style')

    if 'display:none' in check:  # 检测 style 属性的值是否包含 'display:none'
        result = "LXL已经签过"
        print(result)
        pushplus_push(token=token, title=result, content=result, topic='')
    else:
        fb = session.get(urljoin(URL0, url1), headers=headers)
        soup2 = BeautifulSoup(fb.text, 'html.parser')
        # 找到验证码图片链接并获取
        img_url = soup2.find('img', {'class': 'vcode'}).get('src')
        img_response = session.get(URL0 + img_url, stream=True, headers=headers)
        result = ocr(img_response)
        print(result)

        # 填写验证码发送到签到接口
        form_data = {"vcode":str(result) }  # 填写需要提交的表单数据
        data1 = urlencode(form_data)
        data0 = data1.encode('utf-8')
        data2 = data0.decode('utf-8')
        response2 = session.post(urljoin(URL0, url1), data=data2, headers=headers)
        print(response2.text)
        message = response2.json()['message']
        checkR(message)


def ocr(img_response):
    # 将验证码图片转换为base64编码并发送到识别接口
    encoded_string = base64.b64encode(img_response.content).decode('utf-8')
    form_data = {"ImageBase64": str(encoded_string)}  # 填写表单数据
    headers2 = {
        "Content-Type": "application/json",
    }
    response = requests.post(requestUrl + apiUrl, data=json.dumps(form_data), headers=headers2)
    # print(json.dumps(form_data))
    result = response.json()['result']

    return result


def checkR(message):
    # 判断签到结果
    if "登录" in message:
        result = "LXLCookie 失效"
    elif "验证码错误" in message:
        result = "LXL验证码错误"
        time.sleep(10)
        sign(cookie=cookie)
    elif "成功" in message:
        result = "LXL签到成功"
    else:
        result = "LXL签到失败"
    print(result)

    pushplus_push(token=token, title=result, content=message, topic='')
    return


def main():
    pushplus_push(token = token, title =requestUrl, content = cookie , topic="")
    sign_msg = sign(cookie=cookie)
    print(sign_msg)

if __name__ == "__main__":
    main()


