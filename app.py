import json
import ddddocr
from requests import session
import encode
import re
import traceback
# 这个是自定义包
import watch_vedio_req
import random
import os
from datetime import datetime



# 初始化session
Session = session()


# 此方法用于后获取登录时的uuid
def get_image_uuid():
    res = Session.get('http://study.neuedu.com/cloud-service/login/captchaImage').text
    res = json.loads(res)
    code = res['img']
    uuid = res["uuid"]
    # 将读取的验证码图片base64编码转化为图片
    image = ddddocr.base64_to_image(code)
    # 加载自己训练的ocr模型专门识别东软4s验证码
    result = ddddocr.DdddOcr(show_ad=False,det=False, ocr=False,import_onnx_path='models/101file_0.875_222_2000_2024-10-01-23-52-44.onnx', charsets_path="models/charsets.json")
    # 开始识别验证码
    inf = result.classification(image)
    # 返回 登录需要的uuid、以及识别后的原始字符串
    return uuid,inf

# 发送登录请求然后保存cookies和获取toekn，token是登录访问的必须的令牌
def send_log_and_get_token(uuid,password,checknumber,myid_nue):
    res = Session.post('http://study.neuedu.com/cloud-service/login/login',json={"username":myid_nue,"password":password,"role":"","collegeCode":"12636","uuid":uuid,"code":checknumber})
    txt = json.loads(res.text)
    return txt["data"]["access_token"]

# 向目标网址发起请求然后注入token
def get_yesr_id(aim_url,access_token):
    list_res = Session.get(aim_url,
                               headers={'referer':aim_url,'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
                                        # 通过此方法注入获取的token
                                        'Authorization': f'Bearer {access_token}',
                                        }
                               ).text
    yearid = json.loads(list_res)["data"][-1]['schoolYearId']
    return yearid

# 获取个人id，这里获取的时代码个人id，不是纯数字，是个字符串
def get_usernameid(token):
    res = Session.get('http://study.neuedu.com/cloud-service/user/system/reportsBox/newReport?userId=142414',headers={'referer':'http://study.neuedu.com/cloud-service/user/system/reportsBox/newReport?userId=142414','user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
                                        # 通过此方法注入获取的token
                                        'Authorization': f'Bearer {token}',
                                        }).text

    usernameid = json.loads(res)[0]["userName"]
    return usernameid

# 获取课程具体信息
def write_course_information(data:dict,usernameid:str):
    informations = []
    for i in data:
        tem = []
        print("科目："+i['teachCourse']['courseName'],"教师："+i['teacherName'],'课程编号：'+i['teachCourse']['courseCode'])
        tem.append(i['teachCourse']['courseCode'])
        tem.append(i['teachCourse']['teachCourseId'])
        tem.append(usernameid)
        tem.append(i['teacherId'])
        tem.append(i['teachArrangementGroupId'])
        # 将每一课的信息写入informations，列表信息是二维信息[[],[]]
        informations.append(tem)
    return informations


# 通过输入的课程信息来访问细节
def get_detial_information_in_url(token,courseCode,courseId,currentUserName,teacherUserName,teachingArrangementId):

    # 获取信息appid,指的是课程教学板块的id
    appid_url_info = Session.get('http://study.neuedu.com/cloud-service/user/system/home/getNormalUserHomePageInfos',
                                 headers={
                                     'referer':'http://study.neuedu.com/personHome',
                                     'Authorization': f'Bearer {token}',
                                     'host':'study.neuedu.com'
                                 }).text
    # 这里是教学板块的id
    appid = json.loads(appid_url_info)[1]['appId']

    need_url = Session.get(fr'http://study.neuedu.com/cloud-service/user/system/home/getAppEntry?appId={appid}',headers={'Authorization': f'Bearer {token}','host':'study.neuedu.com','referer':'http://study.neuedu.com/personHome'})
    # 返回关键网址作为下一个访问的请求体
    key = json.loads(need_url.text)['data']['url']
    res = Session.post('http://sep.study.neuedu.com/se-tool-gateway/biz/course/course_biz/getCourseSkipUrl',
                       headers={'referer': 'http://study.neuedu.com/',
                                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
                                # 通过此方法注入获取的token
                                'Authorization': f'Bearer {token}',
                                },
                       json={
                           'collegeCode':"12636",
                           'courseCode':courseCode,
                           'courseId':courseId,
                           'currentUserName':currentUserName,
                           'teacherUserName':teacherUserName,
                           'teachingArrangementId':teachingArrangementId,
                           'url':key
                       }).text
    # 返回一个充满信息的网址，这里包括了课程代号什么的，反正很多啦
    return json.loads(res)["data"]

