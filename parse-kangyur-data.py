
import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
from dataset import Dataset, Output
import requests

# data_file = 'sample-data.xml'
# Note: change back to xml-parsing without the refactoring
data_file = "/Users/williamdewey/Development/code/84000-data-rdf/xml-parsing/data-export/kangyur-data.xml"
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

spreadsheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRoQ2LY-zLATi0XMd_MUhV94zAMkHLzxbAVHji4EtBLl2gAkzXJmKyq0alkd9B3HJsX-98D6mKzCoyL/pub?output=xlsx"
print("loading Kangyur spreadsheet")
r = requests.get(spreadsheet_url)
#is it possible to change file paths so it's not hardcorded?
spreadsheet_path = '/users/williamdewey/Development/code/84000-data-rdf/xml-parsing/data-export/ATII - Tentative template.xlsx'
with open(spreadsheet_path, 'wb') as f:
    f.write(r.content)
spreadsheet = Path(spreadsheet_path)
kangyur_sheet = ""
if spreadsheet.exists():
    kangyur_sheet = pd.read_excel(spreadsheet, sheet_name = "DergeKangyur")
    tib_sheet = pd.read_excel(spreadsheet, sheet_name = "Persons-Tib")
    ind_sheet = pd.read_excel(spreadsheet, sheet_name = "Persons-Ind")
matches_path = '/users/williamdewey/Development/code/84000-data-rdf/xml-parsing/data-export/WD_identified_person_matches.xlsx'
matches = Path(matches_path)
WD_person_matches = ""
if matches.exists():
    WD_person_matches = pd.read_excel(matches, sheet_name = "WD_person_matches")
missing_path = '/users/williamdewey/Development/code/84000-data-rdf/xml-parsing/data-export/WD_missing_entries.xlsx'
missing = Path(missing_path)
WD_missing_entries = ""
if missing.exists():
    WD_missing_entries = pd.read_excel(missing)
dataset = Dataset(texts, ns, kangyur_sheet, tib_sheet, ind_sheet)

for text in dataset.texts:
    for work in text.works:
        if len(work.attributions) > 0:
            for attribution in work.attributions:
                attribution.find_matches()
        else:
            work.find_unattributed_works()
        work.add_bdrc_id(kangyur_sheet)
#some query to get associated places, likely from BDRC
matches_df = pd.DataFrame(Output.person_matches)
unmatched_df = pd.DataFrame(Output.unmatched_persons)
unmatched_works_df = pd.DataFrame(Output.unmatched_works)
matchable_works_df = pd.DataFrame(Output.matchable_works)
unattributed_works_df = pd.DataFrame(Output.unattributed_works)
attributable_works_df = pd.DataFrame(Output.attributable_works)
discrepant_roles_df = pd.DataFrame(Output.discrepant_roles)
with pd.ExcelWriter("discrepancies.xlsx") as writer:
    unmatched_df.to_excel(writer, sheet_name='unmatched persons')
    unmatched_works_df.to_excel(writer, sheet_name='unmatched works')
    unattributed_works_df.to_excel(writer, sheet_name='unattributed works')
    matchable_works_df.to_excel(writer, sheet_name="matchable works")
    attributable_works_df.to_excel(writer, sheet_name='attributable works')
    discrepant_roles_df.to_excel(writer, sheet_name='discrepant roles')

all_person_matches = pd.concat([matches_df, WD_person_matches], axis = 0)
bdrc_ids = set(all_person_matches["BDRC ID"].to_list())
ids_84000 = []
for bdrc_id in bdrc_ids:
    matching_ids = all_person_matches.loc[all_person_matches['BDRC ID'] == bdrc_id, "84000 ID"].to_list()
    matching_ids = set(matching_ids)
    ids_84000.append(matching_ids)
grouped_matches = pd.DataFrame({ "BDRC ID": list(bdrc_ids), "84000 ID": ids_84000})

for bdrc_id in bdrc_ids:
    id_84000 = grouped_matches.loc[grouped_matches['BDRC ID'] == bdrc_id, "84000 ID"].values[0]
    kangyur_sheet.loc[kangyur_sheet['identification'] == bdrc_id, 'text_84000_ids'] = str(id_84000)
with pd.ExcelWriter("all_person_matches.xlsx") as writer:
    all_person_matches.to_excel(writer, sheet_name='person matches')
    grouped_matches.to_excel(writer, sheet_name='grouped matches')
final_sheet = pd.concat([kangyur_sheet, WD_missing_entries], axis=0)
final_sheet.to_excel("WD_BDRC_data.xlsx", sheet_name='DergeKangyur')

for text in dataset.texts:
    for work in text.works:
        spread_attributions = work.find_matching_attributions(final_sheet)
        for person in spread_attributions.itertuples():
            work.add_or_update_attributions(person)
new_attributions_df = pd.DataFrame(Output.new_attributions)
new_attributions_df.to_excel("new_attributions.xlsx")

tree.write("new-kangyur-data.xml")