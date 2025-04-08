import re
import tqdm
import random
# 这个库函数的访问为当用户点击视频时的访问的所有一系列必须的网络访问请求，通过调用这个包可以很方便的实现东软4s平台教育平台
# 的视频快速刷课，等待开源后，维护的伙伴们可以尝试加入发送m3u8文件访问时的跨度大小，或者减少不必要的网络访问来节省资源

# 添加记录访问
def Add_Record(arrangeId, calendarId, courseId, resId, studentId, classId, teacherId, termId, watchDuration,
               watchMaxProgress, watchPercent, Session,token):
    addrecord = Session.post(
        'http://sep.study.neuedu.com/se-tool-gateway/data/learning/learning-res-record/addLearningResRecord',
        json={
            'arrangeId': arrangeId,
            'calendarId': calendarId,
            'collegeId': "2263",
            'courseId': courseId,
            'isAssess': "1",
            'resId': resId,
            'resType': '1',
            'studentId': studentId,
            'teachClassId': classId,
            'teacherId': teacherId,
            'termId': termId,
            # 下面为时间 单位为秒
            # 观看期间（加载+视频观看时间）
            'watchDuration': watchDuration,
            # 仅观看视频时间
            'watchMaxProgress': watchMaxProgress,
            # 观看部分占总时间比值
            'watchPercent': watchPercent,
            # 仅观看时间
            'watchProgress': watchMaxProgress,
        },
        headers={
            'token': token,
            'dnt': '1',
            'host': 'sep.study.neuedu.com',
            'origin': 'http://sep.study.neuedu.com',
            'referer': 'http://sep.study.neuedu.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
        }
    )


# 更新日志文件
def Updata_log(arrangeId, calendarId, courseId, resId, studentId, classId, termId, studentNum, myname, costTime,
               lastTime, Session,token):
    addrecordlog = Session.post(
        'http://sep.study.neuedu.com/se-tool-gateway/data/learning/learning-res-record-log/updateLearningResRecordLog',
        json={
            'arrangeId': arrangeId,
            'calendarId': calendarId,
            'classId': classId,
            'collegeId': "2263",
            # 花费时间 单位为秒
            'costTime': costTime,
            'courseId': courseId,
            # 视频观看最后的时间 单位为秒
            'lastTime': lastTime,
            'resId': resId,
            'resType': '1',
            'studentId': studentId,
            'studentName': myname,
            'studentNum': studentNum,
            'termId': termId,
        }, headers={
            'token': token,
            'dnt': '1',
            'host': 'sep.study.neuedu.com',
            'origin': 'http://sep.study.neuedu.com',
            'referer': 'http://sep.study.neuedu.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
        })

def get_learn_progress(Session,url , token,arrangeId,calendarId,resId,teachClassId,teacherId):
    res = Session.post(url, headers={
            'token': token,
            'dnt': '1',
            'host': 'sep.study.neuedu.com',
            'origin': 'http://sep.study.neuedu.com',
            'referer': 'http://sep.study.neuedu.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
        },json={
        'arrangeId':arrangeId,
        'calendarId':calendarId,
        'resId':resId,
        'teachClassId':teachClassId,
        'teacherId':teacherId
    })

# 实现加入日志文件的访问
def add_log(arrangeId, calendarId, courseId, resId, studentId, classId, termId, studentNum, myname, costTime, lastTime,
            Session,token):
    addrecordlog = Session.post(
        'http://sep.study.neuedu.com/se-tool-gateway/data/learning/learning-res-record-log/addLearningResRecordLog',
        json={
            'arrangeId': arrangeId,
            'calendarId': calendarId,
            'classId': classId,
            'collegeId': "2263",
            # 花费时间 单位为秒
            'costTime': costTime,
            'courseId': courseId,
            # 视频观看最后的时间 单位为秒
            'lastTime': lastTime,
            'resId': resId,
            'resType': '1',
            'studentId': studentId,
            'studentName': myname,
            'studentNum': studentNum,
            'termId': termId,
        }, headers={
            'token': token,
            'dnt': '1',
            'host': 'sep.study.neuedu.com',
            'origin': 'http://sep.study.neuedu.com',
            'referer': 'http://sep.study.neuedu.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
        })
