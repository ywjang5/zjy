from logging import disable
import requests
import json
import random
import time
import os
# 验证码图片识别
from utils import captcha

class ZhiJiao:
    def __init__(self, ):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }
    # 获取cookie
    def getCookie_acw_tc(self):
        url = 'https://zjy2.icve.com.cn/portal/login.html'
        self.session.get(url, verify=False)

        return 1
    # 验证码
    def verfiyCode(self):     
        url = "https://zjy2.icve.com.cn/api/common/VerifyCode/index" + "?t=" + str(random.random())

        res = self.session.get(url, verify=False)
        
        img = res.content
        # 下载到本地
        with open('verifycode.png', 'wb') as f:
            f.write(img)
        # 识别验证码 
        self.code = captcha('verifycode.png')
        # 删除图片
        os.remove('verifycode.png')

        return 1
    # 登录
    def login(self, userName, passWord):
        url = 'https://zjy2.icve.com.cn/api/common/login/login'

        data = {
            'userName': userName,
            'userPwd': passWord,
            'verifyCode': self.code
        }
        res = self.session.post(url, data=data, verify=False).json()

        if res['code'] == -16:
            print('⚠️  验证码识别错误！')
            return 0
        elif res['code'] == 1:
            self.token = res['token']
            userName = res['displayName']
            print('{}, 欢迎您！🎉🎉🎉'.format(userName))         
            return 1
        else:
            print(res)
            print('❌ 登录异常, 出现未知错误, 请联系管理员！')
            exit()
    # 获取所学课程Info
    def courseInfo(self):
        url = 'https://zjy2.icve.com.cn/api/student/learning/getLearnningCourseList'

        res = self.session.post(url, verify=False)
 
        if res.text == '':
            return ''
        else:
            # 课程信息
            courseList = res.json()['courseList']

            return courseList
    # 获取所有章节Info
    def chapter(self, course):
        # 所需参数
        self.courseOpenId = course['courseOpenId']
        self.openClassId = course['openClassId']

        url = 'https://zjy2.icve.com.cn/api/study/process/getProcessList'

        params = {
            'courseOpenId': self.courseOpenId,
            'openClassId': self.openClassId
        }
        
        moduleList = self.session.post(url, params=params, verify=False).json()['progress']['moduleList']

        List = []
        for module in moduleList:
            # 进度
            percent = module['percent']
            if percent == 100:
                continue
            # 章节id
            moduleId = module['id']
 
            List.append(moduleId)

        return List
    # 获取章节下所有子目录Info
    def topic(self, chapterList):
        url = 'https://zjy2.icve.com.cn/api/study/process/getTopicByModuleId'

        List = []
        for moduleId in chapterList:
            data = {
                'courseOpenId': self.courseOpenId,
                'moduleId': moduleId
            }
            # 子目录
            topicList = self.session.post(url,  data=data).json()['topicList']

            for topic in topicList:
                topicId = topic['id']

                dic = {
                    'moduleId': moduleId,
                    'topicId': topicId
                }

                List.append(dic)
            
            time.sleep(2)

        return List 
    # 获取所有文件Info
    def cell(self, topicList):
        url = 'https://zjy2.icve.com.cn/api/study/process/getCellByTopicId'
        
        List = []
        for topic in topicList:
            moduleId = topic['moduleId']
            topicId = topic['topicId']

            data = {
                'courseOpenId': self.courseOpenId,
                'openClassId': self.openClassId,
                'topicId': topicId
            }

            cellList = self.session.post(url, data=data, verify=False).json()['cellList']

            for cell in cellList:
                cellId = cell['Id']
                cellName = cell['cellName']
                categoryName = cell['categoryName']
                childNodeList = cell['childNodeList']
                stuCellPercent = cell['stuCellPercent']

                dic = {
                    'cellId': cellId,
                    'moduleId': moduleId,
                    'cellName': cellName,
                    'categoryName': categoryName,
                    'childNodeList': childNodeList,
                    'stuCellPercent': stuCellPercent
                }

                List.append(dic)
            time.sleep(2)

        return List
    # 将cookie写入本地
    def set_cookie(self, ck):
        obj = json.loads(ck)

        cookies = {}
        for o in obj:
            cookies[o[0]] = o[1]

        self.session.cookies.update(cookies)
    

if __name__ == '__main__':
    print('请运行main.py文件')

