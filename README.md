# hamamooz_log_parser
a cli tool for parsing and analysis of saved log

# Libraries used and justification

# Desgin Notes

# Problems
## run time:
runtime may increase drasticly due to large number of records(not with the mock versino but in real production senarios)

### solution: 
we can keep track for an offset that when new records has beend added we don't have to process all records again , just the remaining