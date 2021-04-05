
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
dataset = Dataset(texts, ns, kangyur_sheet, tib_sheet, ind_sheet)

for text in dataset.texts:
    for work in text.works:
        if len(work.attributions) > 0:
            for attribution in work.attributions:
                attribution.find_matches()
        else:
            work.find_unattributed_works()
            # work.add_attributions()
#some query to get associated places, likely from BDRC
matches_df = pd.DataFrame(Output.person_matches)
matches_df.to_csv("person_matches.csv")
unmatched_df = pd.DataFrame(Output.unmatched_persons)
unmatched_df.to_csv("unmatched_persons.csv", encoding='utf-8')
unmatched_works_df = pd.DataFrame(Output.unmatched_works)
unmatched_works_df.to_csv("unmatched_works.csv")
matchable_works_df = pd.DataFrame(Output.matchable_works)
matchable_works_df.to_csv("matchable_works.csv")
unattributed_works_df = pd.DataFrame(Output.unattributed_works)
unattributed_works_df.to_csv("unattributed_works.csv")
attributable_works_df = pd.DataFrame(Output.attributable_works)
attributable_works_df.to_csv("attributable_works.csv")
discrepant_roles_df = pd.DataFrame(Output.discrepant_roles)
discrepant_roles_df.to_csv("discrepant_roles.csv", encoding='utf-8')
tree.write("new-kangyur-data-test.xml")