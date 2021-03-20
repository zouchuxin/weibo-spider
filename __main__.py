#-*- coding = utf-8 -*-
#@Time : 2021/2/4 15:44
#@Author : zou chuxin
#@File: __main__.py
#@Software: PyCharm

from weibo_spide_2021.comments import Comments
from weibo_spide_2021.fansList import Fanslist
from weibo_spide_2021.followList import FollowList
from weibo_spide_2021.allFans import AllFans
from weibo_spide_2021.allFollow import AllFollow
from weibo_spide_2021.getInfos import GetInfos
from weibo_spide_2021.fansInfoList import FansInfolist
from weibo_spide_2021.followInfoList import FollowInfoList
from weibo_spide_2021.AllFansInfo import AllFansInfo
from weibo_spide_2021.AllFollowInfo import AllFollowInfo
import random




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
    }, {
        "cookie": "SCF=Al0kxrTjWmyquyWfhP8aS1Flri1XZKyn4O9SfCIY8uDRXDNg7XovAEerY_NbEFkqtiCGlp5HMvuMVhgGBM9-raI.; SUB=_2A25NKn6QDeRhGeBP6lYY9C3Fzz-IHXVu1QLYrDV6PUJbktANLRHHkW1NRZVO-UNI2ZDyhFq0oNKasUDfGF87-6ts; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWZ.2peNWRuScjKBxMq-znZ5JpX5K-hUgL.FoqpeKB4She4She2dJLoIE8oIGHbqr.LxKML1-2L1hBLxK.L1KnLB.qLxKqLB-eLBKet; ALF=1616223168; _T_WM=36982414575; XSRF-TOKEN=421521; WEIBOCN_FROM=1110005030; MLOGIN=1; M_WEIBOCN_PARAMS=uicode%3D20000174",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding":"gzip, deflate, br",
        "accept-language":"zh-CN,zh;q=0.9"
    }
    ])

    userId = '6558422975'  # 修改微博用户id
    mysql_config = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "123456",
        "db": "weibo",
        "charset": "utf8mb4"
    }


    # #获取评论内容
    # weibo_filename = "E:\Python学习\studyPython\sina\weiboSpider\weibo\Alan_Wu214\\6558422975.csv"
    # get_comment(headers, userId, weibo_filename, mysql_config)
    #
    # #获取粉丝列表
    # get_fanList(headers, userId, mysql_config)
    # #获取粉丝信息列表
    # #get_fansInfoList(headers, userId, mysql_config)
    #
    # #获取关注列表
    # get_followList(headers, userId, mysql_config)
    # #获取关注列表信息
    # #get_followInfoList(headers, userId, mysql_config)
    #
    # #获取多层粉丝列表及社交网络图
    fanNum = 0 #把fanNum设为数字,（0表示爬取全部粉丝）
    fanLevel = 2   #set fanLevel in (1,2,3)
    get_allfans(headers, userId, fanNum, fanLevel, mysql_config)
    #获取多层粉丝信息列表及社交网络图
    #get_allfansinfo(headers, userId, fanNum, fanLevel, mysql_config)

    #获取多层关注列表及社交网络图
    followNum = 100 #把followNum设为数字,（0表示爬取全部粉丝）
    followLevel = 2  #set followLevel in (1,2,3)
    get_allfollow(headers, userId, followNum, followLevel,mysql_config)
    #获取多层关注信息列表及社交网络图
    #get_allfollowinfo(headers, userId, followNum, followLevel, mysql_config)


    #获取想要列表的个人信息
    Info_filename = ""
    # get_infos(headers, userId, Info_filename,mysql_config)


def get_comment(headers, userId, weibo_filename, mysql_config):
    get_comment = Comments(headers, userId, weibo_filename, mysql_config)
    get_comment.get_all_comment()


def get_fanList(headers, userId, mysql_config):
    get_fanslist = Fanslist(headers, userId, mysql_config)
    get_fanslist.get_fanslist()

def get_fansInfoList(headers, userId, mysql_config):
    get_fansInfoList = FansInfolist(headers, userId, mysql_config)
    get_fansInfoList.get_fansinfolist()

def get_followList(headers, userId, mysql_config):
    get_followlist = FollowList(headers, userId, mysql_config)
    get_followlist.get_followlist()

def get_followInfoList(headers, userId, mysql_config):
    get_followInfoList = FollowInfoList(headers, userId, mysql_config)
    get_followInfoList.get_followinfolist()

def get_allfans(headers, userId, fanNum, fanLevel, mysql_config):
    get_allfan = AllFans(headers, userId, fanNum,fanLevel, mysql_config)
    get_allfan.get_allfans()

def get_allfollow(headers, userId, followNum, followLevel, mysql_config):
    get_all_follow = AllFollow(headers,userId,followNum,followLevel, mysql_config)
    get_all_follow.get_allfollow()

def get_allfansinfo(headers, userId, fanNum, fanLevel, mysql_config):
    get_allfaninfo = AllFansInfo(headers, userId, fanNum,fanLevel, mysql_config)
    get_allfaninfo.get_allfansinfo()

def get_allfollowinfo(headers,userId,followNum,followLevel, mysql_config):
    get_allfollowinfo = AllFollowInfo(headers,userId,followNum,followLevel, mysql_config)
    get_allfollowinfo.get_allfollowinfo()

def get_infos(headers, userId, filename, mysql_config):
    get_info = GetInfos(headers,userId,filename, mysql_config)
    get_info.get_infos()

if __name__ == "__main__":  # 相当于程序入口
    main()

