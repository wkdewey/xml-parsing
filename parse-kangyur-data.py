
import xml.etree.ElementTree as ET
import pandas as pd
import re
from pathlib import Path

data_file = 'sample-data.xml'
# data_file = "/Users/williamdewey/Development/code/84000-data-rdf/data-export/kangyur-data.xml"
#load the xml file
tree = ET.parse(data_file)
root = tree.getroot()
#import the BDRC spreadsheet
spreadsheet = Path(__file__).parent / "/Users/williamdewey/Development/code/84000-data-rdf/data-export/Tentative template.xlsx"
kangyur_sheet = ""
if spreadsheet.exists():
  kangyur_sheet = pd.read_excel(spreadsheet, sheet_name = "DergeKangyur")
#iterate through XML entries (texts)
 #should refactor with namespace dictionaries
for bibl in root.iter("{http://read.84000.co/ns/1.0}bibl"):
    toh_num = bibl.attrib["key"][3:]
    print(toh_num)
    #match ID with spreadsheet
    spread_num = "D" + toh_num
    match = kangyur_sheet.loc[kangyur_sheet["ID"] == spread_num]
    print(match)


#add roles from spreadsheet

#some query to get associated places, likely from BDRC

#write to file, probably