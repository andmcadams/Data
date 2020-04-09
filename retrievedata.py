import json
import datetime
import time
from bs4 import BeautifulSoup
import boto3
import sys
import random

proxies = ['getHiscores{}'.format(i) for i in range(1, 11)]
functionArn = json.load(open('secrets.json'))['arn']

def getPagesToRetrieve(tolerance, retrievedPages):
	# Make a pass through the list and queue up bad ones
	prevPageIndex = 1
	thisPageIndex = None
	queue = []
	for i in range(1, len(retrievedPages)):
		if retrievedPages[i] == None:
			continue

		thisPage = retrievedPages[i]
		thisPageIndex = i

		# Get the last number from the previous page
		prevPageVal = retrievedPages[prevPageIndex][-1]

		thisPageVal = thisPage[0]

		if prevPageVal - thisPageVal > tolerance and thisPageIndex-prevPageIndex > 1:
			queue.append((thisPageIndex+prevPageIndex)//2)

		prevPageIndex = i

	return queue

def addResponse(content, retrieved):

	body = json.loads(content['body'])
	print(body['pageData'])
	for k in body['pageData']:
		retrieved[int(k)] = body['pageData'][k][0]

	print(body['pageData'].keys())
	goodVals = [int(k) for k in body['pageData'].keys() if body['pageData'][k][0] != None]
	print(goodVals)
	if goodVals == []:
		return None
	return max(goodVals)

# If a page past last is contained, return True
# If no page after last is contained, return False
def containsPastLast(content):

	body = json.loads(content['body'])
	for k in body['pageData']:
		if body['pageData'][k][0] == None and body['pageData'][k][1] == False:
			return True
	return False


def isLast(pageNum, content):
	pageNum = str(pageNum)
	body = json.loads(content['body'])

	#print('isLast({}, {})'.format(pageNum, json.dumps(content)))
	if body['pageData'][pageNum][1] == True:
		return True
	if body['pageData'][pageNum][0] != None:
		return False
	return None

def makeCall(lambda_client, queue, tableNum):
	print('{}:function:{}'.format(functionArn, proxies[random.randint(0, len(proxies)-1)]))

	response = lambda_client.invoke(
    FunctionName='{}:function:{}'.format(functionArn, proxies[random.randint(0, len(proxies)-1)]),
    InvocationType='RequestResponse',
    Payload=json.dumps({
    	'pageNums': str(queue),
    	'tableNum': str(tableNum)
    	})
	)
	return response

def retrieve(tolerance, pageSpacing, tableNum):
	startTime = datetime.datetime.now()
	lambda_client = boto3.client('lambda')
	retrieved = {}
	calls = 0
	#retrieve every 100 pages until an out of bounds occurs
	pageNum = 1
	queue = [1 + pageSpacing*r for r in range(0, 10)]
	last = 0
	while True:
		print('Trying queue: {}'.format(queue))
		response = makeCall(lambda_client, queue, tableNum)
		calls += 1

		print('Received response...')
		content = json.loads(response['Payload'].read())
		print(content)
		# Add responses to retrieved
		last = addResponse(content, retrieved) or last
		# Check for oob
		if containsPastLast(content) == True:
			break
		# increase pages in queue to keep going
		queue = [page + 10*pageSpacing for page in queue]

	# Find the last page
	# Take last page and next 100
	start = last
	ps = pageSpacing
	print('Looking for last page...')
	steps = 0
	while True:
		steps += 1
		if steps > 12:
			print('Could not find last page after 12 attempts. Aborting...')
			exit(1)
		ps //= 2
		if ps == 0:
			ps = 1
		print('Trying page {}'.format(start))
		queue = [start]
		response = makeCall(lambda_client, queue, tableNum)

		calls += 1
		content = json.loads(response['Payload'].read())

		last = addResponse(content, retrieved)
		r = isLast(start, content)
		#if r is None, r is oob
		#if r is False, r is a page, but not the last
		#if r is True, r is a page, and r is the last page
		if r == None:
			start -= ps
		if r == False:
			start += ps
		if r == True:
			break
	
	print('Last page found: {}'.format(last))
	# The last page index is stored in last

	retrievedPages = [None] * (last+1)
	for r in retrieved.keys():
		rI = int(r)
		if rI < len(retrievedPages):
			retrievedPages[rI] = retrieved[r]

	queue = getPagesToRetrieve(tolerance, retrievedPages)
	while True:
		if queue == []:
			break
		
		#Probably want to split up the queue into chunks
		n = 10
		queueChunks = [queue[i * n:(i + 1) * n] for i in range((len(queue) + n - 1) // n )]
		for queue in queueChunks:
			print('Queue: {}'.format(queue))
			response = makeCall(lambda_client, queue, tableNum)
			calls += 1

			content = json.loads(response['Payload'].read())

			if 'body' in content:
				last = addResponse(content, retrievedPages)
			else:
				print('Couldn\'t find a body in the response Payload. Sleeping for 60s...')
				time.sleep(60)

		queue = getPagesToRetrieve(tolerance, retrievedPages)

	mintot = 0
	maxtot = 0
	prevIndex = -1
	for i in range(1, len(retrievedPages)):
		if retrievedPages[i] != None:
			mintot += sum(retrievedPages[i])
			maxtot += sum(retrievedPages[i])
			if prevIndex != -1:
				minadd = 25*(i-prevIndex-1)*(retrievedPages[i][0])
				mintot += minadd
				maxadd = 25*(i-prevIndex-1)*(retrievedPages[prevIndex][-1])
				maxtot += maxadd
			prevIndex = i
	print(retrievedPages)
	avgtot = (maxtot+mintot)/2

	file = open('./autoresults/{}/table{}dt'.format(datetime.datetime.utcnow().strftime('%Y-%m-%d'), tableNum) + '{}.txt'.format(datetime.datetime.utcnow().strftime('%Y-%m-%d--%H-%M')), 'w+')
	# Note that index 0 is always none since there is no page 0!
	file.write(str(retrievedPages[1:]))
	file.close()

	print('T: {}\tPS: {}'.format(tolerance, pageSpacing))
	print('\tEstimated kc (min): {}'.format(mintot))
	print('\tEstimated kc (avg): {}'.format(avgtot))
	print('\tEstimated kc (max): {}'.format(maxtot))
	print('\tTotal calls: {}'.format(calls))
	print('\tTotal time: {}'.format(datetime.datetime.now() - startTime))

tableNum = sys.argv[1]
retrieve(0, 100, tableNum)