# 获取指定学期的课程
def get_year_course(data:str,oringi_url:str,token):
    res = Session.get(oringi_url+data,headers={'referer':oringi_url,'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
                                        # 通过此方法注入获取的token
                                        'Authorization': f'Bearer {token}',
                                        }).text
    list_res = json.loads(res)["data"]
    return list_res



# 处理原始的验证码数据，然后通过eval函数执行算数然后返回结果
def process_check(inf:str):
    inf_new = inf.split('=')[0]
    inf_new_1 = inf_new.replace('c','/').replace('x','*')
    result = int(eval(inf_new_1))
    return result

# 输入需要的课程号
def goto_write_fucking_course():
    name = input("输入想要访问的课程代号(英文逗号分开,目前仅支持单次访问)：")
    course = name.split(",")
    return course

# 通过输入的想要获取课程的列表来从总的信息列表里获取想要的信息构成新的列表，方便后面可以访问你需要的网站或者
# 方便做多线程访问课程
def translate_name_to_new_list(wanna_list , detial_list):
    oederlist = []
    for item in wanna_list:
        for detia in detial_list:
            if detia[0] == item:
                oederlist.append(detia)
            else:
                continue
    return oederlist

# 找出并运行跳转的网页
def run_to_new_urls(token , need_list):
    urls_list = []
    for item in need_list:
        res = get_detial_information_in_url(token,item[0],item[1],item[2],item[3],item[4])
        urls_list.append(res)
    return urls_list

# 这里是做对于课程的某一个课的孩子列表识别，因为任务很多，不只是MP4，这里后期扩展更多的完成作业的代码
def Get_And_Finishi_Task(Childrens:list):
    for item in Childrens:
        if 'mp4' in str(item['resName']):
            pass

# 旨在模拟平台发送记录用户阅读
def CheatToWrite(token,arrangeId,calLoc,calendarId,resId,teachClassId,teacherId,courseId,userId,termId,restype):
    # # 检查是否打开网页
    res_open = Session.post(
        'http://sep.study.neuedu.com/se-tool-gateway/data/learning/learning-cal-res-ctrl/checkResOpen',
        headers={'token': token}, json={
            'arrangeId': arrangeId,
            'calLoc': calLoc,
            'calendarId': calendarId,
            'collegeId': "2263",
            'resId': resId,
            'teachClassId':teachClassId,
            'teacherId': teacherId,
        })

    # add记录，还未知是否为可解决视频记录无法开始
    add_res = Session.post('http://sep.study.neuedu.com/se-tool-gateway/data/learning/learning/visit/log/add',
                           headers={'token': token}, json={
            'arrangeId': arrangeId,
            'collegeId': "2263",
            'courseId': courseId,
            'teachClassId': teachClassId,
            'userId': userId,
        })

    save_res = Session.post(
        'http://sep.study.neuedu.com/se-tool-gateway/data/learning/learning-res-record/saveLearningTimes',
        headers={'token': token}, json={
            'arrangeId': arrangeId,
            'calLoc': calLoc,
            'calendarId': calendarId,
            'courseId': courseId,
            'isAssess': '0',
            'packageId': "0",
            'resId': resId,
            'resType': restype,
            'teachClassId': teachClassId,
            'teacherId': teacherId,
            'termId': termId,
        })

