import urllib.request
from pyquery import PyQuery as pq
import os
import time
import hashlib
import datetime
import pymysql
import hashlib
import xlrd
import jieba


def HttpGet(url):
    user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)'
    headers = { 'User-Agent' : user_agent }
    req = urllib.request.Request(url,headers = headers)
    response = urllib.request.urlopen(req)
    html=pq(response.read().decode("utf-8"))
    return html

 
def Md5(str):
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    return m.hexdigest() 

print("                                                                 ")
print("=================================================================")
print("                                                                 ")
print("          程序启动成功,3秒后开始采集   ")

time.sleep(3)

print("正在读取分词库...........")
dededata = xlrd.open_workbook('dededic.xlsx')
dedetable = dededata.sheets()[0]  
dederesult= dedetable.col_values(1)
print("分词库读取成功..........")



con = pymysql.connect(user='用户名', password='密码', database='你的数据库',host='你的数据库地址',charset='utf8')
cur = con.cursor()


fenleiUrl="http://www.120ask.com/list/"
fenleiHtml=HttpGet(fenleiUrl)
fenleiList=fenleiHtml.find(".h-ul1").find("a")
fenleiItems=[]
for fenlei in fenleiList.items():
    fenleiItems.append(fenlei.attr("href"))





for fl in fenleiItems:
    aaa=0
    bbb=0
    for psize in range(1,10):
        purl=fl+"over/"+str(psize)+"/"
        phtml=HttpGet(purl)
        mlist=phtml.find(".h-color")
        print("")
        print("")
        print("----------------- 准备抓取第"+str(psize)+"页的数据 -------------------------")
        time.sleep(3)
        
       
        for mitem in mlist.items():
            link = mitem.find(".q-quename").attr("href")
            content=HttpGet(link)

            title=content.find("#d_askH1").html()
            question=content.find("#d_msCon").find("p").html()[60:]
            classname=content.find(".b_route").find("a").eq(-1).find("span").html()
            department=content.find(".b_route").find("a").eq(-2).html();
            qaid=Md5(link)
            updatetime = datetime.datetime.now()
            
            cur.execute("select count(*) from question where qaid= %s",[qaid])
            rowresult = str(cur.fetchall())
            
            fenci=[]

            seg_list = jieba.cut(title)  
            jiebares=",".join(seg_list).split(',')
            for jb in jiebares:
                for dede in dederesult:
                    if jb==dede:
                        fenci.append(jb)

            keyword=','.join(fenci)

            if rowresult!="((0,),)":
                continue

            
            cur.execute('insert into question (title,question,keyword,classname,department,updatetime,qaid,url) values (%s,%s,%s,%s,%s,%s,%s,%s)', [title,question,keyword,classname,department,updatetime,qaid,link])
            con.commit()
            aaa+=1
            
            
            
            ans=content.find(".b_answerli")
            g=0
            for x in ans.items():
                g+=1
                if str(x.attr("class"))!="b_answerli":
                    continue
                state=0
                if g==1:
                   state=1

                username=x.find(".b_sp1").find("a").html()
                if username==None or username=="":
                    username="未知"
                nickname=x.find(".b_sp1").html()[-100:][0:2]
                gooduse=x.find(".b_answertl").find("span").eq(1).html()
                if "擅长" not in gooduse:
                    gooduse="未知"
                pp=x.find(".crazy_new").find("p").html()
               
                bingqing=pp[pp.find("病情分析：<br/>")+16:pp.find("指导意见：<br/>")]
                zhidao = pp[pp.find("指导意见：<br/>")+16:]
              
                cur.execute('insert into answer (answerer,profession,major,bingqing,zhidao,state,updatetime,query,qaid) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)',[username,nickname,gooduse,bingqing,zhidao,state,updatetime,0,qaid])
               
                con.commit()
                
                print("\n")
                print(" 入库成功:" + " ："+str(title))
                bbb+=1







cur.close()
con.close()



print("全部抓取完成")
res=input()
