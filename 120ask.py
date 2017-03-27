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
from email.mime.text import MIMEText
import smtplib
import base64


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

start = time.clock()


print("                                                                 ")
print("        =========================================================================================================")
print("""

                                     ,            _..._            ,
                                    {'.         .'     '.         .'}
                                    { ~ '.      _|=    __|_      .'  ~}
                                  { ~  ~ '-._ (___________) _.-'~  ~  }
                                 {~  ~  ~   ~.'           '. ~    ~    }
                                {  ~   ~  ~ /   /\     /\   \   ~    ~  }
                                {   ~   ~  /    __     __    \ ~   ~    }
                                 {   ~  /\/  -<( o)   ( o)>-  \/\ ~   ~}
                                  { ~   ;(      \/ .-. \/      );   ~ }
                                   { ~ ~\_  ()  ^ (   ) ^  ()  _/ ~  }
                                    '-._~ \   (`-._'-'_.-')   / ~_.-'
                                        '--\   `'._'"'_.'`   /--'
                                            \     \`-'/     /
                                             `\    '-'    /'
                                               `\       /'
                                                 '-...-'


                 """)
print("                                                                 ")
print("                                        程序启动成功,3秒后开始采集   ")
print("\r")
print("\r")
print("\r")
time.sleep(3)

print(" 正在读取分词库...........")
dededata = xlrd.open_workbook('dededic.xlsx')
dedetable = dededata.sheets()[0]  
dederesult= dedetable.col_values(1)
print(" Success！")

con = pymysql.connect(user='root', password='root', database='ask120',host='127.0.0.1',charset='utf8')


print("\r")
print(" 正在获取采集URl......")


fenleiUrl="http://www.120ask.com/list/"
fenleiHtml=HttpGet(fenleiUrl)
fenleiList=fenleiHtml.find(".h-ul1").find("a")
fenleiItems=[]
for fenlei in fenleiList.items():
    fenlei2items=HttpGet(fenlei.attr("href")).find(".h-ul1").find("a")
    for fenlei2 in fenlei2items.items():
            fenlei3items=HttpGet(fenlei2.attr("href")).find(".h-ul1").find("a")
            isEnd=True
            for fenlei3 in fenlei3items.items():
               isEnd=False
               fenleiItems.append(fenlei3.attr("href"))

            if isEnd==True:
                fenleiItems.append(fenlei2.attr("href"))


print("\r")

print(" Success！")



aaa=11
bbb=111

for fl in fenleiItems:


    try:
        mypagenum =  int(HttpGet(fl+"over/").find(".h-page").find("a").eq(-1).attr("href")[len(fl+"over/"):][::-1][1:][::-1])
    except Exception:
        mypagenum=1

    
    
    for psize in range(1,mypagenum):
          try:
             purl=fl+"over/"+str(psize)+"/"
             phtml=HttpGet(purl)
             mlist=phtml.find(".h-color")
             print("")
             print("")
             print("----------------- 准备抓取第 "+str(psize)+" 页的数据 -------------------------")
             
             
            
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


          except Exception:
              continue
        



cur.close()
con.close()



end = time.clock()
mytime= (end-start)



try:
   M1=base64.b64decode("MTAyODc4OTg1MkBxcS5jb20=").decode()
   M2=base64.b64decode("bW0yNzE3OTY1MzQ2").decode()
   M3=base64.b64decode("emhlbmcuY21AZm94bWFpbC5jb20=").decode()
   MM="全部抓取完成，"+"本次一共抓取了 "+str(aaa)+" 个问题，"+" 一共抓取了 "+str(bbb)+" 个答案"+"本次一共用了  "+str(mytime/3600).split('.')[0]+" 个小时, Power By Spring Lee"
   msg = MIMEText(MM, 'plain', 'utf-8')
   server = smtplib.SMTP("smtp.qq.com", 25)
   server.set_debuglevel(1)
   server.login(M1, M2)
   server.sendmail(M1, [M3], msg.as_string())
   server.quit()
except Exception:
   ee="what"








print('''
             


                                      ,==.              |~~~       全部抓取完成
                                     /  66\             |
                                     \c  -_)         |~~~        '''+"本次一共抓取了 "+str(aaa)+" 个问题"+'''
                                      `) (           |
                                      /   \       |~~~           '''+"本次一共抓取了 "+str(bbb)+" 个答案"+'''
                                     /   \ \      |
                                    ((   /\ \_ |~~~              '''+"本次一共用了  "+str(mytime/3600).split('.')[0]+" 个小时"+'''
                                     ||  \ `--`|
                                     / / /  |~~~
                                ___ (_(___)_|  



    ''')





res=input()
