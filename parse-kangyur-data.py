#import the necessary modules
import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
#load the XML file/copy the file?
tree = ET.parse('sample-data.xml')
root = tree.getroot()
#test
for child in root:
    print(child.tag, child.attrib)
#import the BDRC spreadsheet
spreadsheet = Path("../data_export/Tentative template.xlsx")
kangyur_sheet = ""
if spreadsheet.exists():
  kangyur_sheet = pd.read_excel(spreadsheet, sheet_name = "dergeKangyur")
print(kangyur_sheet)
#iterate through XML entries (texts)

#get ID from spreadsheet

#match with ID in this doc

#add IDs from spreadsheet

#add roles from spreadsheet

#some query to get associated places, likely from BDRC

#write to file, probably