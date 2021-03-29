
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import re
from pathlib import Path
from dataset import Dataset, Output
import requests

# data_file = 'sample-data.xml'
data_file = "/Users/williamdewey/Development/code/84000-data-rdf/xml-parsing/data-export/kangyur-data.xml"
#load the xml file
ET.register_namespace('', "http://read.84000.co/ns/1.0")
ET.register_namespace('rdf', "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
ET.register_namespace('owl', "http://www.w3.org/2002/07/owl#")
ns = {
  'default': "http://read.84000.co/ns/1.0",
  'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
  'owl': "http://www.w3.org/2002/07/owl#"
}
tree = ET.parse(data_file)
root = tree.getroot()
texts = root.findall("default:text", ns)

#import the BDRC spreadsheet

spreadsheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRoQ2LY-zLATi0XMd_MUhV94zAMkHLzxbAVHji4EtBLl2gAkzXJmKyq0alkd9B3HJsX-98D6mKzCoyL/pub?output=xlsx"
r = requests.get(spreadsheet_url)
spreadsheet_path = '/users/williamdewey/Development/code/84000-data-rdf/xml-parsing/data-export/ATII - Tentative template.xlsx'
with open(spreadsheet_path, 'wb') as f:
    f.write(r.content)
spreadsheet = Path(spreadsheet_path)
kangyur_sheet = ""
if spreadsheet.exists():
    kangyur_sheet = pd.read_excel(spreadsheet, sheet_name = "DergeKangyur")
    tib_sheet = pd.read_excel(spreadsheet, sheet_name = "Persons-Tib")
    ind_sheet = pd.read_excel(spreadsheet, sheet_name = "Persons-Ind")

dataset = Dataset(texts, ns, kangyur_sheet)
#iterate through XML entries (texts)
 #should refactor with namespace dictionaries






for text in dataset.texts:

    for work in text.works:
        if len(work.attributions) > 0:
            #get the names that are already in the 84000 spreadsheet
            for attribution in work.attributions:
                #make the name into more searchable format
                # label = attribution.find("default:label", ns)
                # name_84000 = strip_name(label.text)
                
                
                attribution.find_matches()
                # for bdrc_id, bdrc_names in possible_individuals.items():
                #     for bdrc_name in bdrc_names:
                #         print(f"checking {bdrc_name} against {name_84000}")
                #         if re.search(name_84000, bdrc_name, re.IGNORECASE):
                #             #update the attributions
                #             #add role that matches with the BDRC id
                            
                #             #add alternate role?
                #             break
                #     if matched:
                #         if id_84000 not in person_matches["84000 ID"]:
                #             person_matches["84000 ID"].append(id_84000)
                #             person_matches["BDRC ID"].append(bdrc_id)
                #         break
                # if not matched:
                #     print("no matches found")
                #     if id_84000 not in unmatched_persons["84000 ID"] and possible_individuals not in  unmatched_persons["possible BDRC matches"]:
                #         unmatched_persons["84000 ID"].append(id_84000)
                #         unmatched_persons["84000 name"].append(name_84000)
                #         unmatched_persons["possible BDRC matches"].append(possible_individuals)
        else:
            work.add_attributions()
            
#some query to get associated places, likely from BDRC
#export CSV with matching ID's
matches_df = pd.DataFrame(Output.person_matches)
matches_df.to_csv("person_matches.csv")
unmatched_df = pd.DataFrame(Output.unmatched_persons)
unmatched_df.to_csv("unmatched_persons.csv", encoding='utf-8')
unmatched_works_df = pd.DataFrame(Output.unmatched_works)
unmatched_works_df.to_csv("unmatched_works.csv")
unattributed_works_df = pd.DataFrame(Output.unattributed_works)
unattributed_works_df.to_csv("unattributed_works.csv")
#write to file


tree.write("new-kangyur-data-test.xml")