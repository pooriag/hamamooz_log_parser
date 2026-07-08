# hamamooz_log_parser
a cli tool for parsing and analysis of saved log

# Libraries used and justification

# Desgin Notes
## saving the processed records
we can save our processed reocrds up to the point in a json file(db is also an option but since we only want to save aggregated data it won't be necessory)

# Problems
## run time:
runtime may increase drasticly due to large number of records(not with the mock versino but in real production senarios)

### solution: 
we can keep track for an offset that when new records has beend added we don't have to process all records again , just the remaining