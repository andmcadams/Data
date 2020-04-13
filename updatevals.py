import csv
import sys
import os
import json

names=["Abyssal Sire", "Alchemical Hydra", "Barrows Chests", "Bryophyta", "Callisto", "Cerberus", "CoX", "Cox CM", "Chaos Elemental", "Chaos Fanatic", "Commander Zilyana", "Corporeal Beast", "Crazy Archaeologist", "Dagannoth Prime", "Dagannoth Rex", "Dagannoth Supreme", "Deranged Archaeologist", "General Graardor", "Giant Mole", "Grotesque Guardians", "Hespori", "Kalphite Queen", "King Black Dragon", "Kraken", "Kree'Arra", "K'ril Tsutsaroth", "Mimic", "Obor", "Sarachnis", "Scorpia", "Skotizo", "The Gauntlet", "The Corrupted Gauntlet", "Theatre of Blood", "Thermonuclear Smoke Devil", "TzKal-Zuk", "TzTok-Jad", "Venenatis", "Vet'ion", "Vorkath", "Zulrah"]
tableNums = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 54]


try:
	filenames = sorted(os.listdir('./processedresults'))
	print(filenames)
except FileNotFoundError as e:
	print('Unable to find processedresults directory. Aborting...')
	exit(1)

results = {}

for file in filenames:
	stats = open('./processedresults/{}/overallstats.csv'.format(file), 'r', newline='')

# Grab info form the two days
	fileReader = csv.reader(stats, delimiter=',', quotechar='|')

	row = fileReader.__next__()
	row = fileReader.__next__()
	while row != None:
		if not row[0] in results:
			results[row[0]] = [row[3]]
		else:
			results[row[0]].append(row[3])

		try:
			row = fileReader.__next__()
		except StopIteration as e:
			break
	stats.close()

for k in sorted(results.keys()):
	killarr = results[k]
	killdelta = [int(killarr[j]) - int(killarr[max(0, j-1)]) for j in range(len(killarr))]

print(results)
cols = []
cols.append({'id': 'date', 'label': 'Date', 'type': 'date'})
for i in range(len(names)):
	cols.append({'id': tableNums[i], 'label': names[i], 'type': 'number'})

outfile = open('datavals.js', 'w+')

rows = []
for i in range(len(filenames)):
	year = int(filenames[i][:4])
	# Subtract 1 from month to account for the dumb way js handles dates
	month = int(filenames[i][5:7])-1
	day = int(filenames[i][8:])
	rowdata = ['Date({},{},{})'.format(year, month, day)]
	for j in results:
		rowdata.append(results[j][i])

	rowdata = [{'v': r} for r in rowdata]
	row = {"c": rowdata}
	rows.append(row)

deltaRows = []
for i in range(len(filenames)):
	if i == len(filenames)-1:
		break
	year = int(filenames[i][:4])
	# Subtract 1 from month to account for the dumb way js handles dates
	month = int(filenames[i][5:7])-1
	day = int(filenames[i][8:])
	rowdata = ['Date({},{},{})'.format(year, month, day)]
	for j in results:
		rowdata.append(int(results[j][i+1]) - int(results[j][i]))

	rowdata = [{'v': r} for r in rowdata]
	row = {"c": rowdata}
	deltaRows.append(row)


table = {
	"cols": cols,
	"rows": rows
}

deltaTable = {
	"cols": cols,
	"rows": deltaRows
}

outfile.write('var data = {}\nvar deltaData = {}'.format(json.dumps(table), json.dumps(deltaTable)))