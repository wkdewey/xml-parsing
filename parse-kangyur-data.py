
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import re
from pathlib import Path

# data_file = 'sample-data.xml'
data_file = "/Users/williamdewey/Development/code/84000-data-rdf/data-export/kangyur-data.xml"
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
    tib_sheet = pd.read_excel(spreadsheet, sheet_name = "Persons-Tib")
    ind_sheet = pd.read_excel(spreadsheet, sheet_name = "Persons-Ind")
person_matches = { "84000 ID": [], "BDRC ID": []}
unmatched_persons = { "84000 ID": [], "84000 name": [], "possible BDRC matches": []}
unmatched_texts = {"Toh": []}
unattributed_texts = { "84000 ID": []}
#iterate through XML entries (texts)
 #should refactor with namespace dictionaries
ns = {
  'default': "http://read.84000.co/ns/1.0",
  'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
  'owl': "http://www.w3.org/2002/07/owl#"
}

def find_possible_individuals(person_ids, kangyur_names):
    possible_individuals = {}
    for (idx, id) in enumerate(person_ids):
        possible_individuals[id] = []
        kangyur_name = kangyur_names.iloc[idx]
        possible_individuals[id].append(kangyur_name)
        tib_match = tib_sheet.loc[tib_sheet["ID"] == id]
        tib_name_1 = tib_match["names_tib"] 
        if len(tib_name_1) > 0:
            if not pd.isnull(tib_name_1.iloc[0]):
                possible_individuals[id].append(tib_name_1.iloc[0])
        tib_name_2 = tib_match["names_skt"]
        if len(tib_name_2) > 0:
            if not pd.isnull(tib_name_2.iloc[0]):
                possible_individuals[id].append(tib_name_2.iloc[0])
        ind_match = ind_sheet.loc[ind_sheet["ID"] == id]
        ind_name_1 = ind_match["names_tib"]
        if len(ind_name_1) > 0:
            if not pd.isnull(ind_name_1.iloc[0]):
                possible_individuals[id].append(ind_name_1.iloc[0])
        ind_name_2 = ind_match["names_skt"]
        if len(ind_name_2) > 0:
            if not pd.isnull(ind_name_2.iloc[0]):
                possible_individuals[id].append(ind_name_2.iloc[0])
    return possible_individuals

def strip_name(name):
    pattern = r'\/'
    pattern2 = r' \(k\)'
    name = re.sub(pattern, '', name)
    mod_name = re.sub(pattern2, '', name)
    return mod_name

for text in root.findall("default:text", ns):
    bibl = text.find("default:bibl", ns)
    toh_num = bibl.attrib["key"][3:]
    work = bibl.find("./{http://read.84000.co/ns/1.0}work[@type='tibetanSource']")
    #find toh_num in spreadsheet
    spread_num = "D" + toh_num
    #should check to make sure there is a match, not the case if there is a hyphen
    kangyur_match = kangyur_sheet.loc[kangyur_sheet["ID"] == spread_num]
    if kangyur_match.empty:
        unmatched_texts["Toh"].append(bibl.attrib["key"])
    #add roles from spreadsheet
    #get lists of roles, and lists of names
    person_ids = kangyur_match["identification"]
    roles = kangyur_match["role"]
    kangyur_names = kangyur_match["indicated value"]
    attributions = work.findall("default:attribution", ns)
    labels = work.findall("./{http://read.84000.co/ns/1.0}attribution/{http://read.84000.co/ns/1.0}label")
    if len(attributions) > 0:
        #get the names that are already in the 84000 spreadsheet
        possible_individuals = find_possible_individuals(person_ids, kangyur_names)
        for attribution in attributions:
            #make the name into more searchable format
            label = attribution.find("default:label", ns)
            name_84000 = strip_name(label.text)
            id_84000 = attribution.attrib["resource"]
            print(f"Looking for matches for person {name_84000} from toh {toh_num}")
            matched = False
            for bdrc_id, bdrc_names in possible_individuals.items():
                for bdrc_name in bdrc_names:
                    print(f"checking {bdrc_name} against {name_84000}")
                    if re.search(name_84000, bdrc_name, re.IGNORECASE):
                        #update the attributions
                        #add role that matches with the BDRC id
                        matched = True
                        print("match found")
                        person = kangyur_match.loc[kangyur_match["identification"] == bdrc_id]
                        role = person["role"].item()
                        print(f"adding role {role}")
                        if attribution.attrib["role"]:
                            attribution.attrib["role2"] = role
                        else:
                            attribution.attrib["role"] = role
                        #add sameAs element with BDRC number
                        print(f"same as bdrc {bdrc_id}")
                        sameAs = ET.SubElement(attribution, "owl:sameAs")
                        person_uri = "http://purl.bdrc.io/resource/" + bdrc_id
                        sameAs.attrib["rdf:resource"] = person_uri
                        #add alternate role?
                        break
                if matched:
                    if id_84000 not in person_matches["84000 ID"]:
                        person_matches["84000 ID"].append(id_84000)
                        person_matches["BDRC ID"].append(bdrc_id)
                    break
            if not matched:
                print("no matches found")
                if id_84000 not in unmatched_persons["84000 ID"] and possible_individuals not in  unmatched_persons["possible BDRC matches"]:
                    unmatched_persons["84000 ID"].append(id_84000)
                    unmatched_persons["84000 name"].append(name_84000)
                    unmatched_persons["possible BDRC matches"].append(possible_individuals)
    else:
        if len(roles) == 0:
            unattributed_texts["84000 ID"].append(bibl.attrib["key"])
        for (idx, role) in enumerate(roles):
            attribution = ET.SubElement(work, "attribution")
            attribution.attrib["role"] = role
            #add a label with corresponding name
            label = ET.SubElement(attribution, "label")
            label.text = kangyur_names.iloc[idx]
            sameAs= ET.SubElement(attribution, "owl:sameAs")
            if type(person_ids.iloc[idx]) is str:
                person_uri = "http://purl.bdrc.io/resource/" + person_ids.iloc[idx]
            sameAs.attrib["rdf:resource"] = person_uri
#some query to get associated places, likely from BDRC
breakpoint()
#export CSV with matching ID's
matches_df = pd.DataFrame(person_matches)
matches_df.to_csv("person_matches.csv")
unmatched_df = pd.DataFrame(unmatched_persons)
unmatched_df.to_csv("unmatched_persons.csv", encoding='utf-8')
unmatched_texts_df = pd.DataFrame(unmatched_texts)
unmatched_texts_df.to_csv("unmatched_texts.csv")
unattributed_texts_df = pd.DataFrame(unattributed_texts)
unattributed_texts_df.to_csv("unattributed_texts.csv")
#write to file


tree.write("new-kangyur-data-test.xml")