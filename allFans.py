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
import traceback
import json


class AllFans:

    def __init__(self,headers,userId,fanNum,fanLevel, mysql_config):
        self.headers = headers
        self.userId = userId
        self.fanNum = fanNum #把fanNum设为数字,（0表示爬取全部粉丝）
        self.fanLevel = fanLevel   #set fanLevel in (1,2,3)
        self.mysql_config = mysql_config

    def get_allfans(self):
        try:
            (fansList, fansList2) = self.get_fanlist(self.userId, self.headers, self.fanNum, self.fanLevel)
            if self.fanNum == 0:
                self.create_networkx_allfans(self.userId,fansList2, self.fanLevel)
            else:
                self.create_networkx(self.userId,fansList2, self.fanNum, self.fanLevel)
            savepath = ".\\"+ self.userId +"的"+str(self.fanLevel+1) + "层"+ str(self.fanNum)+"位粉丝数据.csv"

            self.data_save_mysql(fansList, self.userId, self.fanLevel+1)
            self.data_write_csv(savepath, fansList)
        except Exception as e:
            print(e)
            info = traceback.format_exc()
            print(info)

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
            print("爬取上一层用户个数\n", length)
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
                    try:
                        fans = fansList2[i][j][k]
                        fanall = self.get_all_fans(fans[1], headers)
                        if fanall == "error":
                            pass
                        else:
                            fansp.append(fanall)
                            fansl.extend(fanall)
                        print(fanall)
                        print("第%d位粉丝数据爬取完毕\n" % (k + 1))
                    except Exception as e:
                        print(e)
                        info = traceback.format_exc()
                        print(info)
                    continue
            fansList.extend(fansl)
            fansList2.append(fansp)
            time.sleep(random.randint(4, 6))
            print("第%d轮爬取完毕\n\n" % (i + 2))
        print(fansList)
        print(fansList2)
        #create_networkx(fansList2)
        return fansList,fansList2



    #获取每位用户的全部粉丝
    def get_all_fans(self,userId, headers):

        url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_" + userId
        print(url)
        fansNum = self.get_fans_num(userId, headers)
        if fansNum == "error":
            return "error"
        else:
            html = []
            html.append(self.get_html(url, headers))
            # if fansNum >40:
            #     page = 2
            # else:
            if fansNum % 20 == 0:
                page = fansNum // 20
            else:
                page = fansNum // 20 + 1  # 获取页面数
            print(userId, "粉丝页数" ,page)
            fansList = []
            firstfan = self.parse_html(userId,html[0])
            if firstfan == "error":
                print("获取页面失败")
                return "error"
            else:
                fansList.extend(firstfan)  # 增加第一页粉丝数据
                if page > 1:
                    for i in range(0, page):
                        try:
                            newhtml = self.get_html_new(url, html[i], headers)
                            if newhtml == "error":  # 判断是否最后一页（通过since_id)判断
                                break
                            else:
                                html.append(newhtml)
                                nexthtml = self.parse_html(userId,html[i + 1])
                                if nexthtml  == "error":  # 判断是否最后一页，通过最后一页是否有数据判断
                                    break
                                else:
                                    fansList.extend(nexthtml)
                        except Exception as e:
                            print(e)
                            info = traceback.format_exc()
                            print(info)
                        i = i + 1
                        time.sleep(random.randint(4, 6))
                        continue
                #print(fansList)

                return fansList

    #获取第一页内容
    def get_html(self,url, headers):
        try:
            response = requests.get(url=url, headers = headers)
            #print(type(response))
            #print(response.text)
            #print(response)
            res = response.json()
            return res
        except Exception as e:
            print(e)
            info = traceback.format_exc()
            print(info)
            return "error"


    #获取第二页以后内容
    def get_html_new(self,url,html, headers):
        try:
            if self.get_since_id(html) == None:       #部分用户最后一页since_id为0
                return "error"
            else:
                url = url+"&since_id="+str(self.get_since_id(html))
                #print(url)
                response = requests.get(url=url, headers = headers)
                if response.json() == []:
                    return "error"
                else:
                    res = response.json()
                    return res
        except Exception as e:
            print(e)
            info = traceback.format_exc()
            print(info)
            return "error"

    # 获得粉丝数量
    def get_fans_num(self,userId, headers):
        try:
            url = "https://m.weibo.cn/profile/info?uid=" + userId
            html = self.get_html(url, headers= headers)
            fansNum = html["data"]["user"]["followers_count"]
            print(userId, "粉丝数量：", fansNum)
            return fansNum
        except Exception as e:
            print(e)
            info = traceback.format_exc()
            print(info)
            return "error"

    #解析数据
    def parse_html(self,userId, html):
        try:
            fansList = []
            if html["data"]["cards"] == []:
                return "error"
            else:
                cards = html["data"]["cards"][-1]["card_group"]
                #print(cards)
                for card in cards:
                    try:
                        fansInfo = []
                        if card.get('user')["followers_count"] == None:
                            return "error"
                        else:
                            followersNum = card.get('user')["followers_count"]
                            #print("follower_count",followersNum)
                            if followersNum < 10000 or followersNum > 100000:
                                pass
                            else:
                                fansInfo.append(userId)
                                if card.get('user')["id"] == None:
                                    return "error"
                                    break
                                else:
                                    fansInfo.append(str(card.get('user')["id"]))
                                    fansName = card.get('user')["screen_name"]
                                    fansInfo.append(fansName)
                                    fansList.append(fansInfo)
                    except Exception as e:
                        print(e)
                        info = traceback.format_exc()
                        print(info)
                    continue
                    #print(fansList)
               # print(userId, "第%d页粉丝爬取完毕" %(i+2))
                return fansList
        except Exception as e:
            print(e)
            info = traceback.format_exc()
            print(info)
            return "error"


    #获取新页面since_id
    def get_since_id(self,html):
        try:
            cardlistInfo = html["data"]["cardlistInfo"]
            #print(cardlistInfo)
            if  "since_id" in cardlistInfo:
                since_id = cardlistInfo["since_id"]
                #print(since_id)
                return since_id
            else:
                return None
        except Exception as e:
            print(e)
            info = traceback.format_exc()
            print(info)


    #存为csv文件
    def data_write_csv(self,savepath, datalist):
        csvFile = open(savepath, 'w', encoding='utf-8-sig', newline='')
        name = ['用户id', '粉丝id', '粉丝昵称']
        try:
            writer =  csv.writer(csvFile)
            writer.writerow(name)
            for i in datalist:
                writer.writerow(i)
            print("存为csv文件成功")
        except Exception as e:
            print(e)
            print("存为csv文件失败")
            info = traceback.format_exc()
            print(info)
        finally:
            csvFile.close()

    # 存入mysql数据库
    def data_save_mysql(self,datalist, userId, fanLevel):
        self.init_db(userId, fanLevel)
        conn = pymysql.connect(**self.mysql_config)
        cursor = conn.cursor()
        for data in datalist:
            try:
                sql = "INSERT INTO fans_%s_round%d (userId,fansId,fansName) VALUES (%s,%s,'%s');"%(userId, fanLevel, data[0], data[1], data[2])
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
        CREATE TABLE fans_%s_round%d (
        id INT auto_increment PRIMARY KEY ,
        userId CHAR(10) NOT NULL,
        fansId CHAR(10) NOT NULL,
        fansName CHAR(50) NOT NULL
        )ENGINE=innodb DEFAULT CHARSET=utf8;
        """%(userId, fanLevel)
        cursor.execute(sql)
        cursor.close()
        conn.close()


    def create_networkx_allfans(self,userId, dataList, fanLevel):
        G = nx.DiGraph()
        G.add_node(userId)
        n = -1
        m = -1
        for i in range(0,len(dataList[0][0])):
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
                        try:
                            print("第三轮", dataList[2][n][k])
                            G.add_edge(dataList[1][i][j][1], dataList[2][n][k][1])
                            if fanLevel < 3:
                                continue
                            else:
                                m = m + 1
                                for l in range(0, len(dataList[3][m])):
                                    print("第四轮", dataList[3][m][l])
                                    G.add_edge(dataList[2][n][k][1], dataList[3][m][l][1])
                        except Exception as e:
                            print(e)
                            info = traceback.format_exc()
                            print(info)
                        continue
        nx.draw_networkx(G)
        net_pic_savepath = userId + "的" + str(fanLevel + 1) + "层" + "全部粉丝社交网络图.png"
        plt.savefig(net_pic_savepath)
        net_gexf_savepath = userId + "的" + str(fanLevel + 1) + "层" + "粉丝社交网络图.gexf"
        nx.write_gexf(G, net_gexf_savepath)
        plt.show()


    def create_networkx(self,userId,dataList, fanNum, fanLevel):
        G = nx.DiGraph()
        G.add_node(userId)
        # n = -1
        # m = -1
        # if len(dataList[0][0]) < fanNum:
        #     length1 = len(dataList[0][0])
        # else:
        #     length1 = fanNum
        # for i in range(0, length1):
        #     print("第一轮", dataList[0][0][i])
        #     G.add_edge(userId, dataList[0][0][i][1])
        #     if len(dataList[1][i]) < fanNum:
        #         length2 = len(dataList[1][i])
        #     else:
        #         length2 = fanNum
        #     for j in range(0, length2):
        #         print("第二轮", dataList[1][i][j])
        #
        #         G.add_edge(dataList[0][0][i][1], dataList[1][i][j][1])
        #         if fanLevel < 2:
        #             continue
        #         else:
        #             n = n + 1
        #             print("第二轮第%d位粉丝：\n" % (n+1))
        #             print(len(dataList[2][n]))
        #             if len(dataList[2][n]) < fanNum:
        #                 length3 = len(dataList[2][n])
        #             else:
        #                 length3 = fanNum
        #             for k in range(0, length3):
        #                 try:
        #                     print("第三轮", dataList[2][n][k])
        #                     G.add_edge(dataList[1][i][j][1], dataList[2][n][k][1])
        #                     if fanLevel < 3:
        #                         continue
        #                     else:
        #                         m = m + 1
        #                         print("第三轮第%d位粉丝：\n" % (m+1))
        #                         print(len(dataList[3][m]))
        #                         if len(dataList[3][m]) < fanNum:
        #                             length4 = len(dataList[3][m])
        #                         else:
        #                             length4 = fanNum
        #                         for l in range(0, length4):
        #                             print("第四轮", dataList[3][m][l])
        #                             G.add_edge(dataList[2][n][k][1], dataList[3][m][l][1])
        #                 except Exception as e:
        #                     print(e)
        #                     info = traceback.format_exc()
        #                     print(info)
        #                 continue


        for data in dataList[0][0]:
            print("第一轮：", data)
            G.add_edge(userId, data[1])
        for data in dataList[1]:
            G.add_node(data[0][0])
            for data2 in data:
                print("第二轮：", data2)
                G.add_edge(data2[0][0], data2[1])
        if fanLevel < 2:
            pass
        else:
            for data in dataList[2]:
                G.add_node(data[0][0])
                for data2 in data:
                    print("第三轮：", data2)
                    G.add_edge(data2[0][0], data2[1])
            if fanLevel < 3:
                pass
            else:
                for data in dataList[3]:
                    G.add_node(data[0][0])
                    for data2 in data:
                        print("第四轮：", data2)
                        G.add_edge(data2[0][0], data2[1])
        nx.draw_networkx(G)
        net_pic_savepath = userId +"的"+str(fanLevel+1) + "层"+ str(fanNum) + "位" +"粉丝社交网络图.png"
        net_gexf_savepath = userId + "的" + str(fanLevel + 1) + "层" + str(fanNum) + "位" + "粉丝社交网络图.gexf"
        nx.write_gexf(G, net_gexf_savepath)
        plt.savefig(net_pic_savepath)
        plt.show()


