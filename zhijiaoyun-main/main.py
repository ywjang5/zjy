import os
import yaml
import json
import time
import urllib3
import threading
 
from utils import captcha
from zhijiao import ZhiJiao
from shuake import ShuaKe

# 解决警告
urllib3.disable_warnings()


if __name__ == "__main__":

    try:
        # 读取配置文件
        with open("config.yml", "r", encoding='utf-8') as f:
            data = f.read()
        # 加载配置文件
        config = yaml.safe_load(data)
    except IOError:
        print("❌ 初始化时出现错误：没找到配置文件！")
        exit(-1)
    except yaml.YAMLError as exc:
        print("❌ 初始化时出现错误：配置文件异常！")
        exit(-2)
    # 职教云实例对象
    zjy = ZhiJiao()
    print('开始登录...⏳')
    # 先判断有没有缓存Cookie
    if os.path.exists("cookies.json"):
        with open("cookies.json", "r", encoding='utf-8') as f:
            js = f.read()
        # 设置 Cookies
        zjy.set_cookie(js)
    # 课程列表
    courseList = zjy.courseInfo()
    if len(zjy.session.cookies.items()) == 0 or  courseList == '':
        print('⚠️  Cookie信息失效, 自动登录中...⏳')
        # 清空Cookies
        zjy.session.cookies.clear()
        # 获取cookie参数acw_tc
        zjy.getCookie_acw_tc()

        while True:
            # 登录
            if zjy.verfiyCode() and zjy.login(str(config['member']['user']), str(config['member']['pass'])):
                print('登录成功 ✅')
                courseList = zjy.courseInfo()

                if config['saveCookies']:
                    # 获取 Cookies
                    ck = json.dumps(zjy.session.cookies.items())
                    # 保存到文件
                    f = open("cookies.json", "w", encoding='utf-8')
                    f.write(ck)
                    f.close()
                break
            else:
                print('⚠️  2秒后将重新登录, 请等待...')
                time.sleep(2)
    else:
        print('登录成功！Cookie信息可以使用！🎉\n')
    # 打印课程名
    for i in range(len(courseList)):
        courseName = courseList[i]['courseName']
        print(str(i+1) +'   '+ courseName)
    # 选择课程
    while True:
        try:
            courseId = int(input('请选择你要刷的课程：')) - 1
        except ValueError:
            print("您输入的数据不符合规范！")
            continue

        if courseId >= len(courseList) or courseId  < 0:
            print("课程id不存在！")
            continue                   
        break
    print('开始刷课 <{}>'.format(courseList[courseId]['courseName']))
    print('获取各课件参数中, 请稍候...⏳')
    # 所有章节请求参数
    chapterList = zjy.chapter(courseList[courseId])
    # 所有子目录的请求参数
    topicList = zjy.topic(chapterList)
    # 所有文件的请求参数
    cellList = zjy.cell(topicList)
    #　刷课实例对象
    shuake = ShuaKe(zjy.session, zjy.courseOpenId, zjy.openClassId, config)
    # 刷课件函数
    def kejian():
        global cellList
        # 刷课件
        for cell in cellList:
            cellId = cell['cellId']
            moduleId = cell['moduleId']
            cellName = cell['cellName']
            categoryName = cell['categoryName']
            childNodeList = cell['childNodeList']
            stuCellPercent = cell['stuCellPercent']
            count = 0
            if stuCellPercent == 100:
                continue

            if categoryName != '子节点': 
                print("\n💼 任务类型: %s" % categoryName)

            # 刷视频文件
            if categoryName == '视频' or categoryName == '音频':
                print("📺 {} <{}> ".format(categoryName, cellName))
                print("⏳ 正在自动完成...")

                shuake.video(cellId, moduleId, cellName, categoryName, count)

                print("🎉 {}任务完成!".format(categoryName))
            
            elif categoryName == 'ppt文档' or  categoryName == '文档' or  categoryName == 'ppt' or categoryName == 'office文档':
                print("📽  {} <{}> ".format(categoryName, cellName, categoryName))
                print("⏳ 正在自动完成...")

                shuake.ppt(cellId, moduleId, cellName, categoryName, count)

                print("🎉 {}任务完成!".format(categoryName))
            
            elif categoryName == '压缩包' or categoryName == 'swf' or categoryName=='链接' or categoryName == '其他'  or categoryName == '图片':
                print("🔗 {} <{}> ".format(categoryName, cellName))
                print("⏳ 正在自动完成...")

                shuake.info(cellId, moduleId, cellName, count)

                print("🎉 {}任务完成!".format(categoryName))

            elif categoryName == '子节点':
                for childNode in childNodeList:
                    cellId = childNode['Id']
                    cellName = childNode['cellName']
                    categoryName = childNode['categoryName']
                    stuCellFourPercent = childNode['stuCellFourPercent']

                    if stuCellFourPercent == 100:
                        continue
                    
                    print("\n💼 任务类型: %s" % categoryName)

                    # 刷视频文件
                    if categoryName == '视频' or categoryName == '音频':
                        print("📺 {} <{}> ".format(categoryName, cellName))
                        print("⏳ 正在自动完成...")

                        shuake.video(cellId, moduleId, cellName, categoryName, count)

                        print("🎉 {}任务完成!".format(categoryName))
                    
                    elif categoryName == 'ppt文档' or  categoryName == '文档' or  categoryName == 'ppt' or categoryName == 'office文档':
                        print("📽  {} <{}> ".format(categoryName, cellName))
                        print("⏳ 正在自动完成...")

                        shuake.ppt(cellId, moduleId, cellName, categoryName, count)

                        print("🎉 {}任务完成!".format(categoryName))
                    
                    elif categoryName == '压缩包' or categoryName == 'swf' or categoryName=='链接' or categoryName == '其他'  or categoryName == '图片':
                        print("🔗 {} <{}> ".format(categoryName, cellName))
                        print("⏳ 正在自动完成...")

                        shuake.info(cellId, moduleId, cellName, count)

                        print("🎉 {}任务完成!".format(categoryName))

                    else:
                        print("❓ {}程序无法识别, 请联系管理员！".format(categoryName))
                        continue
                    
                    time.sleep(3)
                continue
            
            else:
                print("❓ {}程序无法识别, 请联系管理员！".format(categoryName))
                continue
            
            time.sleep(3)
    # 职教云评论函数
    # 1评价  3问答  2笔记  4纠错 
    def comment():
        global cellList
        for i in [1, 3, 2, 4]:
            for cell in cellList:
                cellId = cell['cellId']
                
                if i == 1:
                    shuake.pinglun(cellId, 1, config['star'])
                else:
                    shuake.pinglun(cellId, i, 0)

                time.sleep(3)

    # 刷课件 评论
    if config['comment']:
        # 线程一刷课件
        t1 = threading.Thread(target=kejian)
        t1.setDaemon(True)
        t1.start()
        # 线程二刷评论
        t2 = threading.Thread(target=comment)
        t2.setDaemon(True)
        t2.start()

        t1.join()
        t2.join()
    else:
        kejian()

    print("\n🎉🎉🎉 你已完成了 <{}> 的所有课程！🎉🎉🎉".format(courseList[courseId]['courseName']))

 


    
