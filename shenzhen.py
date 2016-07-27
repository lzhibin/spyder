#coding=utf8
import urllib2
import random
import time
jgcs="http://www.szse.cn/main/disclosure/jgxxgk/jgcs/"   #监管信息公开--监管措施：
gsgg="http://disclosure.szse.cn/m/drgg.htm"              #上市公司信息--上市公司公告：
cxda="http://disclosure.szse.cn/m/drgg.htm"              #上市公司信息--上市公司诚信档案：
jjgg="http://disclosure.szse.cn/m/zqgg.htm"              #基金信息--基金公告/ETF公告：
zqgg="http://disclosure.szse.cn/m/zqgg.htm"              #债券信息--债券公告：
ywgg="http://www.szse.cn/main/disclosure/rzrqxx/ywgg/"   #融资融券信息--业务公告：
jyxx="http://www.szse.cn/main/disclosure/news/dzjy/"     #大宗交易信息--权益类证券大宗交易/债券大宗交易：
yysg="http://www.szse.cn/main/disclosure/news/yysg/"     #其他交易信息--要约收购：

class Spyder:
	def __init__(self,proxy_ip,try_time=5,sleep=0):
		self.proxy=proxy_ip
		self.sleep=sleep
		self.try_time=try_time
		self.headers = {
		'Connection' : 'keep-alive' ,
		'Accept' : '*/*' ,
		'User_Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36' ,
		}
		self.make_proxy()
	def make_proxy(self):
		ip=random.choice(self.proxy)
		self.opener=urllib2.build_opener(urllib2.HTTPHandler)
		proxy=urllib2.ProxyHandler({'http':'http://'+ip})
		self.opener.add_handler(proxy)
		print 'proxy change , new proxy ip:%s' % ip
	def get_page(self,url):
		req=urllib2.Request(url,headers=self.headers)
		for i in range(self.try_time):
			try:
				page=self.opener.open(req,timeout=i+1).read()
				time.sleep(self.sleep)
				print 'succeed to get %s (page length:%s)' % (url,len(page))
				return page
			except Exception, e :
				print 'No%s to get %s failed for %s ' % (str(i+1),url,e)
				self.make_proxy()
				continue
if __name__=='__main__':
	proxy_ip=['202.100.167.149:80']
	spyder=Spyder(proxy_ip)
	spyder.get_page('http://www.baidu.com')
	