values=( 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 39 40 41 42 43 44 45 46 47 48 49 50 51 54 )

d=$(date -u '+%Y-%m-%d')
mkdir "autologs/$d"
mkdir "autoresults/$d"

scrape_data (){
	names=( "Abyssal Sire" "Alchemical Hydra" "Barrows Chests" "Bryophyta" "Callisto" "Cerberus" "CoX" "Cox CM" "Chaos Elemental" "Chaos Fanatic" "Commander Zilyana" "Corporeal Beast" "Crazy Archaeologist" "Dagannoth Prime" "Dagannoth Rex" "Dagannoth Supreme" "Deranged Archaeologist" "General Graardor" "Giant Mole" "Grotesque Guardians" "Hespori" "Kalphite Queen" "King Black Dragon" "Kraken" "Kree'Arra" "K'ril Tsutsaroth" "Mimic" "Obor" "Sarachnis" "Scorpia" "Skotizo" "The Gauntlet" "The Corrupted Gauntlet" "Theatre of Blood" "Thermonuclear Smoke Devil" "TzKal-Zuk" "TzTok-Jad" "Venenatis" "Vet'ion" "Vorkath" "Zulrah" )

	values=( 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 39 40 41 42 43 44 45 46 47 48 49 50 51 54 )

	local i="$1"
	local d="$2"

	echo "Starting to scrape ${names[i]}..." #, ${values[i]}"
	python3 "retrievedata.py" "${values[i]}" > "./autologs/${d}/table${values[i]}dt$(date -u '+%Y-%m-%d--%H-%M').log"
	if [ $? -eq 0 ]
	then
		echo -e "\033[0;32mDone with ${names[i]}.\033[0m"
	else
		echo -e "\033[1;31mError with ${names[i]}. Retrying...\033[0m"
		scrape_data "$i" "$d"
	fi
}

export -f scrape_data

for j in "${!values[@]}"; do
	sem -u -j 4 "scrape_data $j '$d'"
done

sem --wait
python3 processdata.py "$d"
python3 updatevals.py

git add "autologs/" "autoresults/" "processedresults/"
git add "datavals.js"
git commit -m "AUTOCOMMIT---Add new data $d"

git push