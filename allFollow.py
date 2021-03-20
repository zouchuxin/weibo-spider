#-*- coding = utf-8 -*-
#@Time : 2021/1/30 11:03
#@Author : zou chuxin
#@File: allfollow.py
#@Software: PyCharm

from matplotlib import pyplot as plt
import networkx as nx
import requests
import csv
import time
import random
import pymysql
import traceback

class AllFollow:
    def __init__(self,headers,userId,followNum,followLevel,mysql_config):
        self.headers = headers
        self.userId = userId

        self.follownum = followNum  # 把fanNum设为数字,（0表示爬取全部粉丝）
        self.followLevel = followLevel  # set fanLevel in (1,2,3)
        self.mysql_config = mysql_config

    def get_allfollow(self):
        try:
            (followList, followList2) = self.get_followlist(self.userId, self.headers, self.follownum, self.followLevel)
            if self.follownum == 0:
                self.create_networkx_allfollow(self.userId,followList2, self.followLevel)
            else:
                self.create_networkx(self.userId,followList2, self.follownum, self.followLevel)
            savepath = ".\\"+ self.userId +"的"+str(self.followLevel+1) + "层"+ str(self.follownum)+"位关注数据.csv"

            self.data_save_mysql(followList, self.userId, self.followLevel+1)
            self.data_write_csv(savepath, followList)
        except Exception as e:
            print(e)
            info = traceback.format_exc()
            print(info)

    #获取最终关注列表
    def get_followlist(self,userId, headers, followNum, followLevel):
        followall = self.get_all_follow(userId, headers)
        followList = []
        followList.extend(followall)
        firstfollow = []
        firstfollow.append(followall)
        followList2 = []
        followList2.append(firstfollow)
        print(followall)
        print("第1轮爬取完毕\n\n")
        for i in range(0, followLevel):  # 设置爬取深度
            followl = []  # 所有关注存入关系表中
            followp = []  # 每一层设置一个列表
            length = len(followList2[i])
            print("要爬取上一层用户个数\n", length)
            for j in range(0, length):
                length2 = len(followList2[i][j])
                print("用户关注个数", length2)
                if followNum == 0:
                    follownum = length2
                else:
                    if length2 < followNum:
                        follownum = length2
                    else:
                        follownum = followNum
                for k in range(0, follownum):  # 设置爬取关注个数,方便测试，即只爬取某一用户的follownum个关注
                    try:
                        follow = followList2[i][j][k]
                        allfollow = self.get_all_follow(follow[1], headers)
                        if allfollow == "error":
                            pass
                        else:
                            followp.append(allfollow)
                            followl.extend(allfollow)
                        print(allfollow)
                        print("第%d位关注数据爬取完毕\n" % (k + 1))
                    except Exception as e:
                        print(e)
                        info = traceback.format_exc()
                        print(info)
                    continue
            followList.extend(followl)
            followList2.append(followp)
            time.sleep(random.randint(1, 3))
            print("第%d轮爬取完毕\n\n" % (i + 2))
        print(followList)
        print(followList2)
        #create_networkx(followList2)
        return followList,followList2



    #获取每位用户的全部关注
    def get_all_follow(self,userId, headers):
        url = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_" + userId
        print(url)
        followNum = self.get_follow_num(userId, headers)
        if followNum == "error":
            return "error"
        else:

            html = []
            html.append(self.get_html(url, headers))
            if followNum == 80:
                page = 4
            else:
                if followNum % 20 == 0:
                    page = followNum // 20
                else:
                    page = followNum // 20 + 1  # 获取页面数
            print(userId, "关注页数" ,page)
            followList = []
            firstfollow = self.parse_html(userId,html[0])
            if firstfollow == "error":
                print("获取页面失败")
                return "error"
            else:
                followList.extend(firstfollow)  # 增加第一页关注数据
                if page > 1 :
                    for i in range(2, page):
                        try:
                            newhtml = self.get_html_new(url, i, headers)
                            if newhtml  == "error":
                                break
                            else:
                                html.append(newhtml)
                                html_info = self.parse_html(userId, html[i - 1])  # 判断是否最后一页，通过最后一页是否有数据判断
                                if html_info == "error":
                                    break
                                else:
                                    followList.extend(html_info)
                        except Exception as e:
                            print(e)
                            info = traceback.format_exc()
                            print(info)
                        i = i + 1
                        time.sleep(random.randint(1, 3))
                        continue
                #print(followList)
                return followList


    #获取第一页内容
    def get_html(self,url, headers):
        try:
            response = requests.get(url=url, headers = headers)
            res = response.json()
            return res
        except Exception as e:
            print(e)
            info = traceback.format_exc()
            print(info)
            return "error"

    #获取第二页以后内容
    def get_html_new(self,url,i, headers):
        try:
            url = url + "&page=" + str(i)
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

    # 获得关注数量
    def get_follow_num(self,userId, headers):
        try:
            url = "https://m.weibo.cn/profile/info?uid=" + userId
            html = self.get_html(url, headers= headers)
            followNum = html["data"]["user"]["follow_count"]
            print(userId, "关注数量：", followNum)
            return followNum
        except Exception as e:
            print(e)
            info = traceback.format_exc()
            print(info)
            return "error"

    #解析数据
    def parse_html(self,userId,  html):
        try:
            followList = []
            if html["data"]["cards"] == []:
                return "error"
            else:
                cards = html["data"]["cards"][-1]["card_group"]
                #print(cards)
                for card in cards:
                    try:
                        followInfo = []
                        followInfo.append(userId)
                        #print(card)
                        #followNum = int(card.get('desc2').split('：')[1])
                        #print(followNum)
                        followId = card.get('user')["id"]
                        if followId == None:
                            return None
                            break
                        else:
                            followInfo.append(str(followId))
                            followName = card.get('user')["screen_name"]
                            followInfo.append(followName)
                            followList.append(followInfo)
                    except Exception as e:
                        print(e)
                        info = traceback.format_exc()
                        print(info)
                    continue
                    #print(followList)
                #print("第%d页关注页面爬取完毕" %(i))
                return followList
        except Exception as e:
            print(e)
            info = traceback.format_exc()
            print(info)
            return "error"



    #存为csv文件
    def data_write_csv(self,savepath, datalist):
        csvFile = open(savepath, 'w', encoding='utf-8-sig', newline='')
        name = ['用户id', '关注id', '关注昵称']
        try:
            writer =  csv.writer(csvFile)
            writer.writerow(name)
            for i in datalist:
                writer.writerow(i)
        except Exception as e:
            print(e)
            info = traceback.format_exc()
            print(info)
        finally:
            csvFile.close()

    # 存入mysql数据库
    def data_save_mysql(self,datalist, userId, followLevel):
        self.init_db(userId, followLevel)
        conn = pymysql.connect(**self.mysql_config)
        cursor = conn.cursor()
        for data in datalist:
            try:
                sql = "INSERT INTO follow_%s_round%d (userId,followId,followName) VALUES (%s,%s,'%s');"%(userId, followLevel, data[0], data[1], data[2])
                cursor.execute(sql)
                conn.commit()
            except Exception as e:
                print(str(e))
                conn.rollback()
        cursor.close()
        conn.close()
        print("存入数据库成功")


    # 创建新表
    def init_db(self,userId, followLevel):
        conn = pymysql.connect(**self.mysql_config)
        cursor = conn.cursor()
        sql = """
        CREATE TABLE follow_%s_round%d (
        id INT auto_increment PRIMARY KEY ,
        userId CHAR(10) NOT NULL,
        followId CHAR(10) NOT NULL,
        followName CHAR(50) NOT NULL
        )ENGINE=innodb DEFAULT CHARSET=utf8;
        """%(userId, followLevel)
        cursor.execute(sql)
        cursor.close()
        conn.close()


    def create_networkx_allfollow(self,userId,dataList, followLevel):
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
                if followLevel < 2:
                    continue
                else:
                    n = n + 1
                    print(n, "\n")
                    for k in range(0, len(dataList[2][n])):
                        try:
                            print("第三轮", dataList[2][n][k])
                            G.add_edge(dataList[1][i][j][1], dataList[2][n][k][1])
                            if followLevel < 3:
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
        net_pic_savepath = userId + "的" + str(followLevel + 1) + "层" + "全部关注社交网络图.png"
        plt.savefig(net_pic_savepath)
        plt.show()


    def create_networkx(self,userId,dataList, followNum, followLevel):
        G = nx.DiGraph()
        G.add_node(userId)
        n = -1
        m = -1
        if len(dataList[0][0]) < followNum:
            length1 = len(dataList[0][0])
        else:
            length1 = followNum
        for i in range(0, length1):
            print("第一轮", dataList[0][0][i])
            G.add_edge(userId, dataList[0][0][i][1])
            if len(dataList[1][i]) < followNum:
                length2 = len(dataList[1][i])
            else:
                length2 = followNum
            for j in range(0, length2):
                print("第二轮", dataList[1][i][j])
                G.add_edge(dataList[0][0][i][1], dataList[1][i][j][1])
                if followLevel < 2:
                    continue
                else:
                    n = n + 1
                    print("第二轮第%d位关注：\n" % (n+1))
                    if len(dataList[2][n]) < followNum:
                        length3 = len(dataList[2][n])
                    else:
                        length3 = followNum
                    for k in range(0, length3):
                        try:
                            print("第三轮", dataList[2][n][k])
                            G.add_edge(dataList[1][i][j][1], dataList[2][n][k][1])
                            if followLevel < 3:
                                continue
                            else:
                                m = m + 1
                                print("第三轮第%d位关注：\n" % (m+1))
                                if len(dataList[3][m]) < followNum:
                                    length4 = len(dataList[3][m])
                                else:
                                    length4 = followNum
                                for l in range(0, length4):
                                    print("第四轮", dataList[3][m][l])
                                    G.add_edge(dataList[2][n][k][1], dataList[3][m][l][1])
                        except Exception as e:
                            print(e)
                            info = traceback.format_exc()
                            print(info)
                        continue
        nx.draw_networkx(G)
        net_pic_savepath = userId + "的" + str(followLevel + 1) + "层" + str(followNum) + "位" + "关注社交网络图.png"
        plt.savefig(net_pic_savepath)
        plt.show()