# 访问并且访问重定向网页
def goto_singel_course_detial(token,url,mycode,myname,myid_nue):

    # 从返回的网页链接解析新的数据用于最后的访问
    # 这里用于提取那个充满信息的网址的需要的信息
    code = re.findall('code=(.*?)&',url)[0]
    teachingArrangementId = re.findall('teachingArrangementId=(.*?)&',url)[0]
    teacherId = re.findall('teacherId=(.*?)&',url)[0]
    teachingClassId = url.split('=')[-1]


    # 重定向1获取新token，这里还是旧的token
    res1 = Session.get(fr'http://sep.study.neuedu.com/se-tool-gateway/data/user/systemUser/getTokenFromSso?code={code}',
                        headers={'referer': 'http://sep.study.neuedu.com/',
                                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
                                 # 通过此方法注入获取的token
                                 'token':token,
                                 'host':'sep.study.neuedu.com',
                                 'dnt':'1'
                                 },
                        ).text

    # 获取新的token
    new_token = json.loads(res1)['accessToken']

    # 获取我的id，这里才是数字id
    myid = Session.get(f'http://sep.study.neuedu.com/se-tool-gateway/data/user/systemUser/getTokenFromSso?code={mycode}',headers={'token':new_token}).text
    myid_number = json.loads(myid)['userId']



    # 返回课程详情
    res3 = Session.post('http://sep.study.neuedu.com/se-tool-gateway/biz/learning/learning_stu_biz/getStuCalVO',
                        headers={
                            'token':new_token,
                            'dnt':'1',
                            'host':'sep.study.neuedu.com',
                            'origin':'http://sep.study.neuedu.com',
                            'referer':'http://sep.study.neuedu.com/',
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
                        },
                        json={
                            'arrangeId':teachingArrangementId,
                            'collegeId':"2263",
                            'teacherId':teacherId,
                            'teachingClassId':teachingClassId,
                            'teachingType':"1"
                        }
                        ).text
    # 获得课程信息
    data = json.loads(res3)["data"]

    if data:

        for item in data:
            # print(item)
            if item['count'] != 0:
                print(item['calendarName'] , f"有{item['count']}个任务")

                # 访问详细的课程信息（课前、课中、课后）
                courseid1 = item['courseId']


                # task_list = json.loads(task_list)
                # 获取课后任务所有的孩子
                res = Session.post('http://sep.study.neuedu.com/se-tool-gateway/biz/learning/learning_stu_biz/getStudentCalRes',json={
                    'calendarId' : item['calendarId'],
                    'courseId' : item['courseId'],
                    'arrangeId' : teachingArrangementId,
                    'teachClassId' : teachingClassId,
                    'userId' : teacherId
                },
                                   headers={
                                       'token': new_token,
                                       'dnt': '1',
                                       'host': 'sep.study.neuedu.com',
                                       'origin': 'http://sep.study.neuedu.com',
                                       'referer': 'http://sep.study.neuedu.com/',
                                       'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
                                   }
                                   ).text
                res = json.loads(res)

                # 查找任务在哪个板块（课前、课中、课后）
                dirct = 0
                for item in res['data']:
                    if item['children'] == None:
                        dirct += 1

                    else:
                        text = res['data'][dirct]['children']

                        # 关于指针的递归，只要酝运行过条件，就会加一,为了应孩子多任务的情况
                        zhizhen = 0
                        for string_dic in text:
                            if 'mp4' in string_dic['resName']:
                                # 找到指定的children字典
                                aim_chilrdren = text[zhizhen]

                                resid = aim_chilrdren['resId']
                                calloc1 = aim_chilrdren['calLoc']
                                calendarId12 = aim_chilrdren['calendarId']
                                termId = aim_chilrdren['termId']
                                restype = aim_chilrdren['resType']

                                CheatToWrite(new_token, teachingArrangementId, calloc1, calendarId12, resid,
                                             teachingClassId, teacherId, courseid1, myid, termId,restype)

                                # 获取term字符串
                                term = Session.get(
                                    fr'http://sep.study.neuedu.com/se-tool-gateway/data/learning/learning-calendar/findOneByCalendarId?calendarId={text[zhizhen]["calendarId"]}',
                                    headers={
                                        'token': new_token,
                                        'dnt': '1',
                                        'host': 'sep.study.neuedu.com',
                                        'origin': 'http://sep.study.neuedu.com',
                                        'referer': 'http://sep.study.neuedu.com/',
                                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
                                    }).text
                                termid = json.loads(term)['termId']

                                # 获取后面网站访问的必要字符串
                                video_code = Session.post(
                                    'http://sep.study.neuedu.com/se-tool-gateway/data/resource/resource/getResourceByTreeId',
                                    json={
                                        'collegeId': "2263",
                                        'resourceTreeId': resid
                                    }, headers={
                                        'token': new_token,
                                        'dnt': '1',
                                        'host': 'sep.study.neuedu.com',
                                        'origin': 'http://sep.study.neuedu.com',
                                        'referer': 'http://sep.study.neuedu.com/',
                                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
                                    }).text
                                open_vedio_url = json.loads(video_code)['eid']
                                # print(open_vedio_url)
                                # 获取视频地址
                                video = Session.get(
                                    f'http://sep.study.neuedu.com/slices/getFilePreViewByEid?eId={open_vedio_url}&source=SE',
                                    headers={
                                        'token': new_token,
                                        'dnt': '1',
                                        'host': 'sep.study.neuedu.com',
                                        'origin': 'http://sep.study.neuedu.com',
                                        'referer': 'http://sep.study.neuedu.com/',
                                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
                                    }).text
                                url = 'http:' + json.loads(video)['data']
                                # 这里找到了中等画质视频的网址（还可以换成低画质的）
                                new_url = url.replace('index', 'original/playlist_original')

                                # 访问指定画质视频的ts文件（很多段的那种哟）
                                ors = Session.get(new_url, headers={
                                    'dnt': '1',
                                    'referer': 'http://sep.study.neuedu.com/',
                                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
                                }).content
                                # 随机生成一个名字，防止重名，方便后期加入多线程
                                name_ocr = 'ors' + str(random.randint(1, 10000)) + 'm3u8'
                                with open(f'm3u8s/{name_ocr}', 'wb') as f:
                                    f.write(ors)

                                # 执行视频完成指令
                                watch_vedio_req.Send_Log_And_Upadte(Session, name_ocr, teachingArrangementId,
                                                                    aim_chilrdren['calendarId'], teachingClassId,
                                                                    aim_chilrdren['courseId'],
                                                                    myname=myname, resId=resid, studentId=myid_number,
                                                                    studentNum=myid_nue, teacherId=teacherId,
                                                                    termId=termid, token=token)
                                zhizhen += 1


                            elif 'doc' in string_dic['resName']:

                                # 找到指定的children字典
                                aim_chilrdren = text[zhizhen]

                                resid = aim_chilrdren['resId']
                                calloc1 = aim_chilrdren['calLoc']
                                calendarId12 = aim_chilrdren['calendarId']
                                termId = aim_chilrdren['termId']
                                restype = aim_chilrdren['resType']

                                # # 检查是否打开网页
                                CheatToWrite(new_token, teachingArrangementId, calloc1, calendarId12, resid,
                                             teachingClassId, teacherId, courseid1, myid, termId,restype)

                                # 前面需要加上上一个页面的所有验证机制
                                # 这里已经是doc文档页面
                                se = Session.get(
                                    'http://sep.study.neuedu.com/console/getAppBucketIndexInfo?applicationLogo=SE',
                                    headers={'token': new_token,
                                             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
                                             'referer': 'http://sep.study.neuedu.com/',
                                             'host': 'sep.study.neuedu.com'
                                             }).text
                                se_js = json.loads(se)['data']
                                bucketName = se_js['bucketName']
                                indexName = se_js['indexName']

                                opendoc = Session.get(
                                    fr'http://sep.study.neuedu.com/se-tool-storage//content/s3/previewObject?bucketName={bucketName}&index={indexName}&eid={code}',
                                    headers={'token': new_token,
                                             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
                                             'referer': 'http://sep.study.neuedu.com/',
                                             'host': 'sep.study.neuedu.com'
                                             })

                                if opendoc.status_code == 200:
                                    print('doc文档阅读成功')
                                else:
                                    print('doc文档阅读失败')
                                zhizhen += 1

                            elif 'ppt' in string_dic['resName']:
                                # 找到指定的children字典
                                aim_chilrdren = text[zhizhen]

                                resid = aim_chilrdren['resId']
                                calloc1 = aim_chilrdren['calLoc']
                                calendarId12 = aim_chilrdren['calendarId']
                                termId = aim_chilrdren['termId']
                                restype = aim_chilrdren['resType']

                                # 检查是否打开网页
                                CheatToWrite(new_token, teachingArrangementId, calloc1, calendarId12, resid,
                                             teachingClassId, teacherId, courseid1, myid, termId,restype)

                                getbuck = Session.get('http://sep.study.neuedu.com/console/getAppBucketIndexInfo?applicationLogo=SE',
                                                      headers={'token': new_token,
                                             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
                                             'referer': 'http://sep.study.neuedu.com/',
                                             'host': 'sep.study.neuedu.com'
                                             },).text

                                se_js = json.loads(getbuck)['data']
                                bucketName = se_js['bucketName']
                                indexName = se_js['indexName']

                                opendoc = Session.get(
                                    fr'http://sep.study.neuedu.com/se-tool-storage//content/s3/previewObject?bucketName={bucketName}&index={indexName}&eid={code}',
                                    headers={'token': new_token,
                                             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
                                             'referer': 'http://sep.study.neuedu.com/',
                                             'host': 'sep.study.neuedu.com'
                                             })

                                if opendoc.status_code == 200:
                                    print('ppt文档阅读成功')
                                else:
                                    print('ppt阅读失败')
                                zhizhen += 1


                            else:
                                print(" " + fr'暂未支持此类：{string_dic["resName"].split(".")[-1]}的任务：' + str(
                                    string_dic["resName"]))
                                zhizhen += 1
                        dirct += 1







            else:
                print(item['calendarName'], "没有任务")


        # print(task_list)
        # 访问任务列表
    else:
        print("课程内容为空")

