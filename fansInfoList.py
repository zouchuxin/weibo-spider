#-*- coding = utf-8 -*-
#@Time : 2020/12/30 15:13
#@Author : zou chuxin
#@File: fansList.py
#@Software: PyCharm

import requests
import csv
import time
import random
import pymysql
from weibo_spide_2021.getInfo import GetInfo

class FansInfolist:
    def __init__(self,headers,userId,mysql_config):
        self.headers = headers
        self.userId = userId
        self.mysql_config = mysql_config


    def get_fansinfolist(self):
        url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_" + self.userId
        fansNum = self.get_fans_num(self.userId, self.headers)
        html = []
        html.append(self.get_html(url, self.headers))
        savepath = ".\\" + self.userId + "粉丝信息.csv"
        if fansNum % 20 == 0:
            page = fansNum // 20
        else:
            page = fansNum // 20 + 1  # 获取页面数
        print("粉丝页数：",page)
        fansList = []
        fansList.extend(self.parse_html(-1, html[0]))  # 增加第一页粉丝数据
        if page > 1:
            for i in range(0, page):
                new_html = self.get_html_new(url, html[i], self.headers)  # 判断是否最后一页（通过since_id)判断
                if new_html == None:
                    break
                else:
                    html.append(new_html)
                    html_info = self.parse_html(i, html[i + 1])  # 判断是否最后一页，通过最后一页是否有数据判断
                    if html_info == None:
                        break
                    else:
                        fansList.extend(html_info)
                i = i + 1
                time.sleep(random.randint(1, 3))
        print(fansList)
        self.data_write_csv(savepath, fansList)

        self.data_save_mysql(fansList, self.userId)


    #获取第一页内容
    def get_html(self,url, headers):
        response = requests.get(url=url, headers = headers)
        res = response.json()
        return res

    #获取第二页以后内容
    def get_html_new(self,url,html, headers):
        since_id = self.get_since_id(html)
        if since_id == None:       #部分用户最后一页since_id为0
            return None
        else:
            url = url+"&since_id="+str(since_id)
            print(url)
            response = requests.get(url=url, headers = headers)
            if response.json() == []:
                return None
            else:
                res = response.json()
                return res

    # 获得粉丝数量
    def get_fans_num(self,userId, headers):
        url = "https://m.weibo.cn/profile/info?uid=" + userId
        html = self.get_html(url, headers= headers)
        fansNum = html["data"]["user"]["followers_count"]
        print(fansNum)
        return fansNum

    #解析数据
    def parse_html(self,i, html):
        fansList = []
        if html["data"]["cards"] == []:
            return None
        else:
            cards = html["data"]["cards"][-1]["card_group"]
            #print(cards)
            for card in cards:
                fansInfo = []
                #print(card)
                #fansNum = int(card.get('desc2').split('：')[1])
                #print(fansNum)
                fansId = card.get('user')["id"]
                #print(fansId)
                fInfo = GetInfo(self.headers, str(fansId)).get_infos()
                fansInfo.extend(fInfo)
                #print(fansName)
                #print(fansInfo)
                fansList.append(fansInfo)
            print(fansList)
            print("第%d页用户爬取完毕" %(i+2))
            return fansList


    #获取新页面since_id
    def get_since_id(self,html):
        cardlistInfo = html["data"]["cardlistInfo"]
        0
        if  "since_id" in cardlistInfo:
            since_id = cardlistInfo["since_id"]
            #print(since_id)
            return since_id
        else:
            return None


    #存为csv文件
    def data_write_csv(self,savepath, datalist):
        csvFile = open(savepath, 'w', encoding='utf-8-sig', newline='')
        name = [ '粉丝id', '粉丝昵称','性别', '地区', '生日', '简介', '认证', '学习经历', '微博数量', '关注数', '粉丝数']
        try:
            writer =  csv.writer(csvFile)
            writer.writerow(name)
            for i in datalist:
                writer.writerow(i)
        finally:
            csvFile.close()

    # 存入mysql数据库
    def data_save_mysql(self,datalist, userId):
        self.init_db(userId)
        conn = pymysql.connect(**self.mysql_config)
        cursor = conn.cursor()
        for data in datalist:
            try:
                sql = "INSERT INTO singlefaninfo_%s (fansId,fansName,sex,area,birth,intro,Certification,learningExp,weiboNum,followNum,fansNum) VALUES (%s,'%s','%s','%s','%s','%s','%s','%s',%d,%d,%d);"%(userId,data[0], data[1],data[2], data[3],data[4],data[5],data[6],data[7],int(data[8]),int(data[9]),int(data[10]))
                cursor.execute(sql)
                conn.commit()
            except Exception as e:
                print(str(e))
                conn.rollback()
        cursor.close()
        conn.close()
        print("存入数据库成功")


    # 创建新表
    def init_db(self,userId):
        conn = pymysql.connect(**self.mysql_config)
        cursor = conn.cursor()
        sql = """
        CREATE TABLE singlefaninfo_%s (
        fansId CHAR(10) NOT NULL primary key ,
        fansName CHAR(50) NOT NULL,
        sex char(2),
        area char(20),
        birth char(20),
        intro char(255),
        Certification char(100),
        learningExp char(255),
        weiboNum int ,
        followNum int,
        fansNum int
        )ENGINE=innodb DEFAULT CHARSET=utf8;
        """%userId
        cursor.execute(sql)
        sql2 = """
        alter table singlefaninfo_%s convert to character set utf8mb4 collate utf8mb4_bin; 
        """%userId
        cursor.execute(sql2)
        cursor.close()
        conn.close()




