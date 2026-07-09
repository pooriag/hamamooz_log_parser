# hamamooz_log_parser
a cli tool for parsing and analysis of saved log

# Libraries used and justification
## pybloomfiltermmap3
since we were only instructed to avoid using the libs that do the log parsing for us this lib does not violate the tasks constraints since its only a saving/compression algorithm and it does not have anything with parsing

bloom filter uses multiple hash functions to map a given input to multiple values and this way we can compress the storage needed and speed up the checkup phase for wanting to check if the ip has been considered for unique ip count or not

note: pay attention that the analysis tool logic can be done without this lib but i include it to avoid implementing the bloom filter which in my opinion is not in the defined task scope and it will overcoplicate the code for no reason and it also could be done without bloom filter or any similar techinque of storing data but like mentioned in problem section it would fail to scale and to handle real senario cases

# Desgin Notes
## initial paramters
if any paramters needed and its not given thorugh the .env file or argument with terminal command you will be prompted to provide the necessory argumetns.

## saving the processed records
we can save our processed reocrds up to the point in a json file(db is also an option but since we only want to save aggregated data it won't be necessory)
## ranking top 10 most used end points
since we might have multiple end point with same count we would keep the same count end points in top 10 even if it exeeds 10 untill the difference of 10 and these end points become equal to length of same count end points in top 10(in the senario that they are the least frequent in top10) and then remove them.

this is to not have the same count end point for processed records on considere in top 10 and one not, it doesnt make sense

# Problems
## run time:
runtime may increase drasticly due to large number of records(not with the mock versino but in real production senarios)

### solution: 
we can keep track for an offset that when new records has beend added we don't have to process all records again , just the remaining

## high number of ips:
when we have a large user base we will get requests form lots of ips and if we want to keep track of all of the ips we need to know which we already stored and which we didn't and it will be time consuming to search through all of the saved logs to see that the ip already exists or not

### solution:
since we only want to keep track of count of unique ids a very resource efficient way is using bloom filter (like in redis bloom but without setting up a redis server necesserly we can just use a library)
