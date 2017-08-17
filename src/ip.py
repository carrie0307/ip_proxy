# -*- coding: UTF-8 -*-
'''
	获取代理ip

	也作为对class的一个练习

'''
import Queue
import threading
import requests
import urllib2
from bs4 import BeautifulSoup
import re
import chardet
import time
import myException
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class IP():
	def __init__(self):
		self.ini_IP_q = Queue.Queue() # 初始获得的IP
		self.available_IP_q = Queue.Queue() # 验证后可用的IP
		self.date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
		#QUESTION: 验证后存在时间问题，有可能超过有效期  可用ip维持再某个数量？？？


	def get_66IP(self):
		'''
			功能：从66代理(http://www.66ip.cn)获取ip，将获取到的ip加入self.ini_IP_q队列
		'''
		for province in range(1, 33): # 各省页面
			page = 0
			flag = True
			while True:
				url = 'http://www.66ip.cn/areaindex_' + str(province) + '/' + str(page) + '.html'
				html = urllib2.urlopen(url).read()
				coding =  chardet.detect(html)
				html = html.decode(coding['encoding']) #  编码处理
				soup = BeautifulSoup(html,from_encoding="utf8")
				tables = soup.findAll('table')
				tab = tables[2]
				for tr in tab.findAll('tr'):
					tds = tr.findAll('td')
					if tds[0].string == 'ip': # 跳过列名
						continue
					# print str(tds[0].string) + ':' + str(tds[1].string)
					date = re.compile('\d+').findall(tds[4].string)
					date = str("-".join(date[:3]))
					if date == self.date:
						self.ini_IP_q.put(str(tds[0].string) + ':' + str(tds[1].string))
						# print str(tds[0].string) + ':' + str(tds[1].string)
					else:
						flag = False # 某省当天ip获取结束
						break
				if not flag: # 某省当天ip获取结束
					break


	def get_XiciIP(self):
		'''
			功能：从西刺代理(http://www.xicidaili.com/)获取ip，将获取到的ip加入self.ini_IP_q队列
		'''
		page = 1
		headers = {
					"Host": "www.xicidaili.com",
					"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
					"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
					"Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
					"Connection": "keep-alive"
					}
		while True:
			page = 1
			while page < 3: # 每次只抓前3页（太久的不需要去抓取）;每抓完sleep十分钟，避免被Ban
				flag = True
				url = 'http://www.xicidaili.com/nn/' + str(page)
				html = requests.get(url, headers=headers, timeout=15).text
				if html.find('block') != -1:
					time.sleep(600)
				soup = BeautifulSoup(html,from_encoding="utf8")
				table = soup.findAll('table',id='ip_list')[0]
				for tr in table.findAll('tr'):
					tds = str(tr.findAll('td'))
					tds = tds.split('[]')
					for td in tds:
						ip_port = str(re.compile(r'<td>(\d+\.\d+\.\d+\.\d+)</td>, <td>(\d+)</td>.*?').findall(td)) # 原始提取出的ip和port
						gap = ip_port.find(',')
						ip = ip_port[3:gap - 1]
						port = ip_port[gap + 3: -3]
						ip = ip + ":" + port
						date = str(re.compile(r'<td>(\d+-\d+-\d+) \d+:\d+</td>').findall(td))[2:10]
						if date == self.date[2:]:
							self.ini_IP_q.put(ip)
							# print [ip]
						else:
							flag = False # 当天ip获取结束
							break
					if not flag: # 当天ip获取结束
						page = page + 1
						break
			time.sleep(600)


	def goubanjia_get_IP(self, max_page):
		'''
			功能：从goubanjia代理(www.goubanjia.com)获取ip，将获取到的ip加入self.ini_IP_q队列

			说明：max_page用来限制抓取页数；尤其是update补充时，只抓取前2页的即可;
				ip181网站代理数量较多，因此用作update函数
		'''
		headers = {
				'Host':'www.goubanjia.com',
				'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
				'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8	'
		}
		ip_page = 1
		while ip_page < max_page: # 获取前10页的IP, 合计200个
			url = "http://www.goubanjia.com/index{page}.shtml"
			url = url.format(page = str(ip_page))
			html = requests.get(url, headers=headers, timeout=15).text
			soup = BeautifulSoup(html,from_encoding="utf8")
			ip_td = soup.findAll('td',{'class':'ip'})
			for td in ip_td:
				td = str(td)
				ini_ip = re.compile(r'<span[^>]*?>([^>]+?)</span>|<div style="display:[^>]*?inline-block;">([^>]+?)</div>').findall(td)
				ip = ''
				for index, temp in enumerate(ini_ip):
					temp = temp[0] if temp[0] != '' else temp[1]
					if index == len(ini_ip) - 1:
						ip = ip + ':' + temp
					else:
						ip = ip + temp
				self.ini_IP_q.put(ip)
			ip_page = ip_page + 1


	def ip181_get_IP(self, max_page):
		'''
			功能：从ip181代理(www.ip181.com/daili)获取ip，将获取到的ip加入self.ini_IP_q队列

			说明：max_page用来限制抓取页数；尤其是update补充时，只抓取前2页的即可;
				ip181网站代理数量较多，因此用作update函数
		'''
		ip_page = 1
		while ip_page < max_page: # 取前5页的ip，合计500个
			url = "http://www.ip181.com/daili/{page}.html"
			url = url.format(page = str(ip_page))
			html = urllib2.urlopen(url).read()
			coding =  chardet.detect(html)
			html = html.decode(coding['encoding']) #  编码处理
			soup = BeautifulSoup(html,from_encoding="utf8")
			table = soup.findAll('table',{'class':'table table-hover panel-default panel ctable'})[0]
			trs = table.findAll('tr')
			for tr in trs:
				tds = tr.findAll('td')
				if tds[2].string != '透明' and tds[0].string != 'IP地址':
					ip = tds[0].string + ':' + tds[1].string
					self.ini_IP_q.put(ip)
			ip_page = ip_page + 1


	def kuaidaili_get_IP(self):
		'''
			功能：从快代理(www.kuaidaili.com)获取ip，将获取到的ip加入self.ini_IP_q队列
		'''
		ip_page = 1
		while ip_page < 11: # 只有前10页合计100个ip可以爬取
			url = 'http://www.kuaidaili.com/ops/proxylist/{page}/'
			url = url.format(page = str(ip_page))
			html = urllib2.urlopen(url).read()
			soup = BeautifulSoup(html,from_encoding="utf8")
			table = soup.findAll('table',{'class':'table table-b table-bordered table-striped'})[2]
			trs = table.findAll('tr')
			for index, tr in enumerate(trs):
				if index != 0:
					tds = tr.findAll('td')
					if tds[2].string != '透明':
						ip = tds[0].string + ':' + tds[1].string
						self.ini_IP_q.put(ip)


	def verify_IP(self):
		'''
			功能：从self.ini_IP_q队列获取ip，验证ip有效性，将有效ip加入队列self.available_IP_q
		'''
		while True:
			IP = self.ini_IP_q.get(timeout=60)
			proxy = {'http': 'http://' + IP}
			# print "测试IP:" + str(proxy)
			try:
				res=requests.get("http://www.baidu.com",proxies=proxy,timeout=10)
				if res.content.find("百度一下")!=-1:
					print str(IP) + " is available ...\n"
					self.available_IP_q.put(proxy)
			except:
				pass


	def get_IP(self):
		'''
			功能：从队列self.available_IP_q获取可用proxy

			这里其实是模拟真实使用时候获取ip;实际使用时，通过self.available_IP_q获取
		'''
		try:
			if self.available_IP_q.empty():
				raise myException.available_IP_usedup()
			else:
				proxy = self.available_IP_q.get(timeout = 300)
				print str(proxy) + "   get ...\n"
				return proxy
		except myException.available_IP_usedup:
			print '可用ip已用完，需要补充 ... '


	def update_IP(self):
		'''
			# 功能：监控队列self.available_IP_q可用proxy数量，若不够，则更改self.date,获取更早一天的ip检测后使用
		'''
		while True:
			if self.available_IP_q.qsize() < 20:
				pass # 添加对新获取ip的处理


