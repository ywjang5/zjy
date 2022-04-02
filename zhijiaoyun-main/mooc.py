import requests
import urllib3
import random
import json
import time
import random

# 解决警告 
urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

session = requests.Session()

session.headers = headers

class Mooc:
    def __init__(self):
        self.count = 0
        self.prepareWork()
        self.getCookie()
        self.download_code()
        self.login()
        self.courseNeedInfo()
    
    def prepareWork(self):
        self.userName = input('请输入你的账号：') 
        self.passWord = input('请输入你的密码：')
        
        pinlun = input('请输入是否需要评论：1.评论   2.不评论 ')
        
        # 1 评论  0 不评论
        if pinlun == '2':
            self.whetherNeedPinlun = 0
        else:
            self.whetherNeedPinlun = 1

    def getCookie(self):
        url = 'https://mooc.icve.com.cn/'

        session.get(url, verify=False)
    
    # 下载验证码到本件夹下
    def download_code(self):
        r = random.random()
        
        url = "https://mooc.icve.com.cn/portal/LoginMooc/getVerifyCode?ts=" + str(r)

        res = session.get(url, verify=False)
        
        img = res.content

        with open('verifycode.png', 'wb') as f:
            f.write(img)

    def login(self):
        url = 'https://mooc.icve.com.cn/portal/LoginMooc/loginSystem'

        verifyCode = input("请输入验证码: ")

        data = {
        'userName': self.userName,
        'password': self.passWord,
        'verifycode': verifyCode
        }
        res = session.post(url, data=data, verify=False).json()
        
        if(res['code'] != 1):
            print('登录失败, 请检查账号 密码 验证码.')
            exit()
        else:
            self.token = res['token']
            # 姓名
            self._name = res['displayName']
            print('登录成功! 欢迎你: ' + self._name)
 
    def courseNeedInfo(self):
        url = 'https://mooc.icve.com.cn/portal/Course/getMyCourse?isFinished=0&page=1&pageSize={}'.format(20)

        res = json.loads(session.get(url, verify=False).text)

        if res['code'] != 1:
            print('课程获取失败！')
            exit() 

        courseList = res['list']
    
        for i in range(len(courseList)):        
            courseName = courseList[i]['courseName']           
            print(str(i+1) + ':     ' + courseName)

        i = int(input('你所学课程如上, 请选择: ')) - 1

        # courseInfo = courseList[i]

        self.Id = courseList[i]['Id']
        self.courseOpenId = courseList[i]['courseOpenId']
        self.stuId = courseList[i]['stuId']

        time.sleep(3)

        self.getProcessList()
        
    def getProcessList(self):
        url = 'https://mooc.icve.com.cn/study/learn/getProcessList'

        data = {
            'courseOpenId': self.courseOpenId
        }

        res = json.loads(session.post(url, data=data, verify=False).text)

        if res['code'] != 1:
            print('章节信息获取失败！')
            exit()

        moduleList = res['proces']['moduleList']

        for module in moduleList:
            Mlist = []

            moduleId = module['id']
            moduleName = module['name']
            moduleResId = module['ResId']
            modulePercent = module['percent']

            if moduleResId != "":
                time.sleep(1)
                continue

            Mdic = {
                'moduleId': moduleId,
                'moduleName': moduleName
            }
            Mlist.append(Mdic)

            if modulePercent == 100:
                print('目录: ' + moduleName +', 进度100%(自动跳过)')
                continue

            print('目录: ' + moduleName)
            self.getTopicId(Mlist) 

            time.sleep(3)
    
    def getTopicId(self, Mlist):
        url = 'https://mooc.icve.com.cn/study/learn/getTopicByModuleId'

        for moduleInfo in Mlist:
            moduleId = moduleInfo['moduleId']

            data = {
                'courseOpenId': self.courseOpenId,
                'moduleId': moduleId
            }

            res = json.loads(session.post(url, data=data, verify=False).text)

            if res['code'] != 1:
                print('TopicId获取出错！')
                exit()
            
            topicList = res['topicList']

            for topic in topicList:
                Tlist = []

                topicId = topic['id']
                topicName = topic['name']
                studyStatus = topic['studyStatus']

                if studyStatus == 1:
                    print('    子目录: ' + topicName[:10] + '..'  +  ', 进度100%(自动跳过)')
                    continue

                Tdic = {
                    'topicId': topicId,
                    'moduleId': moduleId
                }

                Tlist.append(Tdic)
                
                print('    子目录: ' + topicName)
                self.getCellId(Tlist) 

                time.sleep(3)
            time.sleep(5)
    
    def getCellId(self, Tlist):
        url = 'https://mooc.icve.com.cn/study/learn/getCellByTopicId'

        for topicInfo in Tlist:
            topicId = topicInfo['topicId']
            moduleId = topicInfo['moduleId']

            data = {
                'courseOpenId': self.courseOpenId,
                'topicId': topicId
            }

            res = json.loads(session.post(url, data=data, verify=False).text)

            if res['code'] != 1:
                print('CellId获取失败！')
                exit()
            
            cellList = res['cellList']

            for cell in cellList:
                Clist = []
                cellId = cell['Id'] 
                categoryName = cell['categoryName'] 
                cellName = cell['cellName']
                isStudyFinish = cell['isStudyFinish']
                resId = cell['resId']
                childNodeList = cell['childNodeList']

                Cdic = {
                    'cellId': cellId,
                    'categoryName': categoryName,
                    'cellName': cellName,
                    'moduleId': moduleId,
                    'topicId': topicId,
                    'isStudyFinish': isStudyFinish,
                    'resId': resId,
                    'childNodeList': childNodeList
                }
                
                Clist.append(Cdic)
                self.doIt(Clist)

                time.sleep(3)
            time.sleep(5)

    def doIt(self, Clist):
        for cell in Clist:
            cellId = cell['cellId']
            categoryName = cell['categoryName']
            cellName = cell['cellName'][:10] + '..' 
            moduleId = cell['moduleId']
            topicId = cell['topicId']
            isStudyFinish = cell['isStudyFinish']
            resId = cell['resId']
            childNodeList = cell['childNodeList']

            if isStudyFinish:
                print('         文件: ' + cellName + ', 进度100%(自动跳过)')
                continue

            if categoryName == '视频' or categoryName == '音频':
                print('         文件: ' + cellName + ', 开始刷课！！')
                print('         请等待..')
                
                shuake = Shuake(self.courseOpenId, cellId, moduleId)
                shuake.VideoInfo()

                shuake.video()
                
                if self.whetherNeedPinlun:
                    shuake.pinglun()

            elif categoryName =='ppt' or  categoryName == 'ppt文档' or categoryName == 'office文档' or categoryName == 'office' or categoryName == '文档' or categoryName == '图片':              
                print('         文件: ' + cellName + ', 开始刷课！！')
                print('         请等待..')
                
                shuake = Shuake(self.courseOpenId, cellId, moduleId)
                shuake.pptInfo()
                shuake.wendang()

                if categoryName == '文档':
                    shuake.wendangAddTime()
                
                if self.whetherNeedPinlun:
                    shuake.pinglun()

            elif categoryName == '讨论':
                print('         文件: ' + cellName + ', 开始刷课！！')
                print('         请等待..')
                
                shuake = Shuake(self.courseOpenId, cellId, moduleId)
                shuake.taolun(resId)

            elif categoryName == '子节点':
                for chiledCell in childNodeList:
                    childClist = []
                    cellIdC = chiledCell['Id'] 
                    categoryNameC = chiledCell['categoryName'] 
                    cellNameC = chiledCell['cellName']
                    resIdC = chiledCell['resId']
                    isStudyFinishC= chiledCell['isStudyFinish']
                    childNodeListC = []

                    childCdic = {
                        'cellId': cellIdC,
                        'categoryName': categoryNameC,
                        'cellName': cellNameC,
                        'moduleId': moduleId,
                        'topicId': topicId,
                        'resId': resIdC,
                        'isStudyFinish': isStudyFinishC,
                        'childNodeList': childNodeListC
                    }
                    
                    childClist.append(childCdic)
                    self.doIt(childClist)
                    time.sleep(3)

            elif categoryName == '作业' or categoryName == '测验':
                print('         文件: ' + cellName + ', 开始刷课！！')
                print('         notice: 作业/测验会刷两次')
                print('         请等待..')

                ReplyCount, agreeWorkExam= self.getWorkExamData(resId)

                if agreeWorkExam != 'agree':
                    print('         作业/测试时间已过期, 跳过')
                    continue
                else:
                    if ReplyCount == -1 or ReplyCount >=2:
                        time.sleep(1)
                        studentWorkId = self.workDetail(resId)

                        if studentWorkId == "":
                            time.sleep(3)
                            uniqueId, bigQuestions, questions = self.workExamPerview(resId)
                            for bigQuestion in bigQuestions:
                                if bigQuestion['Title'] == '简答题' or bigQuestion['Title'] == '主观题':
                                    print('         有简答题/主观题, 请手动实现')
                                    continue

                                examList = []
                                for question in questions:
                                    DAdic = {
                                        'Answer': '1',
                                        'questionId': question['questionId'],
                                        'questionType': question['questionType']
                                    }
                                    examList.append(DAdic)
                                    break

                                time.sleep(5)
                                shuake = Shuake(self.courseOpenId, cellId, moduleId)
                                shuake.zuoye(examList, uniqueId)
                                shuake.zuoyeSubmit(uniqueId, resId)

                                ZYDic = {
                                    'cellId': cellId,
                                    'categoryName': categoryName,
                                    'cellName': cellName,
                                    'moduleId': moduleId,
                                    'topicId': topicId,
                                    'isStudyFinish': False,
                                    'resId': resId,
                                    'childNodeList': []
                                }

                                ZYList = [ZYDic]
                                self.doIt(ZYList)
                                    
                        else:
                            # 作业/测试做第二次执行
                            time.sleep(20)
                            examList = self.ExamHistory(resId, studentWorkId, categoryName)
                            if examList == []:
                                print('         有简答题/主观题, 请手动实现')
                                continue
                            else:
                                time.sleep(3)
                                uniqueId, bigQuestions, questions = self.workExamPerview(resId)

                                time.sleep(1)

                                shuake = Shuake(self.courseOpenId, cellId, moduleId)
                                shuake.zuoye(examList, uniqueId)
                                shuake.zuoyeSubmit(uniqueId, resId)                              
                    else:
                        print('         作业/测试只能做一次或需要审批, 请手动实现')
                        continue
            
            elif categoryName == '其它'  or categoryName == 'swf':
                print('         文件: ' + cellName + ', 开始刷课！！')
                print('         请等待..')

                shuake = Shuake(self.courseOpenId, cellId, moduleId)
                shuake.other()
            
            elif categoryName == '压缩包':
                print('         文件: ' + cellName + ', 开始刷课！！')
                print('         请等待..')

                shuake = Shuake(self.courseOpenId, cellId, moduleId)
                shuake.yasuobao()

            else:
                print('         该程序处理不了！')

            time.sleep(3)

    def getWorkExamData(self, resId):
        url = 'https://mooc.icve.com.cn/study/workExam/getWorkExamData'

        data = {
            'courseOpenId': self.courseOpenId,
            'workExamId': resId,
            'workExamType': 0
        }

        res = json.loads(session.post(url, data=data, verify=False).text)

        if res['code'] != 1:
            print('获取做作业数据失败！')
            exit()
        
        ReplyCount = res['workExam']['ReplyCount']

        agreeWorkExam = res['workExam']['agreeWorkExam']


        return ReplyCount, agreeWorkExam

    def workDetail(self, resId):
       
        url = 'https://mooc.icve.com.cn/study/workExam/detail'

        data = {
            'courseOpenId': self.courseOpenId,
            'workExamId': resId,
            'workExamType': 0
        }

        res = json.loads(session.post(url, data=data, verify=False).text)

        if res['code'] != 1:
            print('获取做作业Id失败！')
            exit()

        resList = res['list']

        if resList == []:
            return ""

        studentWorkId = resList[0]['Id']

        return studentWorkId

    def ExamHistory(self, resId, studentWorkId, categoryName):
       
        url = 'https://mooc.icve.com.cn/study/workExam/history'

        if categoryName == '测验':
            workExamType = 1
        else:
            workExamType = 0

        data = {
            'courseOpenId': self.courseOpenId,
            'workExamId': resId,
            'studentWorkId': studentWorkId,
            'workExamType': workExamType
        }

        res = json.loads(session.post(url, headers=headers, data=data, verify=False).text)

        if res['code'] != 1:
            print('获取历史作业答案失败')
            exit()
        
        workExamData = res['workExamData']
        bigQuestions = json.loads(workExamData)['bigQuestions']

        for i in bigQuestions:
            Title = i ['Title']

            if Title == "简答题" or Title == "主观题":
                return []

        questions = json.loads(workExamData)['questions']

        _list = []
        for i in range(len(questions)):
            questionId = questions[i]['questionId']
            Answer = questions[i]['Answer']
            questionType = questions[i]['questionType']

            DAdic = {
                'Answer': Answer,
                'questionId': questionId,
                'questionType': questionType
            }

            _list.append(DAdic)
        
        return _list

    def workExamPerview(self, resId):
        url = 'https://mooc.icve.com.cn/study/workExam/workExamPreview'

        data = {
            'courseOpenId': self.courseOpenId,
            'workExamId': resId,
            'agreeHomeWork': 'agree',
            'workExamType': 0
        }

        res = json.loads(session.post(url, data=data, verify=False).text)

        if res['code'] != 1:
            print('获取作业题目失败！')
            exit()

        uniqueId = res['uniqueId']
        workExamData = res['workExamData']

        if workExamData == "":
            bigQuestions = res['paperData']['bigQuestions']
            questions = res['paperData']['questions']
        else:
            bigQuestions = json.loads(workExamData)['bigQuestions']
            questions = json.loads(workExamData)['questions']

        return uniqueId, bigQuestions, questions


