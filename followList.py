#-*- coding = utf-8 -*-
#@Time : 2020/12/30 16:23
#@Author : zou chuxin
#@File: followList.py
#@Software: PyCharm

import requests
import csv
import time
import random
import pymysql

class FollowList:
    def __init__(self,headers,userId,mysql_config):
        self.headers = headers
        self.userId = userId
        self.mysql_config = mysql_config


    def get_followlist(self):
        url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_" + self.userId
        followNum = self.get_follow_num(self.userId, self.headers)
        html = []
        html.append(self.get_html(url, self.headers))
        savepath = ".\\" + self.userId + "关注数据.csv"

        if followNum % 20 == 0:
            page = followNum // 20
        else:
            page = followNum // 20 + 1  # 获取页面数
        print(page)
        followList = []
        followList.extend(self.parse_html(1, html[0]))  # 增加第一页关注数据
        if page > 1:
            for i in range(2, page):
                new_html = self.get_html_new(url, i, self.headers)
                if new_html == None:
                    break
                else:
                    html.append(new_html)
                    html_info = self.parse_html(i, html[i - 1])  # 判断是否最后一页，通过最后一页是否有数据判断
                    if html_info == None:
                        break
                    else:
                        followList.extend(html_info)
                i = i + 1
                time.sleep(random.randint(1, 3))
        print(followList)
        self.data_write_csv(savepath, followList)
        self.data_save_mysql(followList, self.userId)


    #获取第一页内容
    def get_html(self, url, headers):
        response = requests.get(url=url, headers = headers)
        res = response.json()
        return res

    #获取第二页以后内容
    def get_html_new(self, url,i, headers):
        url = url+"&page="+ str(i)
        response = requests.get(url=url, headers = headers)
        if response.json() == []:
            return None
        else:
            res = response.json()
            return res
    # 获得关注数量
    def get_follow_num(self, userId, headers):
        url = "https://m.weibo.cn/profile/info?uid=" + userId
        html = self.get_html(url, headers= headers)
        followNum = html["data"]["user"]["follow_count"]
        print(followNum)
        return followNum

    #解析数据
    def parse_html(self, i, html):
        followList = []
        if html["data"]["cards"] == []:
            return None
        else:
            cards = html["data"]["cards"][-1]["card_group"]
            #print(cards)
            for card in cards:
                followInfo = []
                #print(card)
                #followNum = int(card.get('desc2').split('：')[1])
                #print(followNum)
                followId = card.get('user')["id"]
                followInfo.append(followId)
                #print(followId)
                followName = card.get('user')["screen_name"]
                followInfo.append(followName)
                #print(followName)
                #print(followInfo)
                followList.append(followInfo)
            print(followList)
            print("第%d页关注页面爬取完毕" %(i))
            return followList



    #存为csv文件
    def data_write_csv(self, savepath, datalist):
        csvFile = open(savepath, 'w', encoding='utf-8-sig', newline='')
        name = [ '关注id', '关注昵称']
        try:
            writer =  csv.writer(csvFile)
            writer.writerow(name)
            for i in datalist:
                writer.writerow(i)
        finally:
            csvFile.close()


    # 存入mysql数据库
    def data_save_mysql(self,  datalist, userId):
        self.init_db(userId)
        conn = pymysql.connect(**self.mysql_config)
        cursor = conn.cursor()
        for data in datalist:
            try:
                sql = "INSERT INTO singlefollow_%s (followId,followName) VALUES (%s,'%s');"%(userId,data[0],data[1])
                cursor.execute(sql)
                conn.commit()
            except Exception as e:
                print(str(e))
                conn.rollback()
        cursor.close()
        conn.close()
        print("存入数据库成功")


    # 创建新表
    def init_db(self, userId):
        conn = pymysql.connect(**self.mysql_config)
        cursor = conn.cursor()
        sql = """
        CREATE TABLE singlefollow_%s (
        followId CHAR(10) NOT NULL primary key ,
        followName CHAR(50) NOT NULL
        )ENGINE=innodb DEFAULT CHARSET=utf8;
        """%userId
        cursor.execute(sql)
        cursor.close()
        conn.close()

