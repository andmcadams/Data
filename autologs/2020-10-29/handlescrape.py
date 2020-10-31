import json

logscrape = open('zulrahlogscrape.txt', 'r').read().split('\n')

pages = {}

for line in logscrape:
		if line:
			lineData = json.loads(line)

			# For each loaded line, split into keys and assign each one to the table
			for k in lineData.keys():
				pages[k] = lineData[k][0]

lastPage = 0
lastCount = 0
totalMaxDiff = 0
for page in sorted(pages.keys(), key=lambda kv: int(kv)):
	if pages[page] is None:
		print('Page is null: {}'.format(page))
		continue
	firstCount = pages[page][0]
	newLastCount = pages[page][-1]
	maxDiff = 25*(int(page)-int(lastPage) - 1)*(lastCount-firstCount)
	if maxDiff != 0 and lastPage != 0:
		print('Difference of {} between pages {} and {}. Max difference: {}'.format((lastCount-firstCount), lastPage, page, maxDiff))
		totalMaxDiff += maxDiff

	lastPage = page
	lastCount = newLastCount

print(totalMaxDiff)