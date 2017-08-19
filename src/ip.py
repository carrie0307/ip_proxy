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


ini_IP_q = Queue.Queue() # 初始获得的IP
available_IP_q = Queue.Queue() # 验证后可用的IP
std_date = time.strftime('%Y-%m-%d',time.localtime(time.time())) # 当日日期
verify_IP_td = [] # 验证ip有效性的线程集合
get_IP_td = [] # 获取ip线程的集合


class IP_Getter():
	global ini_IP_q
	global available_IP_q
	global std_date

	@staticmethod
	def get_66IP():
		'''
		从66代理(http://www.66ip.cn)获取ip，将获取到的ip加入ini_IP_q队列
		:ini_IP_q 初始获得ip的队列

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
					if date == std_date:
						ini_IP_q.put(str(tds[0].string) + ':' + str(tds[1].string))
						# print str(tds[0].string) + ':' + str(tds[1].string)
					else:
						flag = False # 某省当天ip获取结束
						break
				if not flag: # 某省当天ip获取结束
					break

	@staticmethod
	def get_XiciIP():
		'''
		功能：从西刺代理(http://www.xicidaili.com/)获取ip，将获取到的ip加入ini_IP_q队列
		:ini_IP_q 初始获得ip的队列
		'''
		page = 1
		headers = {
					"Host": "www.xicidaili.com",
					"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
					"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
					"Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
					"Connection": "keep-alive"
					}
		while page < 2: # 每次只抓前3页（太久的不需要去抓取）;每抓完sleep十分钟，避免被Ban
			print 'page: ' + str(page)
			flag = True
			url = 'http://www.xicidaili.com/nn/' + str(page)
			html = requests.get(url, headers=headers, timeout=15).text
			# print html
			if html.find('block') != -1:
				print 'be banned ...'
				break
			soup = BeautifulSoup(html,from_encoding="utf8")
			table = soup.findAll('table',id='ip_list')[0]
			# QUESTION: 这里需要改以下，建议改正则来匹配（class="odd" 和 class=“” 两种同时匹配soup有误
			for tr in table.findAll('tr'):
				print tr
				tds = str(tr.findAll('td'))
				tds = tds.split('[]')
				for td in tds:
					ip_port = str(re.compile(r'<td>(\d+\.\d+\.\d+\.\d+)</td>, <td>(\d+)</td>.*?').findall(td)) # 原始提取出的ip和port
					gap = ip_port.find(',')
					ip = ip_port[3:gap - 1]
					port = ip_port[gap + 3: -3]
					ip = ip + ":" + port
					date = str(re.compile(r'<td>(\d+-\d+-\d+) \d+:\d+</td>').findall(td))[2:10]
					print date
					if date == std_date[2:]:
						print ip
						ini_IP_q.put(ip)
						# print [ip]
					else:
						flag = False # 当天ip获取结束
						break
				if not flag: # 当天ip获取结束
					page = page + 1
					break

	@staticmethod
	def goubanjia_get_IP(max_page):
		'''
		功能：从goubanjia代理(www.goubanjia.com)获取ip，将获取到的ip加入ini_IP_q队列

		说明：max_page用来限制抓取页数；尤其是update补充时，只抓取前2页的即可;
			ip181网站代理数量较多，因此用作update函数

		:ini_IP_q 初始获得ip的队列
		:max_page 抓取的最大页数
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
				ini_IP_q.put(ip)
			ip_page = ip_page + 1


	@staticmethod
	def ip181_get_IP(max_page):
		'''
		功能：从ip181代理(www.ip181.com/daili)获取ip，将获取到的ip加入ini_IP_q队列

		说明：max_page用来限制抓取页数；尤其是update补充时，只抓取前2页的即可;
			ip181网站代理数量较多，因此用作update函数

		:ini_IP_q 初始获得ip的队列
		:max_page 抓取的最大页数

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
					ini_IP_q.put(ip)
			ip_page = ip_page + 1


	@staticmethod
	def kuaidaili_get_IP():
		'''
		功能：从快代理(www.kuaidaili.com)获取ip，将获取到的ip加入ini_IP_q队列
		:ini_IP_q 初始获得ip的队列
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
						ini_IP_q.put(ip)

	@staticmethod
	def verify_IP():
		'''
		功能：从ini_IP_q队列获取ip，验证ip有效性，将有效ip加入队列available_IP_q
		:ini_IP_q 初始获得ip的队列
		:available_IP_q 有效ip
		'''
		while True:
			IP = ini_IP_q.get(timeout=60)
			proxy = {'http': 'http://' + IP}
			# print "测试：" + str(IP) + "\n"
			try:
				res=requests.get("http://www.baidu.com",proxies=proxy,timeout=10)
				if res.content.find("百度一下")!=-1:
					print str(IP) + " 可用 ...\n"
					available_IP_q.put(proxy)
			except:
				pass



def run_Getter():
	'''
	多线程运行各获取ip的函数
	'''
	print 'getting ips...'
	global get_IP_td
	get_66IP = threading.Thread(target=IP_Getter.get_66IP)
	get_IP_td.append(get_66IP)
	get_66IP.start()
	goubanjia_get_IP = threading.Thread(target=IP_Getter.goubanjia_get_IP,  args=(11,))
	get_IP_td.append(goubanjia_get_IP)
	goubanjia_get_IP.start()
	ip181_get_IP = threading.Thread(target=IP_Getter.ip181_get_IP, args=(6,))
	get_IP_td.append(ip181_get_IP)
	ip181_get_IP.start()
	# get_XiciIP = threading.Thread(target=IP_Getter.get_XiciIP)
	# get_XiciIP.start()
	print 'sleep ...'
	time.sleep(60)
	print 'verify ...'



def ip_Verify():
	'''
	验证ip有效性
	'''
	global ini_IP_q
	global verify_IP_td
	print "the num of IP is " + str(ini_IP_q.qsize())
	for _ in range(5):
		verify_IP_td.append(threading.Thread(target=IP_Getter.verify_IP))
	for td in verify_IP_td:
		td.start()



def ip_watcher():
	global verify_IP_td
	global get_IP_td

def get_IP():
	'''
	获取验证后的有效ip，可作为以后使用的接口
	'''
	global available_IP_q
	if available_IP_q.empty():
		raise myException.available_IP_usedup
	else:
		ip = available_IP_q.get()
		return ip



if __name__ == '__main__':
	# run_Getter()
	# time.sleep(60)
	# while True:
		# print get_IP()
	IP_Getter.get_XiciIP()
