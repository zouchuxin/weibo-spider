#-*- coding = utf-8 -*-
#@Time : 2020/12/24 15:19
#@Author : zou chuxin
#@File: comments.py
#@Software: PyCharm


import urllib.request
import chardet
import csv
import time
import pymysql
from bs4 import BeautifulSoup
import re
import urllib
import urllib.request
import random
from lxml import etree
from datetime import datetime, timedelta



class Comments:
    def __init__(self, headers, userId, filename, mysql_config):
        self.headers = headers
        self.userId = userId
        self.filename = filename
        self.mysql_config = mysql_config



    def get_all_comment(self):
        weiboInfos = self.get_comment_id(self.filename)
        commentlists = []
        for weiboInfo in weiboInfos:
            commentlist = self.get_comment(weiboInfo[0], weiboInfo[1], self.userId, self.headers)
            commentlists.extend(commentlist)
            time.sleep(random.randint(1, 3))  # 设置爬取时间间隔
        print(commentlists)
        csv_savepath = ".\\" + self.userId + "评论内容.csv"  # 修改存储csv文件名

        self.data_write_csv(csv_savepath, commentlists)
        self.data_save_mysql(commentlists, self.userId)



    def get_comment(self, weiboId, weiboContent, userId,headers):
        baseurl = "https://weibo.cn/comment/" + weiboId + "?uid=" + userId + "&rl=0"
        req = self.askUrl(baseurl, headers=headers)
        reqSoup = BeautifulSoup(req, "html.parser")
        if reqSoup.find_all('div', class_="pa") == []:
            pageNum = 1
        else:
            pattern = re.compile('<input type="submit" value="跳页" />&nbsp;1/(\d+)页</div>')
            pageNum = int(re.findall(pattern, req)[0])
        datalist = []
        for i in range(0, pageNum):
            url = baseurl + "&page=" + str(i + 1)
            print(url)
            html = self.askUrl(url, headers=headers)
            res_xpath = etree.HTML(html.encode('utf-8'))
            commentInfos = res_xpath.xpath("//div[starts-with(@id,'C_')]")
            for commentInfo in commentInfos:
                data = [baseurl, weiboContent]
                comId = commentInfo.xpath("./a[starts-with(@href,'/spam')]/@href")[0]
                commentatorId = re.findall(re.compile(r'uid=(.*?)&'), comId)[0]
                #print(commentatorId)
                data.append(commentatorId)
                comName = commentInfo.xpath("./a[1]")[0].text
                data.append(comName)
                comContent = commentInfo.xpath("./span[@class='ctt']")[0]
                commentContent = comContent.xpath('string(.)')
                #print(commentContent)
                data.append(commentContent)
                comLike = commentInfo.xpath("./span[@class='cc'][1]/a")[0].text
                if comLike == '取消赞':
                    comLike = commentInfo.xpath("./span[@class='cmt']")[0].text.strip()
                commentLike = re.findall(re.compile(r'赞\[(.*?)\]'), comLike)[0]
                #print(commentLike)
                data.append(commentLike)
                str_time = commentInfo.xpath("./span[@class='ct']")[0].text
                #print(str_time)
                commentTime = str_time.split(u'来自')[0]
                if u'刚刚' in commentTime:
                    commentTime = datetime.now().strftime('%Y-%m-%d %H:%M')
                elif u'分钟' in commentTime:
                    minute = commentTime[:commentTime.find(u'分钟')]
                    minute = timedelta(minutes=int(minute))
                    commentTime = (datetime.now() -
                                   minute).strftime('%Y-%m-%d %H:%M')
                elif u'今天' in commentTime:
                    today = datetime.now().strftime('%Y-%m-%d')
                    time = commentTime[3:]
                    commentTime = today + ' ' + time
                    if len(commentTime) > 16:
                        commentTime = commentTime[:16]
                elif u'月' in commentTime:
                    year = datetime.now().strftime('%Y')
                    month = commentTime[0:2]
                    day = commentTime[3:5]
                    time = commentTime[7:12]
                    commentTime = year + '-' + month + '-' + day + ' ' + time
                else:
                    commentTime = commentTime[:16]
                #print(commentTime)
                data.append(commentTime)
                datalist.append(data)
        print(datalist)
        return datalist


    #获取网页源码
    def askUrl(self, url,headers):
        request = urllib.request.Request(url, headers = headers)
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        #print(html)
        return html


    #获取微博id及微博内容
    def get_comment_id(self,filename):
        with open(filename,'r', encoding='UTF-8') as csvfile:
            reader = csv.reader(csvfile)
            column1 = [row[0] for row in reader]
            del column1[0]
        with open(filename,'r', encoding='UTF-8') as csvfile:
            reader = csv.reader(csvfile)
            column2 = [row[1] for row in reader]
            del column2[0]
        column = list(zip(column1, column2))
        #print(column)
        return column   #返回元组（微博id，微博内容）

    # 存入mysql数据库
    def data_save_mysql(self, datalist, userId):
        self.init_db(userId)
        conn = pymysql.connect(**self.mysql_config)
        cursor = conn.cursor()
        for data in datalist:
            try:
                sql = "INSERT INTO comment_%s (weiboUrl,weiboContent,commentatorId,commentatorName,comment,commentLike,commentTime) VALUES ('%s','%s','%s','%s','%s',%d,'%s');"%(userId, data[0], data[1],data[2], data[3],data[4],int(data[5]),data[6])
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
        CREATE TABLE comment_%s (
        commentId INT auto_increment PRIMARY KEY ,
        weiboUrl char(255) not null,
        weiboContent varchar(500) ,
        commentatorId char(20) ,
        commentatorName char(50),
        comment char(255),
        commentLike int,
        commentTime char(20)
        )ENGINE=innodb DEFAULT CHARSET=utf8;
        """%userId
        cursor.execute(sql)
        sql2 = """
                alter table comment_%s convert to character set utf8mb4 collate utf8mb4_bin; 
                """ % userId
        cursor.execute(sql2)

        cursor.close()
        conn.close()


    #将评论内容存为csv文件
    def data_write_csv(self, savepath, datalist):
        num = len(datalist)
        print("爬取评论数:",num)
        csvFile = open(savepath,'w', encoding='utf-8-sig', newline='')
        name = ['微博链接', '微博内容', '评论人id', '评论者昵称', '评论内容','评论点赞数','评论时间']

        try:
            writer =  csv.writer(csvFile)
            writer.writerow(name)
            for i in datalist:
                writer.writerow(i)
        finally:
            csvFile.close()