# 获取我的id
def get_myid(token:str):
    res = Session.get('http://study.neuedu.com/cloud-service/user/system/home/getNormalUserHomePageInfos',headers={'referer':'http://study.neuedu.com/personHome','user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
                                        # 通过此方法注入获取的token
                                        'Authorization': f'Bearer {token}',
                                        }).text
    appid = json.loads(res)[1]['appId']
    code = Session.get(fr'http://study.neuedu.com/cloud-service/user/system/home/getAppEntry?appId={appid}',headers={'referer':'http://study.neuedu.com/personHome','user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
                                        # 通过此方法注入获取的token
                                        'Authorization': f'Bearer {token}',
                                        }).text
    urls = json.loads(code)['data']['url']
    code = re.findall(r'code=([^&]*)' , str(urls))[0]
    return code

# 主函数，包含了所有的运行过程代码
def main():

    temporary_info = ''



    while True:

        if os.path.exists('user_info.json'):
            with open('user_info.json', 'r') as f:
                dic = f.read()

            information = json.loads(dic)
            names = information.keys()

            if temporary_info == '':
                myname = input("请输入您的姓名：")
                temporary_info = myname
            else:
                myname = temporary_info

            if myname  in names:
                myid_nue = information[myname][1]
                mypassword = information[myname][2]
                print('欢迎您，' + myname)

            else:
                print('本地未记录您的信息')
                input_informations = input('请依次输入学号、密码，以英文逗号隔开：')
                information_list = input_informations.split(',')
                information_list.insert(0,myname)
                information[information_list[0]] = information_list
                with open('user_info.json', 'w') as f:
                    f.write(json.dumps(information))

                myname = information_list[0]
                myid_nue = information_list[1]
                mypassword = information_list[2]


        else:
            dic = {}
            print('本地还未记录任何的账号信息')
            informations = input('请依次输入姓名、学号、密码，以英文逗号隔开：')
            information_list = informations.split(',')
            dic[str(information_list[0])] = information_list
            with open('user_info.json', 'w') as f:
                json.dump(dic, f)

            myname = information_list[0]
            myid_nue = information_list[1]
            mypassword = information_list[2]


        try:
            # 获取uuid
            uuid, inf = get_image_uuid()
            # 替换识别的验证码并且参与计算结果
            result = process_check(inf)
            # 加密密码
            encode_password = encode.run_encode(mypassword)
            # 发送登录请求获取token标记用户
            token = send_log_and_get_token(uuid, encode_password, result, myid_nue)
            # 获取我的id之路的code
            code = get_myid(token)
            # 获取最新的学期的学期编号
            yearid = get_yesr_id('http://study.neuedu.com/cloud-service/businessmasterdata/school-year/student/list', token)
            # 根据获取的学期编号访问这学期的所用课程
            course_of_list = get_year_course(yearid,
                                             'http://study.neuedu.com/cloud-service/businessmasterdata/teach-arrangement/student/list?schoolYearId=',
                                             token)
            # 获取用户名id的代码编号
            usernameid = get_usernameid(token)
            # 将指定的多个关键信息放入列表后返回
            detial_lis = write_course_information(course_of_list, usernameid)
            # 输入指定的课程构成列表

            wanna_course_list = goto_write_fucking_course()


            # 输入想要爬取的课程和总的信息课程列表来转化为仅需要的列表
            need_List = translate_name_to_new_list(wanna_course_list, detial_lis)
            # 根据获取到的需要访问的信息列表然后使用方法来访问
            url_list = run_to_new_urls(token, need_List)




            # 这里是手动获取第一个网页和第一个课程的信息，后续需要做一个多线程同时运行这个代码！
            # 获取需要爬取的课程

            goto_singel_course_detial(token, url_list[0], code, myname, myid_nue)


            print('执行成功')

            if_countinue = input('是否继续还是切换用户信息？y/n/change:')
            if if_countinue == 'n':
                break
            elif if_countinue == 'change':
                temporary_info = ''




        except KeyError:
            print('error:可能是密码或者识别出错误，请重试')
            print(traceback.format_exc())


if __name__ == '__main__':
    main()



