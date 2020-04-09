import random
import aiohttp
import asyncio
import datetime
import time
import json
import ast
from bs4 import BeautifulSoup

def isFailure(soup):
	tableBody = soup.tbody

	if tableBody == None:
		return True
	return False

# Given the html for the hiscores page, parse the
# highest rank out of the page.
# Returns True iff the page's highest rank is 1.
# This should be the first page of the hiscores.
def isFirstPage(soup):

	if soup.tbody == None or len(soup.tbody.find_all('td')) < 4:
		return None

	rank = soup.tbody.find_all('td')[3]

	if "1" == rank.get_text().strip():
		return True
	return False

def isLastPage(soup):
	if soup.tbody == None or len(soup.tbody.find_all('td')) < 4:
		return None

	if soup.find_all('a', {'class': 'personal-hiscores__pagination-arrow personal-hiscores__pagination-arrow--down'}):
		return False
	return True

# Given the html for the hiscores page, parse the kills column
# and return it as a list (highest to lowest rank order).
def getVals(soup):
	vals = []

	tableBody = soup.tbody

	tds = tableBody.find_all('td')
	for i in range(5, len(tds), 3):
		#int call can't handle commas
		vals.append(int(tds[i].get_text().replace(',', '')))
	return vals

async def grabPage(session, tableNumber, pageNumber, fails=0):
	url = 'https://secure.runescape.com/m=hiscore_oldschool/overall?category_type=1&table={}&page={}'.format(tableNumber, pageNumber)
	time.sleep(random.random())
	async with session.get(url) as response:
		resp = await response.text()

		if response.status != 200:
			print('Status code: {}'.format(response.status))
			return (pageNumber, None, None)
		soup = BeautifulSoup(resp, "html.parser")

		if isFailure(soup):
			time.sleep(random.random()+1)
			if fails < 3:
				return await grabPage(session, tableNumber, pageNumber, fails+1)
			else:
				print('Failed a lot. Ending...')
				return (pageNumber, None, None)

		firstPageFlag = isFirstPage(soup)

		# Retrieve vals and populate the shape map
		vals = getVals(soup)

		if vals == None or firstPageFlag == None:
			print('Vals {}\nFirstPageFlag {}'.format(vals, firstPageFlag))

			return (pageNumber, None, None)


		if firstPageFlag and pageNumber != 1:
			print('Found not first page')
			return (pageNumber, None, False)

		if isLastPage(soup):
			return (pageNumber, vals, True)
		else:
			return (pageNumber, vals, False)

async def grabBossKills(tableNumber, pageNums, loop):
	tasks = []
	async with aiohttp.ClientSession() as session:
		for pageNum in pageNums:
			tasks.append(loop.create_task(grabPage(session, tableNumber, pageNum)))

		await asyncio.gather(*tasks)

	lambdaResponse = {
	'pageData': {},
	}
	for t in tasks:
		lambdaResponse['pageData'][t.result()[0]] = (t.result()[1], t.result()[2])
	return lambdaResponse
	
def lambda_handler(event, context):
	if not 'pageNums' in event or not 'tableNum' in event:
		return {
			'status': 400,
			'body': 'Bad request :('
		}
	loop = asyncio.get_event_loop()
	pageNums = ast.literal_eval(event['pageNums'])
	tableNum = int(event['tableNum'])
	startTime = datetime.datetime.now()

	hitLastPage = loop.run_until_complete(grabBossKills(tableNum, pageNums, loop))
	return {
		'status': 200,
		'body': json.dumps(hitLastPage)
	}
