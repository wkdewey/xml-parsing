# xml-parsing

parse-kangyur-data.py is a script is designed to parse the 84000 XML file kangyur-data.xml to incorporate outside data on texts and their translators, which fall under the purview of the 84000 translation project. Currently it compares 84000 data with the BDRC data found in [this spreadsheet](https://docs.google.com/spreadsheets/d/1BLhfPjUdtwt6JS_yZG5NXqcHA7e9IGFHaLsBH-y3igg/edit#gid=319433259), specifically in the DergeKangyur sheet.

In the process of matching up the data, the script uses "combined notes on spreadsheet.xlsx" and "WD_missing_entries" where I have matched up persons and texts found in both data sets

# script functionality

parse-kangyur-data.py parses the XML file kangyur-data.xml, looking through all the <work> elements of the XML document and matches them up by tohoku number with the BDRC spreadsheet. If there are already attributions on the 84000 side for that work, it creates a list of possible individuals from the spreadsheet (based on the BDRC IDs listed in the spreadsheet). It then matches up the attribution by name, if possible. At this point, the script records and outputs spreadsheet files indicating where persons, works, and roles match or do no match between the XML file and the spreadsheet. It also adds the BDRC ID to the spreadsheet.
  
After going through the XML data once, it can create a list of all matched persons, combining those matched by the script with those I manually matched up by looking at the Tibetan and Sanskrit. Using this list, it groups all matches of the BDRC ID with 84000 IDs in order to identify duplicates. It then adds the 84000 IDs to the spreadsheet. The updated spreadsheet is then extended with missing entries (tohoku numbers that are duplicates and for which BDRC has information on the duplicate entry), which I identified from previous data output.
  
Finally the script uses the updated spreadsheet to update the XML file with additional data. If an attribution (person or place) is already in the XML file, it is updated so that the information matches BDRC. If it is not present in the attribution file, attribution elements are added with role attribute, 84000 ID as the resource attribute, name (under the label element), and matching BDRC work (owl:sameAs attribute with resource attribute). As it does so, it outputs a spreadsheet of newly added attributions and finally ouputs the new XML file

# input files (found in the data-export file)
1. ATII - Tensative template.xlsx is BDRC's spreadsheet file downloaded from Google Docs
2. kangyur-data.xml is the original 84000 data file
3. WD_identified_person_matches.xlsx are matches that I identified by hand, which the script could not identify (these are often transliterated Sanskrit or phonetic Tibetan names)
4. WD_missing_entries.xlxs are entries from the BDRC spreadsheet that I could match up based on different Tohoku numbers referring to the same text

# output files

It outputs several csv and spreadsheet files as follows:

1. person_matches.csv contains 84000 IDs and BDRC IDs of persons that match
2. Discrepancies.xlsx notes where 84000 and BDRC do not match up, as well as possible resolutions.
  3. unmatched_persons.csv contains the 84000 names and ID for persons that did not match, as well as a dictionary of possibile individuals from the BDRC side
  4. unmatched_works.csv contains a list of works by tohoku number that were not matched to a BDRC work
  5. unattributed_works.csv contains a list of works (by ID) for which no attributions could be found. It overlaps with the above file.
  6. matchable_works.csv and attributable_works.csv contain lists of 84000 works that did not match a BDRC work in the spreadsheet, or
  7. discprepant_roles.csv notes instances where a person is assigned different roles (i.e. translatorTib vs. translatorPandita) in 84000 and BDRC for the same text.
8. all_person_matches.xlsx is a spreadsheet that combines the data in person_matches.csv and WD_identified_person_matches.xlsx. The sheet 'grouped matches' also indicates duplicate 84000 ids, that match with the same BDRC number
9. WD_BDRC_data.xlsx is the copy of the BDRC spreadsheet (DergeKangyur sheet) with the data I added on to it: BDRC IDs for works, 84000 IDS for persons, and missing entries for texts that can be filled in based on 84000 data.
10. notes_on_discrepant_roles.csv contains my notes on the discrepant roles based on the colophons translated at 84000.
11. new_kangyur_data.xml is the xml data with updated attributions
