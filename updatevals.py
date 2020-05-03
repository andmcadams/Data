import csv
import sys
import os
import json
import datetime

names=["Abyssal Sire", "Alchemical Hydra", "Barrows Chests", "Bryophyta", "Callisto", "Cerberus", "CoX", "Cox CM", "Chaos Elemental", "Chaos Fanatic", "Commander Zilyana", "Corporeal Beast", "Crazy Archaeologist", "Dagannoth Prime", "Dagannoth Rex", "Dagannoth Supreme", "Deranged Archaeologist", "General Graardor", "Giant Mole", "Grotesque Guardians", "Hespori", "Kalphite Queen", "King Black Dragon", "Kraken", "Kree'Arra", "K'ril Tsutsaroth", "Mimic", "Obor", "Sarachnis", "Scorpia", "Skotizo", "The Gauntlet", "The Corrupted Gauntlet", "Theatre of Blood", "Thermonuclear Smoke Devil", "TzKal-Zuk", "TzTok-Jad", "Venenatis", "Vet'ion", "Vorkath", "Zulrah"]
tableNums = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 54]

# Look for the processedresults directory and abort if not found.
try:
	filenames = sorted(os.listdir('./processedresults'))
	print(filenames)
except FileNotFoundError as e:
	print('Unable to find processedresults directory. Aborting...')
	exit(1)

results = {}
players = {}
deltas = {}
# Add keys to both results and players
for k in tableNums:
	results[k] = []
	deltas[k] = []

# For each day (file), yoink the overallstats file and check that for the stats I want to display
for file in filenames:
	stats = open('./processedresults/{}/overallstats.csv'.format(file), 'r', newline='')

	fileReader = csv.reader(stats, delimiter=',', quotechar='|')

	# Skip the first row since it's just the titles of all the columns
	row = fileReader.__next__()
	row = fileReader.__next__()
	# For each row, add kills to results and the player count to players
	while row != None:

		players[int(row[0])] = int(row[1])
		results[int(row[0])].append(row[3])

		try:
			row = fileReader.__next__()
		except StopIteration as e:
			break
	stats.close()

# Get current players. Note that players[k] is the number of players for boss k on the last day.
# Starting -1 to deal with indexing problems in js.
current_players = [-1]
for k in players:
	current_players.append(players[k])

# Create this atrocity of a table. There has to be a better way to do this.
# Unfortunately, even Google admits that the disadvantages to this method are 
# *Syntax is tricky to get right, and prone to typos.
# *Not very readable code.
# This method does allow me to generate the tables much faster as they get larger though.

# Create the columns. These include a date column and a column for each boss.
# These are shared by the two data tables.
cols = []
cols.append({'id': 'date', 'label': 'Date', 'type': 'date'})
for i in range(len(names)):
	cols.append({'id': tableNums[i], 'label': names[i], 'type': 'number'})

# Populate the rows with data. Note that since you can't input things by row, this becomes
# an exercise in patience. Each day becomes its own row, so the format of each rowdata is
# [Date(), Sire kills on date, Hydra kills on date, ..., Zulrah kills on date]
# This is then transformed into the abomination that google charts wants.
rows = []
for i in range(len(filenames)):

	# Get the date of the data currently being looked at.
	year = int(filenames[i][:4])
	# Subtract 1 from month to account for the dumb way js handles dates
	month = int(filenames[i][5:7])-1
	day = int(filenames[i][8:])

	# Add date to rowdata.
	rowdata = ['Date({},{},{})'.format(year, month, day)]

	# Add kills from each boss to rowdata.
	for j in results:
		rowdata.append(results[j][i])

	# Transform regular rowdata into what google chart wants.
	rowdata = [{'v': r} for r in rowdata]
	row = {"c": rowdata}
	rows.append(row)

# Similarly, significant work must be done in order to create rows for the deltas.
# This is done here instead of during runtime in js because then I have to either parse
# data from google chart's questionable format in js or include a copy of the kill counts in js.
deltaRows = []

for i in range(len(filenames)):
	# The last file cannot have a delta since there is no data for the next day.
	if i == len(filenames)-1:
		break

	# Check to make sure the day being looked at can have a delta.
	# This means checking if the next day's data exists.
	year = int(filenames[i][:4])
	month = int(filenames[i][5:7])-1
	day = int(filenames[i][8:])
	currentDate = datetime.date(year, month+1, day)
	nyear = int(filenames[i+1][:4])
	nmonth = int(filenames[i+1][5:7])-1
	nday = int(filenames[i+1][8:])
	nDate = datetime.date(nyear, nmonth+1, nday)
	# If the difference between this day and the next day with data is more than one day,
	# an accurate delta can't be given, so it should be skipped.
	if (nDate-currentDate).days != 1:
		continue

	# Add date to rowdata.
	rowdata = ['Date({},{},{})'.format(year, month, day)]
	# Add delta for each boss to rowdata.
	for j in results:
		rowdata.append(int(results[j][i+1]) - int(results[j][i]))
		# Add delta data to another list in a usable format to be used later
		deltas[j].append(int(results[j][i+1]) - int(results[j][i]))

	# Conversion to google chart format.
	rowdata = [{'v': r} for r in rowdata]
	row = {"c": rowdata}
	deltaRows.append(row)

# Final formatting for google chart data.
table = {
	"cols": cols,
	"rows": rows
}

deltaTable = {
	"cols": cols,
	"rows": deltaRows
}

# Take deltas for each boss to create lists of avg kills/day and max kills/day.
# Starting -1 to deal with indexing problems in js.
avg_day = [-1]
max_day = [-1]
for k in deltas:
	avg_day.append(sum(deltas[k])//len(deltas[k]))
	max_day.append(max(deltas[k]))

outfile = open('datavals.js', 'w+')
outfile.write('var data = {}\nvar deltaData = {}\n'.format(json.dumps(table), json.dumps(deltaTable)))
outfile.write('var players = {}\n'.format(json.dumps(current_players)))
outfile.write('var avg_day = {}\n'.format(json.dumps(avg_day)))
outfile.write('var max_day = {}\n'.format(json.dumps(max_day)))
outfile.write('var minValues = [-1, 50, 50, 50, 10, 50, 50, 50, 10, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 10, 50, 50, 50, 50, 50, 2, 10, 50, 50, 10, 50, 10, 50, 50, 2, 10, 50, 50, 50, 50]\n')