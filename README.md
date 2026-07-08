# hamamooz_log_parser
a cli tool for parsing and analysis of saved log

# Libraries used and justification

# Desgin Notes

# Problems
## run time:
runtime may increase drasticly due to large number of records(not with the mock versino but in real production senarios)

### solution: 
we can make a copy file form the log and then create a service(in linux i would use systemctl) that monitor out log file and if any new record was appended we add it to the coppy file and we will remove the processed records from the copy version so at least we don't need to process everything over and over again
we will save our analysis up to some point in a json file (we can also put it in db file but since its going to only keep the aggregated data it won't be necessory)

note: since its not in the tasks scope i would not write the service i mentioned for updating the copy because implementation of it on the examiners system might be hard and also we don't have a updating log, its simply mock data