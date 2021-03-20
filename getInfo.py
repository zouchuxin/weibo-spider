#-*- coding = utf-8 -*-
#@Time : 2020/12/26 19:11
#@Author : zou chuxin
#@File: othersInfo.py
#@Software: PyCharm

import re
import urllib
import urllib.request
import time
import random


class GetInfo:
    def __init__(self,headers,userId):
        self.headers = headers
        self.userId = userId

    def get_infos(self):
        url1 = "https://weibo.cn/" + self.userId
        url2 = "https://weibo.cn/" + self.userId + "/info"
        datalist = [self.userId]
        datalist.extend(self.getData2(url2))
        datalist.extend(self.getData1(url1))
        print(datalist)
        time.sleep(random.randint(1, 3))
        return datalist

    #获取页面源码
    def askUrl(self,url):
        request = urllib.request.Request(url, headers = self.headers)
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        #print(html)
        return html





    # 获取用户粉丝数、微博数、关注数
    def getData1(self,url1):
        url = url1
        #print(url)
        html = self.askUrl(url)
        #print(html)
        pattern = re.compile(r'<div class="tip2"><span class="tc">微博\[(.*?)\]</span>&nbsp;.*?关注\[(.*?)\]</a>&nbsp;.*?粉丝\[(.*?)\]</a>')
        if re.findall(pattern, html) == []:
            result = ['0', '0', '0']
        else:
            result = list(re.findall(pattern, html)[0])
        return result

    # 获取用户个人信息（包括基本信息和学习经历）
    def getData2(self,url2):
        html = self.askUrl(url2)
        pattern1 = re.compile(r'<div class="tip">基本信息</div><div class="c">(.*?)</div>')   #爬取个人资料基本信息内容
        basicInfo = re.findall(pattern1,html)[0]
        basic_pattern = ['昵称:(.*?)<br/>', '性别:(.*?)<br/>', '地区:(.*?)<br/>', '生日:(.*?)<br/>', '简介:(.*?)<br/>', '认证:(.*?)<br/>']
        infoList = []
        #print(re.findall(basic_pattern[0], basicInfo))
        for i in range(6):
            if re.findall(basic_pattern[i], basicInfo) == []:
                infoList.append('无')
            else:
                infoList.extend(re.findall(basic_pattern[i], basicInfo))
        pattern2 = re.compile(r'<div class="tip">学习经历</div><div class="c">(.*?)<br/></div>')   #获取学习经历信息
        if re.findall(pattern2, html) == []:
            infoList.append('无')
        else:
            infoList.extend(re.findall(pattern2, html))
        #print(infoList)
        return infoList

