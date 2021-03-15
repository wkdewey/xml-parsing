#import the necessary modules
import xml.etree.ElementTree as ET
import pandas as pd
import pdb
import re
from pathlib import Path
#load the XML file/copy the file?
data_file = 'sample-data.xml'
# data_file = "/Users/williamdewey/Development/code/84000-data-rdf/data-export/kangyur-data.xml"
tree = ET.parse(data_file)
root = tree.getroot()
#test
# for child in root:
#     print(child.tag, child.attrib)
#import the BDRC spreadsheet
spreadsheet = Path(__file__).parent / "/Users/williamdewey/Development/code/84000-data-rdf/data-export/Tentative template.xlsx"
kangyur_sheet = ""
if spreadsheet.exists():
  kangyur_sheet = pd.read_excel(spreadsheet, sheet_name = "DergeKangyur")
# print(kangyur_sheet["ID"])
#iterate through XML entries (texts)
# for label in root.iter('label'):
#     pdb.set_trace()
#     print(label)
#     toh_num = label.textroo
#     print(toh_num)
for bibl in root.iter("{http://read.84000.co/ns/1.0}bibl"):
    toh_num = bibl.attrib["key"]
  
#get ID from spreadsheet

#match with ID in this doc

#add IDs from spreadsheet

#add roles from spreadsheet

#some query to get associated places, likely from BDRC

#write to file, probably