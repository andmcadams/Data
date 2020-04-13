# Data
A very basic graph view of this data can be found at https://andmcadams.github.io/Data/

All data were pulled from OSRS hiscores pages.

The filenames refer to the table id of the boss. Check `processedresults/overallstats.txt` for a reference to these numbers.

The master script is run at around 04:00 UTC every day to scrape the hiscores pages. This process takes several hours. Kill counts per day are calculated by calculating the difference in kill counts between that day and the next. Thus the kill count delta for April 1, 2020 is the difference between the kill counts scraped on April 2 and April 1.

`autologs` contains logs for each boss. Just for issue checking.

`autoresults` contains the raw data from each pull. Each file is for a specific boss. The output is a list of lists and Nones, each of which represents a single page of hiscores. The lists contain the actual scores pulled from a page. Nones indicate that the data could be inferred from prior page pulls. In the case of these data, the only time a page's values were assumed was when equal scores could be found in a page before and a page after (0 tolerance).

`processedresults` contains complete versions of the autoresults lists. Nones have been replaced by lists filled with the inferred values. Additionally, there is an overallstats.txt file, which summarizes stats for each boss.

Missing/Incomplete Results due to Hiscores Being Down
* 2020-04-10
* 2020-04-11
* 2020-04-12