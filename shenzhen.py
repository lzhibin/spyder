#coding=utf8
import urllib2
import random
import time
import os
import xlrd
import json
import re
from BeautifulSoup import BeautifulSoup
jgcs="http://www.szse.cn/main/disclosure/jgxxgk/jgcs/"   #监管信息公开--监管措施：
gsgg="http://disclosure.szse.cn/m/drgg.htm"              #上市公司信息--上市公司公告：
cxda="http://www.szse.cn/main/disclosure/bulliten/cxda/cfcfjl/"              #上市公司信息--上市公司诚信档案：
jjgg="http://disclosure.szse.cn/m/zqgg.htm"              #基金信息--基金公告/ETF公告：
zqgg="http://disclosure.szse.cn/m/zqgg.htm"              #债券信息--债券公告：
ywgg="http://www.szse.cn/main/disclosure/rzrqxx/ywgg/"   #融资融券信息--业务公告：
jyxx="http://www.szse.cn/main/disclosure/news/dzjy/"     #大宗交易信息--权益类证券大宗交易/债券大宗交易：
yysg="http://www.szse.cn/main/disclosure/news/yysg/"     #其他交易信息--要约收购：

class Spyder:
	def __init__(self,proxy_ip=None,max_count=300,try_time=5,sleep=0):
		self.count=1
		self.max_count=max_count
		self.proxy=proxy_ip
		self.sleep=sleep
		self.try_time=try_time
		self.headers = {'Connection' : 'keep-alive' ,'Accept' : '*/*' ,
		'User_Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36' ,
		}
		self._make_proxy()
	def _make_proxy(self):
		self.opener=urllib2.build_opener(urllib2.HTTPHandler)
		if not self.proxy is None:
			ip=random.choice(self.proxy)
			proxy=urllib2.ProxyHandler({'http':'http://'+ip})
			self.opener.add_handler(proxy)
			print 'proxy change , new proxy ip:%s' % ip
	def get_page(self,url):
		req=urllib2.Request(url,headers=self.headers)
		if self.count % self.max_count ==0:
			self._make_proxy()
		for i in range(self.try_time):
			self.count +=1
			try:
				page=self.opener.open(req,timeout=i+3).read()
				time.sleep(self.sleep)
				print 'succeed to get %s (page length:%s)' % (url,len(page))
				return page
			except Exception, e :
				print 'No%s to get %s failed for %s ' % (str(i+1),url,e)
				self._make_proxy()
				continue
	def parser_jgcs(self):
		link='http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=xlsx&CATALOGID=1800_jgxxgk&tab1PAGENUM=1&ENCODE=1&TABKEY=tab1'
		file('jgcs.xlsx','wb').write(self.get_page(link))
		excel=xlrd.open_workbook('jgcs.xlsx')
		table=excel.sheets()[0]
		for n in range(table.nrows-1):
			#不要行名
			print ' '.join(table.row_values(n+1))
	def parser_gsgg(self):
		link='http://disclosure.szse.cn//disclosure/fulltext/plate/szlatest_24h.js?ver='+time.strftime("%Y%m%d%H%M",time.localtime())
		res=self.get_page(link)
		res_list=json.loads(res.strip('\r\t\n')[17:-1].decode('gbk'))
		for item in res_list:
			print " ".join(item)
	def parser_cxda(self):
		page=self.get_page('http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=xlsx&CATALOGID=1759_cxda&tab1PAGENUM=1&ENCODE=1&TABKEY=tab1')
		file('cxda.xlsx','wb').write(page)
		excel=xlrd.open_workbook('cxda.xlsx')
		table=excel.sheets()[0]
		for n in range(table.nrows-1):
			print ' '.join(table.row_values(n+1))			
	def parser_jjgg(self):
		link='http://disclosure.szse.cn//disclosure/fulltext/plate/fundlatest_1y.js?ver='+time.strftime("%Y%m%d%H%M",time.localtime())
		res=self.get_page(link)
		res_list=json.loads(res.strip('\r\t\n')[17:-1].decode('gbk'))
		for item in res_list:
			print " ".join(item)	
	def parser_zqgg(self):
		link='http://disclosure.szse.cn//disclosure/fulltext/plate/szbondlatest_1m.js?ver='+time.strftime("%Y%m%d%H%M",time.localtime())
		res=self.get_page(link)
		res_list=json.loads(res.strip('\r\t\n')[17:-1].decode('gbk'))
		for item in res_list:
			print " ".join(item)
	def parser_ywgg(self):
		link='http://www.szse.cn/main/disclosure/rzrqxx/ywgg/index%s.shtml'
		index=""
		page=self.get_page(link % index)
		page_soup=BeautifulSoup(page)
		res_list=[]
		for item in page_soup.findAll('td',attrs={'class':'tdline2'}):
			res_list.append([item.a.get('href').split("'")[1],item.a.getText(),item.span.getText()[1:-1]])
		#res_list=re.findall('href="javascript:openArticle\(\'(.*?)\'\)',page)
		max_page=int(re.findall(u'共([0-9]*?)页'.encode('gbk'),page)[0])
		if max_page==1:
			return res_list
		else:
			for i in range(max_page-1):
				page=self.get_page(link % ('_'+str(i+1)))
				page_soup=BeautifulSoup(page)
				for item in page_soup.findAll('td',attrs={'class':'tdline2'}):
					res_list.append([item.a.get('href').split("'")[1],item.a.getText(),item.span.getText()[1:-1]])
		for i in res_list:
			self._download_ywgg(i)
			time.sleep(0.5)
		return res_list
	def parser_yysg(self):
		link_page='http://www.szse.cn/main/disclosure/news/yysg/'
		link1='http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=xlsx&CATALOGID=1266&ENCODE=1&TABKEY=tab1'
		link2='http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=xlsx&CATALOGID=1266&ENCODE=1&TABKEY=tab2'
		file('yysg1.xlsx','wb').write(self.get_page(link1))
		excel1=xlrd.open_workbook('yysg1.xlsx')
		table1=excel1.sheets()[0]
		file('yysg2.xlsx','wb').write(self.get_page(link2))
		excel2=xlrd.open_workbook('yysg2.xlsx')
		table2=excel2.sheets()[0]
		page=self.get_page(link_page)
		detail_link=re.findall("refreshData\('(.*?)'\)",page)
		for n1 in range(table1.nrows-1):
			print ' '.join(table1.row_values(n1+1)+[u'要约收购']+[detail_link[n1]])		
			self._download_yysg(table1.row_values(n1+1)+[u'要约收购']+[detail_link[n1]])
		for n2 in range(table2.nrows-1):
			print ' '.join(table2.row_values(n2+1)+[u'余约收购']+[detail_link[n1+n2+1]])	
			self._download_yysg(table2.row_values(n2+1)+[u'余约收购']+[detail_link[n1+n2+1]])
	
	def _download_jgcs(self,data):
		download_link='http://www.szse.cn/UpFiles/jgsy/%s'  #大部分公告有pdf文件，没有的话可能是几个文字
		file_name=data[4]
		if file_name.upper().endswith('PDF'):
			page=self.get_page(download_link % file_name)
		else:
			page=''
		return page
	def _download_gsgg(self,data):
		download_link='http://disclosure.szse.cn/m/%s'
		file_name=data[1]
		if file_name.endswith('PDF'):
			page=self.get_page(download_link % file_name)
		else:
			page=''
	def _download_cxda(self,data):
		link='http://www.szse.cn/UpFiles/cfwj/%s'
		file_name=data[6]
		if file_name.upper().endswith('PDF') or file_name.upper().endswith('DOC'):
			page=self.get_page(download_link % file_name)
		else:
			page=''
		return page
	def _download_jjgg(self,data):
		download_link='http://disclosure.szse.cn/m/%s'
		file_name=data[1]
		if file_name.endswith('PDF'):
			page=self.get_page(download_link % file_name)
		else:
			page=''
		return page
	def _download_zqgg(self,data):
		download_link='http://disclosure.szse.cn/m/%s'
		file_name=data[1]
		if file_name.endswith('PDF'):
			page=self.get_page(download_link % file_name)
		else:
			page=''	
		return res
	def _download_ywgg(self,data):
		def extra(html):
			soup=BeautifulSoup(html)
			s=soup.findAll('div',attrs={'class':'content'})[0]
			return s.getText()
		download_link='http://www.szse.cn%s'
		file_name=data[0]
		page=self.get_page(download_link % file_name)
		res=re.subn("\n"extra(page)
		return res
	def _download_yysg(self,data):
		def extra(html):
			table=[]
			soup=BeautifulSoup(html)
			s=soup.findAll('tr',attrs={'class':'cls-data-tr'})
			for item in s:
				table.append([i.text for i in item.findAll('td')])
			return table
		download_link='http://www.szse.cn%s'
		file_name=data[6]
		page=self.get_page(download_link % file_name)
		res=extra(page)
		return res
if __name__=='__main__':
	proxy_ip=['202.100.167.149:80']
	spyder=Spyder(proxy_ip)
	#spyder=Spyder()
	#spyder.get_page('http://www.baidu.com')
	spyder.parser_ywgg()
	

