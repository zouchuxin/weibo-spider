#-*- coding = utf-8 -*-
#@Time : 2020/12/26 19:11
#@Author : zou chuxin
#@File: othersInfo.py
#@Software: PyCharm

import re
import urllib
import urllib.request
import csv
import random
import pymysql

class GetInfos:
    def __init__(self,headers,userId,filename,mysql_config):
        self.headers = headers
        self.userId = userId
        self.filename = filename
        self.mysql_config = mysql_config

    def get_infos(self):   #修改读取文件，可以放入关注列表和粉丝列表
        othersIds = self.getUserId(self.filename)
        othersInfoLists = []
        for othersId in othersIds:
            url1 = "https://weibo.cn/" + othersId
            url2 = "https://weibo.cn/" + othersId + "/info"
            datalist = [othersId]
            datalist.extend(self.getData2(url2))
            datalist.extend(self.getData1(url1))
            print(datalist)
            othersInfoLists.append(datalist)
        savepath = ".\\"+ self.userId + "2层2位粉丝信息.csv"

        self.data_write_csv(savepath, othersInfoLists)
        self.data_save_mysql(othersInfoLists, self.userId)

    #获取页面源码
    def askUrl(self,url):
        request = urllib.request.Request(url, headers = self.headers)
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        #print(html)
        return html

    #获取用户id
    def getUserId(self,filename):
        with open(filename,'r', encoding='UTF-8') as csvfile:
            reader = csv.reader(csvfile)
            column1 = [row[1] for row in reader]
            del column1[0]
        return column1




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


    # 将信息存入csv文件
    def data_write_csv(self,savepath, datalists):
        csvFile = open(savepath,'w', encoding='utf-8-sig', newline='')
        name = ['用户id', '昵称', '性别', '地区', '生日', '简介', '认证', '学习经历', '微博数量', '关注数', '粉丝数']
        try:
            writer =  csv.writer(csvFile)
            writer.writerow(name)
            for datalist in datalists:
                writer.writerow(datalist)
        finally:
            csvFile.close()

    # 存入mysql数据库
    def data_save_mysql(self,datalist, userId):
        self.init_db(userId)
        conn = pymysql.connect(**self.mysql_config)
        cursor = conn.cursor()
        for data in datalist:
            try:
                sql = "INSERT INTO Infos_%s (userId,userName,sex,area,birth,intro,Certification,learningExp,weiboNum,followNum,fansNum) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s',%d,%d,%d);"%(userId, data[0], data[1],data[2], data[3],data[4],data[5],data[6],data[7],int(data[8]),int(data[9]),int(data[10]))
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
        CREATE TABLE Infos_%s (
        InfoId INT auto_increment PRIMARY KEY ,
        userId char(20),
        userName char(20),
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
               alter table Infos_%s convert to character set utf8mb4 collate utf8mb4_bin; 
               """ % userId
        cursor.execute(sql2)
        cursor.close()
        conn.close()