def getBiz(Session,url,token,arrangeId,calendarId,resId,classId,teacherId):
    res = Session.post(url, headers={
            'token': token,
            'dnt': '1',
            'host': 'sep.study.neuedu.com',
            'origin': 'http://sep.study.neuedu.com',
            'referer': 'http://sep.study.neuedu.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
        },json={
        'arrangeId':arrangeId,
        'calLoc':'3',
        'calendarId':calendarId,
        'classId':classId,
        'collegeId':"2263",
        'resId':resId,
        'teacherId':teacherId
    })

# 访问ts结尾的视频请求（我不知道不访问这个请求会不会对刷课有影响，为了项目顺利推进我加上了）
def open_t000x(tsname, Session):
    res = Session.get(fr'http://videoslice.neumooc.com/2024---10/10---d5dcae39f44248f19b20923e46bcc9b1/low/{tsname}',
                      headers={
                          'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
                      })
def getappbucket(Session , token):
    res = Session.get('http://sep.study.neuedu.com/console/getAppBucketIndexInfo?applicationLogo=SE',headers={
            'token': token,
            'dnt': '1',
            'host': 'sep.study.neuedu.com',
            'origin': 'http://sep.study.neuedu.com',
            'referer': 'http://sep.study.neuedu.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
        })

# 这段代码完整的实现了m3u8文件到视频段文件ts的访问
def Send_Log_And_Upadte(Session, m3u8name, arrangeId, calendarId, classId, courseId, resId, studentId, studentNum,
                        termId, teacherId, myname,token):
    with open(f'm3u8s/{m3u8name}','r') as f:
        m3u8filetxt = f.read()
    #前置访问

    getappbucket(Session,token)

    informations = m3u8filetxt.split('\n')

    if informations[0]!= '#EXTM3U':
        print('m3u8文件格式不正确,可能是网站出现了问题')
    else:
        # 提取ts视频文件的关键信息，例如时长和名字
        new_informations = informations[5:-2]
        # print(new_informations)
        getBiz(Session,'http://sep.study.neuedu.com/se-tool-gateway/biz/learning/learning_video_test_biz/getBizLearningVideoTestStu',token,arrangeId,calendarId,resId,classId,teacherId)
        # 发送开始观看的请求
        get_learn_progress(Session,'http://sep.study.neuedu.com/se-tool-gateway/data/learning/learning-res-record/getLearningProgress',token,arrangeId,calendarId,resId,classId,teacherId)
        # 首先访问的两个请求，将需要提交的时间信息置零
        add_log(arrangeId,calendarId,courseId,resId,studentId,classId,termId,studentNum,myname,0,0,Session,token)
        Add_Record(arrangeId,calendarId,courseId,resId,studentId,classId,teacherId,termId,2,0,0,Session,token)
        Updata_log(arrangeId,calendarId,courseId,resId,studentId,classId,termId,studentNum,myname,0,0,Session,token)
        # 预先遍历一边用来计算总时长
        vedio_times = 0
        for i in range(0, len(new_informations), 2):
            time = float(re.findall(r'#EXTINF:([\d\.]+)', str(new_informations[i]))[0])
            vedio_times += time

        # 通过遍历ts视频文件段来分段提交日志文件和更新日志文件
        cost_time = 0
        A = 0
        for i in tqdm.tqdm(range(0, len(new_informations), 2), desc='开始发送阅读请求'):
            time = float(re.findall(r'#EXTINF:([\d\.]+)', str(new_informations[i]))[0])
            name = new_informations[i + 1]
            # 访问视频片段
            open_t000x(name, Session)
            # 计算时间,总消耗时间、和消耗视频占比
            cost_time += time
            # 随机增加花费时间
            all_time = cost_time + random.randint(2, 4)
            percent_time = (cost_time / vedio_times)*100

            # 用于检查代码，无意义
            A = percent_time

            # 更新
            Updata_log(arrangeId, calendarId, courseId, resId, studentId, classId, termId, studentNum, myname, cost_time,
                       cost_time, Session,token)
            Add_Record(arrangeId, calendarId, courseId, resId, studentId, classId, teacherId, termId, all_time, cost_time,
                       percent_time, Session,token)






