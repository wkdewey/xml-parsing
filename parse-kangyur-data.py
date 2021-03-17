
import xml.etree.ElementTree as ET
import pandas as pd
import re
from pathlib import Path

data_file = 'sample-data.xml'
# data_file = "/Users/williamdewey/Development/code/84000-data-rdf/data-export/kangyur-data.xml"
#load the xml file
ET.register_namespace('', "http://read.84000.co/ns/1.0")
ET.register_namespace('rdf', "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
ET.register_namespace('owl', "http://www.w3.org/2002/07/owl#")
tree = ET.parse(data_file)
root = tree.getroot()
#import the BDRC spreadsheet
spreadsheet = Path(__file__).parent / "/Users/williamdewey/Development/code/84000-data-rdf/data-export/Tentative template.xlsx"
kangyur_sheet = ""
if spreadsheet.exists():
  kangyur_sheet = pd.read_excel(spreadsheet, sheet_name = "DergeKangyur")
#iterate through XML entries (texts)
 #should refactor with namespace dictionaries
ns = {
  'default': "http://read.84000.co/ns/1.0",
  'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
  'owl': "http://www.w3.org/2002/07/owl#"
}
for text in root.findall("default:text", ns):
    bibl = text.find("default:bibl", ns)
    toh_num = bibl.attrib["key"][3:]
    #match ID with spreadsheet
    spread_num = "D" + toh_num
    match = kangyur_sheet.loc[kangyur_sheet["ID"] == spread_num]
    #add roles from spreadsheet
    #get lists of roles, and lists of names
    roles = match["role"]
    names = match["indicated value"]
    ids = match["identification"]
    #add an element <attribution> under <work>, with role set to value of spreadsheet
    work = bibl.find("./{http://read.84000.co/ns/1.0}work[@type='tibetanSource']")
    for (idx, role) in enumerate(roles):
      attribution = ET.SubElement(work, "attribution")
      attribution.attrib["role"] = role
      #add a label with corresponding name
      label = ET.SubElement(attribution, "label")
      label.text = names.iloc[idx]
      sameAs= ET.SubElement(attribution, "owl:sameAs")
      if type(ids.iloc[idx]) is str:
          person_uri = "http://purl.bdrc.io/resource/" + ids.iloc[idx]
      sameAs.attrib["rdf:resource"] = person_uri
    



#some query to get associated places, likely from BDRC

#write to file
tree.write("new-sample-data.xml")