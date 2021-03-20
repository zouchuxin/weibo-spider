#-*- coding = utf-8 -*-
#@Time : 2021/1/21 9:29
#@Author : zou chuxin
#@File: allfans.py
#@Software: PyCharm

from matplotlib import pyplot as plt
import networkx as nx
import requests
import csv
import time
import random
import pymysql
from weibo_spide_2021.getInfo import GetInfo



class AllFansInfo:

    def __init__(self,headers,userId,fanNum,fanLevel,mysql_config):
        self.headers = headers
        self.userId = userId
        self.fanNum = fanNum #把fanNum设为数字,（0表示爬取全部粉丝）
        self.fanLevel = fanLevel   #set fanLevel in (1,2,3)
        self.mysql_config  = mysql_config

    def get_allfansinfo(self):
        (fansList, fansList2) = self.get_fanlist(self.userId, self.headers, self.fanNum, self.fanLevel)
        if self.fanNum == 0:
            self.create_networkx_allfans(self.userId,fansList2, self.fanLevel)
        else:
            self.create_networkx(self.userId,fansList2, self.fanNum, self.fanLevel)
        savepath = ".\\"+ self.userId +"的"+str(self.fanLevel+1) + "层"+ str(self.fanNum)+"位粉丝信息.csv"

        self.data_save_mysql(fansList, self.userId, self.fanLevel+1)
        self.data_write_csv(savepath, fansList)

    #获取最终粉丝列表
    def get_fanlist(self,userId, headers, fanNum, fanLevel):
        fansall = self.get_all_fans(userId, headers)
        fansList = []
        fansList.extend(fansall)
        firstfan = []
        firstfan.append(fansall)
        fansList2 = []
        fansList2.append(firstfan)
        print(fansall)
        print("第1轮爬取完毕\n\n")
        for i in range(0, fanLevel):  # 设置爬取深度
            fansl = []  # 所有粉丝存入关系表中
            fansp = []  # 每一层设置一个列表
            length = len(fansList2[i])
            print("上一层用户个数", length)
            for j in range(0, length):
                length2 = len(fansList2[i][j])
                print("用户粉丝个数", length2)
                if fanNum == 0:
                    fannum = length2
                else:
                    if length2 < fanNum:
                        fannum = length2
                    else:
                        fannum = fanNum
                for k in range(0, fannum):  # 设置爬取粉丝个数,方便测试，即只爬取某一用户的fannum个粉丝
                    fans = fansList2[i][j][k]
                    allfans = self.get_all_fans(fans[1], headers)
                    fansp.append(allfans)
                    fansl.extend(allfans)
                    print(allfans)
                    print("第%d位粉丝数据爬取完毕\n" % (k + 1))
            fansList.extend(fansl)
            fansList2.append(fansp)
            time.sleep(random.randint(1, 3))
            print("第%d轮爬取完毕\n\n" % (i + 2))
        print(fansList)
        print(fansList2)
        #create_networkx(fansList2)
        return fansList,fansList2


    #获取每位用户的全部粉丝
    def get_all_fans(self,userId, headers):
        url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_" + userId
        fansNum = self.get_fans_num(userId, headers)
        html = []
        html.append(self.get_html(url, headers))
        if fansNum % 20 == 0:
            page = fansNum // 20
        else:
            page = fansNum // 20 + 1  # 获取页面数
        print(userId, "粉丝页数" ,page)
        fansList = []
        fansList.extend(self.parse_html(userId,html[0]))  # 增加第一页粉丝数据
        if page > 1:
            for i in range(0, page):
                new_html = self.get_html_new(url, html[i], headers)  # 判断是否最后一页（通过since_id)判断
                if new_html == None:
                    break
                else:
                    html.append(new_html)
                    html_info = self.parse_html(userId,html[i + 1])  # 判断是否最后一页，通过最后一页是否有数据判断
                    if html_info == None:
                        break
                    else:
                        fansList.extend(html_info)
                i = i + 1
                time.sleep(random.randint(1, 3))
        #print(fansList)
        print(userId, "粉丝爬取完毕")
        return fansList

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
            #print(url)
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
        print(userId, "粉丝数量：", fansNum)
        return fansNum

    #解析数据
    def parse_html(self,userId, html):
        fansList = []
        if html["data"]["cards"] == []:
            return None
        else:
            cards = html["data"]["cards"][-1]["card_group"]
            #print(cards)
            for card in cards:
                fansInfo = []
                fansInfo.append(userId)
                fansId = card.get('user')["id"]
                if fansId == None:
                    return None
                    break
                else:
                    fInfo = GetInfo(self.headers, str(fansId)).get_infos()
                    fansInfo.extend(fInfo)
                    fansList.append(fansInfo)
                #print(fansList)
           # print(userId, "第%d页粉丝爬取完毕" %(i+2))
            return fansList


    #获取新页面since_id
    def get_since_id(self,html):
        cardlistInfo = html["data"]["cardlistInfo"]
        #print(cardlistInfo)
        if  "since_id" in cardlistInfo:
            since_id = cardlistInfo["since_id"]
            #print(since_id)
            return since_id
        else:
            return None


    #存为csv文件
    def data_write_csv(self,savepath, datalist):
        csvFile = open(savepath, 'w', encoding='utf-8-sig', newline='')
        name = ['用户id', '粉丝id', '粉丝昵称','性别', '地区', '生日', '简介', '认证', '学习经历', '微博数量', '关注数', '粉丝数']
        try:
            writer =  csv.writer(csvFile)
            writer.writerow(name)
            for i in datalist:
                writer.writerow(i)
        finally:
            csvFile.close()

    # 存入mysql数据库
    def data_save_mysql(self,datalist, userId, fanLevel):
        self.init_db(userId, fanLevel)
        conn = pymysql.connect(**self.mysql_config)
        cursor = conn.cursor()
        for data in datalist:
            try:
                sql = "INSERT INTO fansinfo_%s_round%d (userId,fansId,fansName,sex,area,birth,intro,Certification,learningExp,weiboNum,followNum,fansNum) VALUES (%s,%s,'%s','%s','%s','%s','%s','%s','%s',%d,%d,%d);"%(userId, fanLevel, data[0], data[1], data[2], data[3],data[4],data[5],data[6],data[7],data[8],int(data[9]),int(data[10]),int(data[11]))
                cursor.execute(sql)
                conn.commit()
            except Exception as e:
                print(str(e))
                conn.rollback()
        cursor.close()
        conn.close()
        print("存入数据库成功")


    # 创建新表
    def init_db(self,userId, fanLevel):
        conn = pymysql.connect(**self.mysql_config)
        cursor = conn.cursor()

        sql = """
        CREATE TABLE fansinfo_%s_round%d (
        id INT auto_increment PRIMARY KEY ,
        userId CHAR(10) NOT NULL,
        fansId CHAR(10) NOT NULL,
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
        """%(userId, fanLevel)
        cursor.execute(sql)
        sql2 = """
        alter table fansinfo_%s_round%d convert to character set utf8mb4 collate utf8mb4_bin; 
        """ %(userId, fanLevel)
        cursor.execute(sql2)
        cursor.close()
        conn.close()


    def create_networkx_allfans(self,userId, dataList, fanLevel):
        G = nx.DiGraph()
        G.add_node(userId)
        n = -1
        m = -1
        for i in range(0, len(dataList[0][0])):
            print("第一轮", dataList[0][0][i])
            G.add_edge(userId, dataList[0][0][i][1])
            for j in range(0, len(dataList[1][i])):
                print("第二轮", dataList[1][i][j])
                G.add_edge(dataList[0][0][i][1], dataList[1][i][j][1])
                if fanLevel < 2:
                    continue
                else:
                    n = n + 1
                    print(n, "\n")
                    for k in range(0, len(dataList[2][n])):
                        print("第三轮", dataList[2][n][k])
                        G.add_edge(dataList[1][i][j][1], dataList[2][n][k][1])
                        if fanLevel < 3:
                            continue
                        else:
                            m = m + 1
                            for l in range(0, len(dataList[3][m])):
                                print("第四轮", dataList[3][m][l])
                                G.add_edge(dataList[2][n][k][1], dataList[3][m][l][1])
        nx.draw_networkx(G)
        net_pic_savepath = userId + "的" + str(fanLevel + 1) + "层" + "全部粉丝社交网络图.png"
        plt.savefig(net_pic_savepath)
        plt.show()


    def create_networkx(self,userId,dataList, fanNum, fanLevel):
        G = nx.DiGraph()
        G.add_node(userId)
        n = -1
        m = -1
        if len(dataList[0][0]) < fanNum:
            length1 = len(dataList[0][0])
        else:
            length1 = fanNum
        for i in range(0, length1):
            print("第一轮", dataList[0][0][i])
            G.add_edge(userId, dataList[0][0][i][1])
            if len(dataList[1][i]) < fanNum:
                length2 = len(dataList[1][i])
            else:
                length2 = fanNum
            for j in range(0, length2):
                print("第二轮", dataList[1][i][j])
                G.add_edge(dataList[0][0][i][1], dataList[1][i][j][1])
                if fanLevel < 2:
                    continue
                else:
                    n = n + 1
                    print("第二轮第%d位粉丝：\n" % (n+1))
                    if len(dataList[2][n]) < fanNum:
                        length3 = len(dataList[2][n])
                    else:
                        length3 = fanNum
                    for k in range(0, length3):
                        print("第三轮", dataList[2][n][k])
                        G.add_edge(dataList[1][i][j][1], dataList[2][n][k][1])
                        if fanLevel < 3:
                            continue
                        else:
                            m = m + 1
                            print("第三轮第%d位粉丝：\n" % (m+1))
                            if len(dataList[3][m]) < fanNum:
                                length4 = len(dataList[3][m])
                            else:
                                length4 = fanNum
                            for l in range(0, length4):
                                print("第四轮", dataList[3][m][l])
                                G.add_edge(dataList[2][n][k][1], dataList[3][m][l][1])
        nx.draw_networkx(G)
        net_pic_savepath = userId +"的"+str(fanLevel+1) + "层"+ str(fanNum) + "位" +"粉丝社交网络图.png"
        plt.savefig(net_pic_savepath)
        plt.show()


