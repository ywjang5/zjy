import time
import random
 
class ShuaKe:
    def __init__(self, session, courseOpenId, openClassId, config):
        self.session = session
        self.courseOpenId = courseOpenId
        self.openClassId = openClassId
        self.config = config
    # 时间装饰器
    def timer(func):
        def wrapper(self, cellId, moduleId, cellName, categoryName, count):
            t1 = time.time()
            func(self, cellId, moduleId, cellName, categoryName, count)
            t2 = time.time()
            print('⏰ 花费时长：{}分{}秒'.format(int(int(t2 - t1)/60), int(t2-t1)%60))
        return wrapper
    # 刷视频/音频类
    @timer
    def video(self, cellId, moduleId, cellName, categoryName, count):
        res = self.info(cellId, moduleId, cellName, count)
        self.count = count

        # 视频总时长
        audioVideoLong = res['audioVideoLong']
        # 学习过的时长
        stuStudyNewlyTime = res['stuStudyNewlyTime']

        cellLogId = res['cellLogId']

        url = 'https://zjy2.icve.com.cn/api/common/Directory/stuProcessCellLog'

        forNum = int((audioVideoLong - stuStudyNewlyTime) / 10) + 2

        self.wrongCount = 0

        for i in range(forNum):
            if stuStudyNewlyTime-1 < 0:
                stuStudyNewlyTime = 1
                
            nowTime = stuStudyNewlyTime-1 + 10.000001*i
            
            if nowTime >= audioVideoLong: 
                stutyTime = audioVideoLong
            else:
                stutyTime = nowTime

            data = {
                'courseOpenId': self.courseOpenId,
                'openClassId': self.openClassId,
                'cellId': cellId,
                'cellLogId': cellLogId,
                'picNum': 0,
                'studyNewlyTime': stutyTime,
                'studyNewlyPicNum': 0
            }

            res = self.session.post(url, data=data, verify=False)
            status = self.dealRes(res, categoryName, 300)

            if status == False:
                self.count = self.count + 1
                if self.count >= 2:
                    print('⚠️ 文件访问出错过多, 程序退出！')
                    print('⚠️ 建议等待十分钟')
                    exit()
                self.video(cellId, moduleId, cellName, categoryName, self.count)
                return
            time.sleep(self.config['videoSpeed'])
    # 刷ppt/文档/图片类
    @timer
    def ppt(self, cellId, moduleId, cellName, categoryName, count):
        res = self.info(cellId, moduleId, cellName, count)
        self.count = count
        # 文档总页数
        pageCount = res['pageCount']

        cellLogId = res['cellLogId']

        url = 'https://zjy2.icve.com.cn/api/common/Directory/stuProcessCellLog'

        for i in range(2):
            data = {
                'courseOpenId': self.courseOpenId,
                'openClassId': self.openClassId,
                'cellId': cellId,
                'cellLogId': cellLogId,
                'picNum': i,
                'studyNewlyTime': '0',
                'studyNewlyPicNum': i * int(pageCount)
                }

            res = self.session.post(url, data=data, verify=False)

            status = self.dealRes(res, categoryName, 300)

            if status == False:
                self.count = self.count + 1
                if self.count >= 2:
                    print('⚠️ 文件访问出错过多, 程序退出！')
                    print('⚠️ 建议等待十分钟')
                    exit()
                self.ppt(cellId, moduleId, cellName, categoryName, self.count)
                return
            
            if i == 0:
                time.sleep(3)
    # 刷课件所需Info
    # 图片/压缩包/swf等文件只需发起该请求就可完成
    # 注意上述没学习时长
    def info(self, cellId, moduleId, cellName, count):
            self.count = count
            url = 'https://zjy2.icve.com.cn/api/common/Directory/viewDirectory'

            data = {
                'courseOpenId': self.courseOpenId,
                'openClassId': self.openClassId,
                'cellId': cellId,
                'flag': 's',
                'moduleId': moduleId
            }

            res = self.session.post(url, data=data, verify=False)

            status = self.dealRes(res, '进入页面', 60)

            if status == False:
                self.count = self.count + 1
                if self.count >= 2:
                    print('⚠️ 访问出错过多, 程序退出！')
                    print('⚠️ 建议等待十分钟')
                    exit()
                self.info(cellId, moduleId, cellName, self.count)
                return
            
            res = res.json()

            if res['code'] == -100:
                self.choiceCell(moduleId, cellId, cellName)
                res = self.info(cellId, moduleId, cellName, self.count)

                return res
                
            return res
    # 课件选择
    def choiceCell(self, moduleId, cellId, cellName):
        url = 'https://zjy2.icve.com.cn/api/common/Directory/changeStuStudyProcessCellData'
    
        data = {
            'courseOpenId': self.courseOpenId,
            'openClassId': self.openClassId,
            'moduleId': moduleId,
            'cellId': cellId,
            'cellName': cellName
        }
        
        res = self.session.post(url, data=data, verify=False).json()

        if res['code'] != 1:
            print("🚫 选择文件时，出现异常!")
            exit()
    # 评论
    def pinglun(self, cellId, activityType, star):
        url = 'https://zjy2.icve.com.cn/api/common/Directory/addCellActivity'
        
        data = {
            'courseOpenId': self.courseOpenId,
            'openClassId': self.openClassId,
            'cellId': cellId,
            'content': '{}'.format(random.choice(self.config['commentList'])),
            'docJson': '',
            'star': star,
            'activityType': activityType
        }

        res = self.session.post(url, data=data, verify=False).json()
        # PC端同一文件：评价 问答 笔记 纠错间隔需大于1分钟
        if res['code'] == -2:
            time.sleep(60)
            res = self.session.post(url, data=data, verify=False).json()

        if res['code'] != 1:
            print('\n\n❌ 评论时间间隔太快, 程序异常退出！\n\n')
            print('❌ 评论返回Info: {}'.format(res))
            exit()
    # 返回值处理
    def dealRes(self, res, categoryName, Time):
        # 返回结果可以json解析
        try:
            res.json()['code']

            if categoryName == '进入页面':
                List = [-1]
            else:
                List = [-1, -100]

            # 出错
            if res.json()['code'] in List:
                print('⚠️ 访问异常1, <{}>返回Info: {}'.format(categoryName, res.text))
                print('            请求状态码: {}'.format(res.status_code))
                if self.count < 1:
                    print('{}分钟后重新访问, 请等待...⏳'.format(int(Time/60)))
                    time.sleep(Time)
                return False
            elif res.json()['code'] == '-1':
                print('⚠️ 访问异常1, <{}>返回Info: {}'.format(categoryName, res.text))
                print('❌ 用户cookie信息过期, 请重新登录')
                exit()
            else:
                # {code: 1}正常数据
                if res.json()['code'] == 1 or res.json()['code'] == -100:
                    return True
                # 未知情况
                else:
                    print('❌ 异常1, <{}>返回Info: {}'.format(categoryName, res.text))
                    print('            请求状态码: {}'.format(res.status_code))
                    print('❌ 程序退出, 请联系作者')
                    exit()
        # 返回结果不可以解析
        except:
            # Time out
            if res.status_code == 504 or res.text == '':
                print('⚠️ 访问异常2, <{}>返回Info: {}'.format(categoryName, res.text))
                print('            请求状态码: {}'.format(res.status_code))
                if self.count < 1:
                    print('{}分钟后重新访问, 请等待...⏳'.format(int(Time/60)))
                    time.sleep(Time)
                return False
            # 未知情况
            else:
                print('❌ 异常2, <{}>返回Info: {}'.format(categoryName, res.text))
                print('            请求状态码: {}'.format(res.status_code))
                print('❌ 程序退出, 请联系作者')
                exit()


if __name__ == '__main__':
    print('请运行main.py文件')