class Shuake:
    def __init__(self, courseOpenId, cellId, moduleId):
        self.courseOpenId = courseOpenId
        self.cellId = cellId
        self.moduleId = moduleId

    def VideoInfo(self):
        self.count = 0
        url = 'https://mooc.icve.com.cn/study/learn/viewDirectory'

        data = {
            'courseOpenId': self.courseOpenId,
            'cellId': self.cellId,
            'fromType': 'stu',
            'moduleId': self.moduleId
        }

        res = session.post(url, data=data, verify=False).text

        res = self.checkRes(url, data, res, 30)

        if res['code'] != 1:
            print('获取视频信息出错！')
            exit()
        
        self.videoPercent = res['VideoPercent']
        courseCell = res['courseCell']
        self.CategoryName = courseCell['CategoryName']
        self.VideoTimeLong = courseCell['VideoTimeLong']
        self.currentTime = res['currentTime']
   
    def pptInfo(self):
        self.count = 0
        url = 'https://mooc.icve.com.cn/study/learn/viewDirectory'

        data = {
            'courseOpenId': self.courseOpenId,
            'cellId': self.cellId,
            'fromType': 'stu',
            'moduleId': self.moduleId
        }

        res = session.post(url, data=data, verify=False).text

        res = self.checkRes(url, data, res, 10)

        if res['code'] != 1:
            print('获取文档信息出错！')
            exit()
        
        self.videoPercent = res['VideoPercent']
        courseCell = res['courseCell']
        self.CategoryName = courseCell['CategoryName']
        self.PageCount = courseCell['PageCount']
    
    def video(self):
        time.sleep(3)
        url = 'https://mooc.icve.com.cn/study/learn/statStuProcessCellLogAndTimeLong'

        data = {
                'courseId': '',
                'courseOpenId': self.courseOpenId,
                'moduleId': self.moduleId,
                'cellId': self.cellId,
                'auvideoLength': self.VideoTimeLong,
                'videoTimeTotalLong': self.VideoTimeLong,
                'sourceForm': '993'
            }
        
        
        res = json.loads(session.post(url, data=data, verify=False).text)
        if res['code'] == -1:
            print('notice: 刷视频异常')
            time.sleep(15)
            res = json.loads(session.post(url, data=data, verify=False).text)

        print('视频返回信息: ' + str(res))
        if res['code'] != 1:
            print('刷视频出错！')
            exit()

        # for i in [2, 1, 0]:
        #     time.sleep(60)

        #     auvideoLength = self.VideoTimeLong-i*60 + 12

        #     if auvideoLength > self.VideoTimeLong:
        #         auvideoLength = self.VideoTimeLong

        #     data = {
        #         'courseId': '',
        #         'courseOpenId': self.courseOpenId,
        #         'moduleId': self.moduleId,
        #         'cellId': self.cellId,
        #         'auvideoLength': auvideoLength,
        #         'videoTimeTotalLong': self.VideoTimeLong,
        #         'sourceForm': '993'
        #     }

        #     res = json.loads(session.post(url, data=data, verify=False).text)
        #     # print('视频返回信息: ' + str(res))
        #     if res['code'] != 1:
        #         print('刷视频出错！')
        #         exit()
        # url = 'https://mooc.icve.com.cn/study/learn/statStuProcessCellLogAndTimeLong'

        # otherTime = self.VideoTimeLong - self.currentTime

        # forNum = int(otherTime / 60) + 1

        # for i in range(forNum):
        #     time.sleep(60)

        #     auvideoLength = self.currentTime + 60 * (i+1)

        #     if auvideoLength > self.VideoTimeLong:
        #         auvideoLength = self.VideoTimeLong

        #     data = {
        #         'courseId': '',
        #         'courseOpenId': self.courseOpenId,
        #         'moduleId': self.moduleId,
        #         'cellId': self.cellId,
        #         'auvideoLength': auvideoLength,
        #         'videoTimeTotalLong': self.VideoTimeLong,
        #         'sourceForm': '993'
        #     }

        #     res = json.loads(session.post(url, data=data, verify=False).text)
        #     # print('视频返回信息: ' + str(res))
        #     if res['code'] != 1:
        #         print('刷视频出错！')
        #         exit()

    def wendang(self):
        url = 'https://mooc.icve.com.cn/study/learn/statStuProcessCellLogAndTimeLong'

        data = {
                'courseId': '',
                'courseOpenId': self.courseOpenId,
                'moduleId': self.moduleId,
                'cellId': self.cellId,
                'videoTimeTotalLong': 0,
                'sourceForm': 1030
            }
        
        res = json.loads(session.post(url, data=data, verify=False).text)

        if res['code'] == -1:
            print('notice: 刷文档异常')
            time.sleep(10)
            res = json.loads(session.post(url, data=data, verify=False).text)

        if res['code'] != 1:
            print('刷文档出错！')
            exit()

    def other(self):
        url = 'https://mooc.icve.com.cn/study/learn/statStuProcessCellLogAndTimeLong'

        data = {
            'courseId': '',
            'courseOpenId': self.courseOpenId,
            'moduleId': self.moduleId,
            'cellId': self.cellId,
            'videoTimeTotalLong': 0,
            'sourceForm': 1030
            }

        res = json.loads(session.post(url, data=data, verify=False).text)

        if res['code'] != 1:
            print('刷其他文件出错！')
            exit()

    def yasuobao(self):
        url = 'https://mooc.icve.com.cn/study/learn/statStuProcessCellLogAndTimeLong'

        data = {
            'courseId': '',
            'courseOpenId': self.courseOpenId,
            'moduleId': self.moduleId,
            'cellId': self.cellId,
            'auvideoLength': 10,
            'videoTimeTotalLong': 0,
            'sourceForm': 888
            }

        res = json.loads(session.post(url, data=data, verify=False).text)

        if res['code'] != 1:
            print('刷压缩包出错！')
            exit()

    def taolun(self, resId):
        self.count = 0
        url = 'https://mooc.icve.com.cn/study/discussion/addStuViewTopicRemember'

        data = {
            'courseOpenId': self.courseOpenId,
            'topicId': resId
        }

        res = session.post(url, data=data, verify=False).text

        res = self.checkRes(url, data, res, 5)
 
        if res['msg']  not in ["浏览成功", "已浏览主题"]:
            print('讨论类文件出错！')
            exit()
        
    def pinglun(self):
        for i in range(1, 5):
            self.count = 0
            url = 'https://mooc.icve.com.cn/study/learn/saveAllReply'

            if i == 2:
                star = 5
            else:
                star = 0
            
            textDic = {
                "ResId": "",
                "replyToUserId": "",
                "replyToDisplayName": "",
                "Content": "<p>{}</p>".format(random.choice(["好", "无", "内容丰富", "。", "通俗易懂", "课件内容丰富详细", "没有问题", "很详细"])),
                "CourseOpenId": self.courseOpenId,
                "CategoryId": "bbszhtlq-{}".format(self.courseOpenId),
                "cellId": self.cellId,
                "star": str(star),
                "SignType": i
            }

            data = {
                'replyData': str(textDic),
                'urlList': '[]'
            }

            res = session.post(url, data=data, verify=False).text
            
            res = self.checkRes(url, data, res, 5)

            if res['code'] == -100 or res['code'] == -1:
                print('视频异常, 跳过')
                time.sleep(30)
                return

            if res['code'] != 1:
                print('评论出错！')
                exit()
                
            time.sleep(4)
        print('         评论完成！！')
   
    def wendangAddTime(self):
        self.count = 0
        time.sleep(3)
        url = 'https://mooc.icve.com.cn/study/learn/computatlearningTimeLong'


        data = {
            'courseId': '',
            'courseOpenId': self.courseOpenId,
            'moduleId': self.moduleId,
            'cellId': self.cellId,
            'auvideoLength': random.randint(180, 240),
        }

        res = session.post(url, data=data, verify=False).text

        res = self.checkRes(url, data, res, 10)

        if res['code'] != 1:
            print('notice: 刷时间出错！')
            time.sleep(10)
            return
       
    def zuoye(self, examList, uniqueId):
        for exam in examList:
            self.count = 0
            # 答案
            Answer = exam['Answer']
            questionId = exam['questionId']
            questionType = exam['questionType']

            url = 'https://mooc.icve.com.cn/study/workExam/onlineHomeworkAnswer'

            data = {
                'studentWorkId': '',
                'questionId': questionId,
                'workExamType': 0,
                'paperStuQuestionId':'', 
                'online': 1,
                'answer': Answer, 
                'userId': '',
                'questionType': questionType,
                'uniqueId': uniqueId
            }

            res = session.post(url, data=data, verify=False).text

            res = self.checkRes(url, data, res, 5)

            if res['code'] != 1:
                print('回答作业失败')
                exit()
            
            # print("回答题目Info：" + str(res))
            time.sleep(2)
    
    def zuoyeSubmit(self, uniqueId, workExamId):
        url = 'https://mooc.icve.com.cn/study/workExam/workExamSave'

        data = {
            'uniqueId': uniqueId,
            'workExamId': workExamId,
            'workExamType': 1,
            'courseOpenId': self.courseOpenId,
            'paperStructUnique': '',
            'useTime': random.randint(120, 180)
        }

        res = session.post(url, data=data, verify=False).text

        if res == '<h1>:(</h1>您的访问出错了':
            print('提交作业失败 15后重新提交')
            time.sleep(15)
            res = session.post(url, data=data, verify=False).text

        # res = self.checkRes(url, data, res, 30)
        res = json.loads(res)

        if res['code'] != 1:
            print('作业提交Info: ' + str(res))
            exit()

    def checkRes(self, url, data, res, Time):

        while res == '<h1>:(</h1>您的访问出错了':
            self.count = self.count + 1
            
            if self.count >= 2:
                print('访问出错,请等待十分钟, 再次运行')
                exit()

            print('         访问出错, {}秒后重新访问.'.format(Time))
            time.sleep(Time)
            res = session.post(url, data=data, verify=False).text

        return json.loads(res)

if __name__ == "__main__":
    Mooc()
    print('谢谢使用！')


