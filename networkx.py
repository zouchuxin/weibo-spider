#-*- coding = utf-8 -*-
#@Time : 2021/2/6 9:50
#@Author : zou chuxin
#@File: networkx.py
#@Software: PyCharm
from matplotlib import pyplot as plt
import networkx as nx

class NetWork:
    def __init__(self,userId, dataList, fNum, fLevel):
        self.userId = userId
        self.dataList = dataList
        self.fNum = fNum
        self.fLevel = fLevel

    def get_network(self):
        if self.fNum == 0:
            self.create_networkx_allfans(self.userId,self.dataList, self.fanLevel)
        else:
            self.create_networkx(self.userId,self.dataList, self.fanNum, self.fanLevel)

    def create_networkx_allfans(self, userId, dataList, fLevel):
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
                if fLevel < 2:
                    continue
                else:
                    n = n + 1
                    print(n, "\n")
                    for k in range(0, len(dataList[2][n])):
                        print("第三轮", dataList[2][n][k])
                        G.add_edge(dataList[1][i][j][1], dataList[2][n][k][1])
                        if fLevel < 3:
                            continue
                        else:
                            m = m + 1
                            for l in range(0, len(dataList[3][m])):
                                print("第四轮", dataList[3][m][l])
                                G.add_edge(dataList[2][n][k][1], dataList[3][m][l][1])
        nx.draw_networkx(G)
        net_pic_savepath = userId + "的" + str(fLevel + 1) + "层" + "全部粉丝社交网络图.png"
        plt.savefig(net_pic_savepath)
        plt.show()


    def create_networkx(self, userId, dataList, fNum, fLevel):
        G = nx.DiGraph()
        G.add_node(userId)
        n = -1
        m = -1
        if len(dataList[0][0]) < fNum:
            length1 = len(dataList[0][0])
        else:
            length1 = fNum
        for i in range(0, length1):
            print("第一轮", dataList[0][0][i])
            G.add_edge(userId, dataList[0][0][i][1])
            if len(dataList[1][i]) < fNum:
                length2 = len(dataList[1][i])
            else:
                length2 = fNum
            for j in range(0, length2):
                print("第二轮", dataList[1][i][j])
                G.add_edge(dataList[0][0][i][1], dataList[1][i][j][1])
                if fLevel < 2:
                    continue
                else:
                    n = n + 1
                    print("第二轮第%d位粉丝：\n" % (n+1))
                    if len(dataList[2][n]) < fNum:
                        length3 = len(dataList[2][n])
                    else:
                        length3 = fNum
                    for k in range(0, length3):
                        print("第三轮", dataList[2][n][k])
                        G.add_edge(dataList[1][i][j][1], dataList[2][n][k][1])
                        if fLevel < 3:
                            continue
                        else:
                            m = m + 1
                            print("第三轮第%d位粉丝：\n" % (m+1))
                            if len(dataList[3][m]) < fNum:
                                length4 = len(dataList[3][m])
                            else:
                                length4 = fNum
                            for l in range(0, length4):
                                print("第四轮", dataList[3][m][l])
                                G.add_edge(dataList[2][n][k][1], dataList[3][m][l][1])
        nx.draw_networkx(G)
        net_pic_savepath = userId +"的" + str(fLevel + 1) + "层" + str(fNum) + "位" + "粉丝社交网络图.png"
        plt.savefig(net_pic_savepath)
        plt.show()
