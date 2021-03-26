# xml-parsing

parse-kangyur-data.py is a script is designed to parse and update the 84000 XML file kangyur-data to incorporate outside data on texts and their translators. Currently it also loads the BDRC spreadsheet of data on 84000 works, which I downloaded to my computer, so may not be the most up to date file. (Note that I am in the process of refactoring the code to be more object-oriented, which will allow me to improve the functionality).

# script functionality

parse-kangyur-data.py looks through all the text elements of the xml document and matches them up by tohoku number with the spreadsheet. If there are already attributions on the 84000 side, it creates a list of possible individuals from the spreadsheet (based on the BDRC ID of persons associated with the work, located by tohoku number). It then matches up the attribution, if possible. If it finds a match, it adds roles and the BDRC ID of the person. If there is no match it adds whatever attribution data it could find from the spreadsheet. It then writes updated info to a new xml file.

Currently the script only considers the first BDRC work listed. It needs to be updated to consider multiple works, because text and attribution data missing from one might be available in another.

# output

It outputs several csv files as follows:
person_matches.csv contains 84000 IDs and BDRC IDs of persons that match
unmatched_persons.csv contains the 84000 names and ID for persons that did not match, as well as the hash of possibile individuals from the BDRC side
unmatched_works.csv contains a list of works by tohoku number that were not matched to a BDRC work
unattributed_works.csv contains a list of works (by ID) for which no attributions could be found. It overlaps with the above file.

sample-data.xml is a test file containing a subset of the xml data
