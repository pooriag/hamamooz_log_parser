# hamamooz_log_parser
a cli tool for parsing and analysis of saved log

# CLI Tool Instructions

- Run from the project root with `python main.py`.
- Use `--path` for the raw log file and `--bloompath` for the IP Bloom filter file.
- Use `--offsetpath`, `--analysispath`, and `--hourlyanalysis` to override saved output locations.
- Use `--start` and `--end` in `YYYY-MM-DD:HH` format to report from a saved hourly range.
- Add `--save` to write the provided paths back into `.env`.
- If a value is missing, the CLI will prompt for it.

## python main.py
don't forget to install dependencies: pip install -r requirements.txt 
# Libraries used and justification
## RUN: pybloomfiltermmap3
since we were only instructed to avoid using the libs that do the log parsing for us this lib does not violate the tasks constraints since its only a saving/compression algorithm and it does not have anything with parsing

bloom filter uses multiple hash functions to map a given input to multiple values and this way we can compress the storage needed and speed up the checkup phase for wanting to check if the ip has been considered for unique ip count or not

note: pay attention that the analysis tool logic can be done without this lib but i include it to avoid implementing the bloom filter which in my opinion is not in the defined task scope and it will overcoplicate the code for no reason and it also could be done without bloom filter or any similar techinque of storing data but like mentioned in problem section it would fail to scale and to handle real senario cases

## hyperloglog
it has nothing to do the parsing itself and the usecase is expalined in problem section

## pandas
in order to aggregat the hourly processed data from csv for the given time range
it has nothing to do with log parsing

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

## obtaining unique ip count for gvien date range
when savin only an aggregate version of analysis when we want to check for a given date range we would run into problem
for other metrics other than uinque ip count the solution is simple we simply need to also log daily metrics onto a table and because all of them can be summed the implementaion would be easy

The real Problem is that we can not log daily unique ip counts and sum them for a gvien date range because ips will overlap

### solution
one way is iterate through all of records ips again and obtain the unique ips
BUT a more EFICIENT way is to use hyperloglog which is another storage system that uses hashing like bloom filter with the difference that it takes much smaller space and its more cost efficient when we need to merge multiple files of this storage system
the design differnce of these two is that bloom filter is designed to answer wther we encountered and element before or not but hyperloglog is designed to keep track of cardinality instead

so in this way we can have a file system that stores the hyperloglog for each day and whenever we want we can merge files for wanted days and obtain the cardinality in O(number of days x m(constant)(16384)) which is much faster than iterating again and the memory space of this storage system is not that much/

# Notes
i am aware that it is not best practice to push data or .env file on repo but due to ease of testing i did so however the cli will guide you through if you don't have any .env file and if you use --save it will save the paramters and paths you gave it so they are not necessory but i wanted to make the testing easier for you

the result will automaticly save to a json when the cli tool is executed

tests are accesable in tests directory