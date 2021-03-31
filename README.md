# xml-parsing

parse-kangyur-data.py is a script is designed to parse and update the 84000 XML file kangyur-data to incorporate outside data on texts and their translators. Currently it compares 84000 data with the BDRC data found in the spreadsheet at https://docs.google.com/spreadsheets/d/1BLhfPjUdtwt6JS_yZG5NXqcHA7e9IGFHaLsBH-y3igg/edit#gid=319433259.

# script functionality

parse-kangyur-data.py looks through all the work elements of the xml document and matches them up by tohoku number with the spreadsheet. If there are already attributions on the 84000 side, it creates a list of possible individuals from the spreadsheet (based on the BDRC ID of persons associated with the work, located by tohoku number). It then matches up the attribution, if possible. If it finds a match, it adds roles and the BDRC ID of the person. If there is no match it adds whatever attribution data it could find from the spreadsheet. It then writes updated info to a new xml file. The script also outputs csv files comparing data from 84000 and BDRC, where it may be relevant that they match or are discrepant.

# output

It outputs several csv files as follows:

1. person_matches.csv contains 84000 IDs and BDRC IDs of persons that match
2. unmatched_persons.csv contains the 84000 names and ID for persons that did not match, as well as the hash of possibile individuals from the BDRC side
3. unmatched_works.csv contains a list of works by tohoku number that were not matched to a BDRC work
4. unattributed_works.csv contains a list of works (by ID) for which no attributions could be found. It overlaps with the above file.
5. discprepant_roles.csv notes instances where a person is assigned different roles (i.e. translatorTib vs. translatorPandita) in 84000 and BDRC for the same text.

sample-data.xml is a test file containing a subset of the xml data
