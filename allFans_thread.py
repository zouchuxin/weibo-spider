#-*- coding = utf-8 -*-
#@Time : 2021/3/18 8:23
#@Author : zou chuxin
#@File: allFans_thread.py
#@Software: PyCharm

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
from concurrent.futures import ThreadPoolExecutor,as_completed


class AllFans:

    def __init__(self,headers,userId,fanNum,fanLevel, mysql_config):
        self.headers = headers
        self.userId = userId
        self.fanNum = fanNum #把fanNum设为数字,（0表示爬取全部粉丝）
        self.fanLevel = fanLevel   #set fanLevel in (1,2,3)
        self.mysql_config = mysql_config
        self.have_crewed_user = []

    def get_allfans(self):
        try:
            (fansList, fansList2) = self.get_fanlist(self.userId,  self.fanNum, self.fanLevel)
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
    def get_fanlist(self,userId,  fanNum, fanLevel):
        fansall = self.get_all_fans(userId)
        fansList = []
        fansList.extend(fansall)
        # fansListId = []
        # fansListId.append(userId)
        fansList2 = []
        fansList2.append(fansall)
        print(fansList2)
        fansIDList = []
        # fansIDList.append()
        # print(fansall)
        print("第1轮爬取完毕\n\n")
        for i in range(0, fanLevel):  # 设置爬取深度
            fansl = []  # 所有粉丝存入关系表中
            length = len(fansList2[i])
            print("爬取上一层用户粉丝个数\n", length)

            # for fan in fansList2[i]:
            #     try:
            #         if fan[1] in fansListId:
            #             pass
            #         else:
            #             fanall = self.get_all_fans(fan[1])
            #             if fanall == "error":
            #                 pass
            #             else:
            #                 fansl.extend(fanall)
            #                 fansListId.append(fan[1])
            #                 print(fanall)
            #                 print("已爬用户:",fansListId)
            #                 print("粉丝数据爬取完毕\n")
            #     except Exception as e:
            #         print(e)
            #         info = traceback.format_exc()
            #         print(info)
            #     continue

            fans = []
            for fan in fansList2[i]:

                if fan[1] in self.have_crewed_user:
                    pass
                else:
                    fans.append(fan[1])
            with ThreadPoolExecutor(max_workers = 5) as pool:
                futures = [pool.submit(self.get_all_fans,fan) for fan in fans]
                for future in as_completed(futures):
                    try:
                        if future.result() == "error":
                            pass
                        else:
                            fansl.extend(future.result())

                            print("粉丝数据爬取完毕\n" )
                    except Exception as e:
                        print(e)
                        info = traceback.format_exc()
                        print(info)
                    continue


            fansList.extend(fansl)
            fansList2.append(fansl)
            time.sleep(random.randint(4, 6))
            print("第%d轮爬取完毕\n\n" % (i + 2))
        print(fansList)
        print(fansList2)
        #create_networkx(fansList2)
        return fansList,fansList2



    #获取每位用户的全部粉丝
    def get_all_fans(self,userId):
        print("已爬用户：", self.have_crewed_user)
        headers = self.headers
        self.have_crewed_user.append(userId)
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
                                nextfan= self.parse_html(userId,html[i + 1])
                                if nextfan  == "error":  # 判断是否最后一页，通过最后一页是否有数据判断
                                    break
                                else:
                                    fansList.extend(nextfan)
                        except Exception as e:
                            print(e)
                            info = traceback.format_exc()
                            print(info)
                        i = i + 1
                        time.sleep(random.randint(5, 8))
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
            fansListId = []
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
                            if followersNum < 50 or followersNum > 200:
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
        for data in dataList[0]:
            print("第一轮：", data)
            G.add_edge(userId, data[1])
        for data in dataList[1]:
            print("第二轮：", data)
            G.add_edge(data[0], data[1])
        if fanLevel < 2:
            pass
        else:
            for data in dataList[2]:
                print("第三轮：", data)
                G.add_edge(data[0], data[1])
            if fanLevel < 3:
                pass
            else:
                for data in dataList[3]:
                    print("第四轮：", data)
                    G.add_edge(data[0], data[1])
        nx.draw_networkx(G)
        net_pic_savepath = userId +"的"+str(fanLevel+1) + "层"+"粉丝社交网络图.png"
        net_gexf_savepath = userId + "的" + str(fanLevel + 1) + "层" +  "粉丝社交网络图.gexf"
        nx.write_gexf(G, net_gexf_savepath)
        plt.savefig(net_pic_savepath)
        plt.show()





def main():
    headers = random.choice([ {
        "cookie": "SUB=_2A25y5TpSDeRhGeBP6lYY9C3Fzz-IHXVuJkYarDV6PUJbkdANLUnykW1NRZVO-Uh7XDz1Ceqb9XkuIJHcf_BcQfkQ; _T_WM=91830411068; XSRF-TOKEN=0f9095; WEIBOCN_FROM=1110006030; MLOGIN=1; M_WEIBOCN_PARAMS=uicode%3D20000174",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
    },{
        "cookie": "SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWZ.2peNWRuScjKBxMq-znZ5NHD95QceK2X1KB01KB0Ws4DqcjyqcyfqJi4i--NiKLWiKnXi--4iK.Ri-isi--ci-8hi-20; SUB=_2A25NDUEdDeRhGeBP6lYY9C3Fzz-IHXVuDm9VrDV6PUJbkdAKLWrakW1NRZVO-Qd9ZKdH2bTsJtN0mrq-tkYwLc2J; SCF=AsZQj2NVi5vYBq2HW79Sp3si0TpLOVH9yyeeT-hwo1lzgUwjOrCFieCz9DJtXoNe8me7lbMeSGac8FXOnriw4wQ.; WEIBOCN_FROM=1110006030; _T_WM=20576566259; XSRF-TOKEN=87e52e; MLOGIN=1; M_WEIBOCN_PARAMS=luicode%3D20000174%26uicode%3D20000174",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "accept-encoding":"gzip, deflate, br",
        "accept-language":"zh-CN,zh;q=0.9",
        "x-requested-with":"XMLHttpRequest",
        "x-xsrf-token":"2a4cad"
    }
    ])

    userId = '7423347358'  # 修改微博用户id
    mysql_config = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "123456",
        "db": "weibo",
        "charset": "utf8mb4"
    }


    # #获取多层粉丝列表及社交网络图
    fanNum = 0 #把fanNum设为数字,（0表示爬取全部粉丝）
    fanLevel = 2   #set fanLevel in (1,2,3)
    get_allfans(headers, userId, fanNum, fanLevel, mysql_config)

def get_allfans(headers, userId, fanNum, fanLevel, mysql_config):
    get_allfan = AllFans(headers, userId, fanNum,fanLevel, mysql_config)
    get_allfan.get_allfans()

if __name__ == "__main__":  # 相当于程序入口
    main()