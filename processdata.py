import json
import ast
import re
import os
import datetime
import csv
import sys

names = {
	"11":			"Abyssal Sire",
	"12":			"Alchemical Hydra",
	"13":			"Barrows Chests",
	"14":		"Bryophyta",
	"15":			"Callisto",
	"16":			"Cerberus",
	"17":			"CoX",
	"18":	"CoX Challenge Mode",
	"19":		"Chaos Elemental",
	"20":			"Chaos Fanatic",
	"21":			"Commander Zilyana",
	"22":			"Corporeal Beast",
	"23":			"Crazy Archaeologist",
	"24":			"Dagannoth Prime",
	"25":			"Dagannoth Rex",
	"26":			"Dagannoth Supreme",
	"27":	"Deranged Archaeologist",
	"28":			"General Graardor",
	"29":			"Giant Mole",
	"30":			"Grotesque Guardians",
	"31":			"Hespori",
	"32":			"Kalphite Queen",
	"33":			"King Black Dragon",
	"34":			"Kraken",
	"35":			"Kree'Arra",
	"36":			"K'ril Tsutsaroth",
	"37":		"Mimic",
	"39":		"Obor",
	"40":		"Sarachnis",
	"41":			"Scorpia",
	"42":			"Skotizo",
	"43":		"The Gauntlet",
	"44":		"The Corrupted Gauntlet",
	"45":		"Theatre of Blood",
	"46":			"Thermonuclear Smoke Devil",
	"47":		"TzKal-Zuk",
	"48":			"TzTok-Jad",
	"49":			"Venenatis",
	"50":		"Vet'ion",
	"51":			"Vorkath",
	"54":			"Zulrah"
}

if len(sys.argv) != 2:
	print('Simulation failed. Please provide 1 argument.')
	print('Usage: python3 simulationV2.py "YYYY-MM-DD"')
	exit(1)
d = sys.argv[1]

try:
	filenames = os.listdir('./autoresults/{}'.format(d))
except FileNotFoundError as e:
	print('There are no stats for the date {}. Aborting...'.format(d))
	exit(1)

counts = []

vals = {}

try:
	os.mkdir('./processedresults/{}'.format(d))
except FileExistsError as exc:
    pass

for filename in filenames:
	tableNum = re.search('table([0-9]+).*', filename)
	tableNum = tableNum.group(1)
	contents = open('./autoresults/{}/{}'.format(d, filename), 'r').read()
	contents = ast.literal_eval(contents)
	numScores = (len(contents)-1)*25 + len(contents[-1])
	numPages = len(contents)
	totalKills = 0
	prevIndex = -1
	completeScores = [None] * len(contents)

	for i in range(len(contents)):
		if contents[i] != None:
			completeScores[i] = contents[i]
			totalKills += sum(contents[i])
			if prevIndex != -1:
				totalKills += 25*(i-prevIndex-1)*(contents[i][0])
			prevIndex = i
			#if i > 0 and completeScores[i][0] > completeScores[i-1][-1]:
				#print("Table {} page {}".format(tableNum, i))
				#print("{} > {}".format(completeScores[i][0], completeScores[i-1][-1]))
		else:
			completeScores[i] = [completeScores[i-1][-1]]*25

	file = open('./processedresults/{}/complete-{}'.format(d, filename), 'w+')
	file.write(str(completeScores))
	file.close()

	vals[tableNum] = {
		"Players": numScores,
		"Pages": numPages,
		"Total KC": totalKills,
		"Average KC/Player": totalKills/numScores
	}

sortedKeys = sorted(vals.keys())


file = open('./processedresults/{}/overallstats.txt'.format(d), 'w+')
for k in sortedKeys:
	boss = vals[k]
	file.write('{} - {}\n'.format(k, names[k]))
	for stat in boss:
		file.write('\t{}:{}\t{}\n'.format(stat, ' '*(20-len(stat)), boss[stat]))
	file.write('\n')
file.close()

file = open('./processedresults/{}/overallstats.csv'.format(d), 'w+', newline='')
writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
writer.writerow(["Table Number", "Players", "Pages", "Total KC", "Average KC/Player"])

for k in sortedKeys:
	boss = vals[k]
	writer.writerow([k] + list(boss.values()))
file.close()