def run():
	ip = IP()
	print 'getting ips...'
	get_66IP = threading.Thread(target=ip.get_66IP)
	get_66IP.start()
	goubanjia_get_IP = threading.Thread(target=ip.goubanjia_get_IP,  args=(11))
	goubanjia_get_IP.start()
	ip181_get_IP = threading.Thread(target=ip.ip181_get_IP, args=(6))
	ip181_get_IP.start()
	# get_XiciIP = threading.Thread(target=ip.get_XiciIP)
	# get_XiciIP.start()
	print 'sleep ...'
	time.sleep(60)
	print 'verify ...'
	verify_IP_td = []
	print "the num of IP is " + str(ip.ini_IP_q.qsize())
	for _ in range(5):
		verify_IP_td.append(threading.Thread(target=ip.verify_IP))
	for td in verify_IP_td:
		td.start()
	time.sleep(120)
	print 'get ...'
	get_IP = threading.Thread(target=ip.get_IP)
	get_IP.start()

if __name__ == '__main__':
	run()
	# ip = IP()
	# ip.get_IP()
	# ip.get_66IP()
	# ip.get_XiciIP()
	# ip.verify_IP()
	# ip. goubanjia_get_IP()
	# ip.ip181_get_IP()
	# ip.kuaidaili_get_IP()
