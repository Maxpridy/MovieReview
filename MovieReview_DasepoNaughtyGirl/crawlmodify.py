import urllib
import urllib.request
import urllib.parse
import bs4
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor


def deleteTag(x):
	return re.sub("<[^>]*>", "", x)


def getComments(code):
	def makeArgs(code, page):
		params = {
			'code': code,
			'type': 'after',
			'isActualPointWriteExecute': 'false',
			'isMileageSubscriptionAlready': 'false',
			'isMileageSubscriptionReject': 'false',
			'page': page
		}
		return urllib.parse.urlencode(params)

	def innerHTML(s, sl=0):
		ret = ''
		for i in s.contents[sl:]:
			if i is str:
				ret += i.strip()
			else:
				ret += str(i)
		return ret

	def fText(s):
		if len(s): return innerHTML(s[0]).strip()
		return ''

	retList = []
	colSet = set()
	print("Processing: %d" % code)
	page = 1
	while 1:
		try:
			f = urllib.request.urlopen("http://movie.naver.com/movie/bi/mi/pointWriteFormList.nhn?" + makeArgs(code, page))
			data = f.read().decode('utf-8')
		except:
			break
		soup = bs4.BeautifulSoup(re.sub("&#(?![0-9])", "", data), "html.parser")
		cs = soup.select(".score_result li")
		if not len(cs): break
		for link in cs:
			try:
				url = link.select('.score_reple em a')[0].get('onclick')
			except:
				print(page)
				print(data)
				raise ""
			m = re.search('[0-9]+', url)
			if m:
				url = m.group(0)
			else:
				url = ''
			if url in colSet: return retList
			colSet.add(url)
			cat = fText(link.select('.star_score em'))
			cont = fText(link.select('.score_reple p'))
			cont = re.sub('<span [^>]+>.+?</span>', '', cont)
			retList.append((url, cat, cont))
		page += 1
		print(page)

	return retList


def fetch(i):
	reviewoutname = 'reviews.txt'
	labeloutname = 'labels.txt'
	try:
		if os.stat(outname).st_size > 0: return
	except:
		None
	rs = getComments(i)
	if not len(rs): return
	reviewf = open(reviewoutname, 'w', encoding='utf-8')
	labelf = open(labeloutname, 'w', encoding='utf-8')

	for idx, r in enumerate(rs):
		if idx: reviewf.write(chr(10))
		reviewf.write("%s" % (r[2].replace("'", "''").replace("\\", "\\\\")))
		if (int(r[1]) >= 2):
			labelf.write("positive")
			labelf.write(chr(10));
		else:
			labelf.write("negative")
			labelf.write(chr(10));


	reviewf.write(chr(10))
	reviewf.close()
	labelf.close()
	time.sleep(1)


with ThreadPoolExecutor(max_workers=5) as executor:

	executor.submit(fetch, 42589)
