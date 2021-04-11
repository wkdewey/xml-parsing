# xml-parsing

parse-kangyur-data.py is a script is designed to parse the 84000 XML file kangyur-data to incorporate outside data on texts and their translators. Currently it compares 84000 data with the BDRC data found in the spreadsheet at https://docs.google.com/spreadsheets/d/1BLhfPjUdtwt6JS_yZG5NXqcHA7e9IGFHaLsBH-y3igg/edit#gid=319433259. It also incorporates my own work in "combined notes on spreadsheet.xlsx" and "WD_missing_entries" where I have matched up persons and texts found in both data sets

# script functionality

parse-kangyur-data.py looks through all the work elements of the XML document and matches them up by tohoku number with the spreadsheet. If there are already attributions on the 84000 side, it creates a list of possible individuals from the spreadsheet (based on the BDRC ID of persons associated with the work, located by tohoku number). It then matches up the attribution, if possible. If it finds a match, it adds roles and the BDRC ID of the person. If there is no match it adds whatever attribution data it could find from the spreadsheet. It then writes updated info to a new xml file. The script also outputs csv files comparing data from 84000 and BDRC, showing relevant cases where the data match or are discrepant.

The script goes through the data again and matches up works in the spreadsheet with BDRC ID's (taken from the XML), and also persons listed in the spreadsheet with 84000 ID's (taken from the XML). The final spreadsheet is then extended with missing entries, which I identified from previous data output.

(The script is also intended to update the XML, but that part is a work in progress now that I have refactored the code to update the spreadsheet. For now, I commented out or deleted the code that updates the XML)

# output

It outputs several csv and spreadsheet files as follows:

1. person_matches.csv contains 84000 IDs and BDRC IDs of persons that match
2. unmatched_persons.csv contains the 84000 names and ID for persons that did not match, as well as the hash of possibile individuals from the BDRC side
3. unmatched_works.csv contains a list of works by tohoku number that were not matched to a BDRC work
4. unattributed_works.csv contains a list of works (by ID) for which no attributions could be found. It overlaps with the above file.
5. matchable_works.csv and attributable_works.csv contain lists of 84000 works that did not match a BDRC work in the spreadsheet, or
6. discprepant_roles.csv notes instances where a person is assigned different roles (i.e. translatorTib vs. translatorPandita) in 84000 and BDRC for the same text.
7. all_person_matches.xlsx is a spreadsheet that combines the person matches identified by the python script with those I was able to match manually. The sheet 'grouped matches' also indicates duplicate 84000 ids, that match with the same BDRC number
8. WD_BDRC_data.xlsx is a copy of the spreadsheet (DergeKangyur sheet) with the data I added on to it: BDRC IDs for works, 84000 IDS for persons, and missing entries for texts that can be filled in based on 84000 data.
