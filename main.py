import requests
from lxml import etree
import time

from requests.packages import urllib3
urllib3.disable_warnings()

CURRENT_COURSE=["World Literature (2019)"]#, "AP Human Geography (2019)"]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
}

login_url="https://bb.shenzhong.net:6400/webapps/bb-strongLogin-BBLEARN/login.jsp?user_id={}&password={}"
grades_url="https://14.29.153.45:6400/webapps/bb-social-learning-BBLEARN/execute/mybb?cmd=display&toolId=MyGradesOnMyBb_____MyGradesTool&extraParams=override_stream=mygrades"
course_url="https://14.29.153.45:6400/webapps/bb-mygrades-BBLEARN/myGrades?course_id={}&stream_name=mygrades"
stream_url="https://14.29.153.45:6400/webapps/streamViewer/streamViewer"


class Spider(object):

	def __init__(self,account,passwd):
		self.account=account
		self.passwd=passwd
		self.session=requests.Session()
		self.courses=dict()
		self.scores=dict()
		self.weights=list()

	def login(self):
		current_url=login_url.format(self.account,self.passwd)
		res=self.session.get(current_url,verify=False)
		if res.status_code==200:
			print("login successfully")
		else:
			print("login failed")
			print(res.status_code)
			time.sleep(3)
			exit(0)

	def get_course_list(self):
		data={
			"cmd": "loadStream",
			"streamName": "mygrades",
			"providers": "{}",
			"forOverview": "false"
			
		}
		res=self.session.post(stream_url,data=data)
		
		course_list=res.json()['sv_extras']['sx_courses']

		# print(len(course_list))
		
		for course in course_list:
			name=course['name']
			id=course['id']
			self.courses[name]=id

	def get_grades(self):
		for course in self.courses.items():
			self.get_grade(course)
			# break
	
	def get_grade(self,course):
		if course[0] not in CURRENT_COURSE:
			return
		current_url=course_url.format(course[1])
		res=self.session.get(current_url)
		html_raw = etree.HTML(res.text)
		
		scores=dict()

		# status = html_raw.xpath('//div[@class="sortable_item_row calculatedRow row expanded"]//span[@class="grade"]/text()')
		items = html_raw.xpath('//div[@id="grades_wrapper"]/div[@class="sortable_item_row graded_item_row row expanded"]')
		for item in items[:-1]:
			icat=item.xpath('div[@class="cell gradable"]/div[@class="itemCat"]')[0].text.strip("\n ")
			igrade=item.xpath('div[@class="cell grade"]/span[@class="grade"]')[0].text.strip("\n ")
			igrade_possible=item.xpath('div[@class="cell grade"]/span[@class="pointsPossible clearfloats"]')[0].text.strip("\n/ ")
			# print(icat)
			# print(igrade)
			# print(igrade_possible)
			try:
				scores[icat][0]+=float(igrade)
				scores[icat][1]+=float(igrade_possible)
			except:
				scores[icat]=list()
				scores[icat].append(float(igrade))
				scores[icat].append(float(igrade_possible))
				print("create "+icat)
			
		for score in scores:
			print(score+str(scores[score][0]/scores[score][1]))
		
		self.scores=scores

		print(scores[icat])
		return
	def assign_weight(self):
		weighted_percentage=0
		remain_weight=1

		for score in self.scores:
			tmp_weight=float(input("Please input weight for "+score+": "))
			weighted_percentage=weighted_percentage+self.scores[score][0]/self.scores[score][1]*tmp_weight
			remain_weight=remain_weight-tmp_weight
			print("assign successful. Remaining weight: "+str(remain_weight))
		print("the ultimate weighted percentage is: "+str(weighted_percentage))
		pass

		
if __name__=="__main__":
	spider=Spider(input("please input account: "),input("please input password: "))
	spider.login()
	spider.get_course_list()
	spider.get_grades()
	spider.assign_weight()
