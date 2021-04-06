import re
import pandas as pd
import xml.etree.ElementTree as ET

class Dataset:
    def __init__(self, texts, ns, kangyur_sheet, tib_sheet, ind_sheet):
        self.texts = []
        self.kangyur_sheet = kangyur_sheet
        self.tib_sheet = tib_sheet
        self.ind_sheet = ind_sheet
        self.initialize_texts(texts, ns)

    def initialize_texts(self, texts, ns):
        for text in texts:
            bibls = text.findall("default:bibl", ns)
            text_obj = Text(bibls, self.kangyur_sheet, self.tib_sheet, self.ind_sheet, ns)
            self.texts.append(text_obj)

class Text:
    def __init__(self, bibls, kangyur_sheet, tib_sheet, ind_sheet, ns):
        self.works = []
        self.bibls = bibls
        self.initialize_works(bibls, kangyur_sheet, tib_sheet, ind_sheet, ns)
        if len(self.works) > 1:
            self.find_matches()
    
    def initialize_works(self, bibls, kangyur_sheet, tib_sheet, ind_sheet, ns):
        for bibl in bibls:
            works = bibl.findall("./{http://read.84000.co/ns/1.0}work[@type='tibetanSource']")
            for work_element in works:
                work_obj = Work(bibl, work_element, kangyur_sheet, tib_sheet, ind_sheet, ns)
                self.works.append(work_obj)

    def find_matches(self):
        #finds texts where one work has a match in Kangyur and the other doesn't
        #or one work has attributions and the other doesn't
        matched = []
        attributed = []
        matching_texts = { "matched": [], "unmatched": [], "attributed": [], "unattributed": []}
        for work in self.works:
            matched.append(not work.kangyur_match.empty)
            attributed.append(len(work.attributions) > 0)
        if len(set(matched)) > 1:
            for work in self.works:
                if work.kangyur_match.empty:
                    matching_texts["unmatched"].append(work.toh_num)
                else:
                    matching_texts["matched"].append(work.toh_num)
            Output.matchable_works["matched_toh"].append(matching_texts["matched"])
            Output.matchable_works["unmatched_toh"].append(matching_texts["unmatched"])
        
        if len(set(attributed)) > 1:
            for work in self.works:            
                if len(work.attributions) == 0:
                    matching_texts["unattributed"].append(work.toh_num)
                else:
                    matching_texts["attributed"].append(work.toh_num)
            Output.attributable_works["attributed_toh"].append(matching_texts["attributed"])
            Output.attributable_works["unattributed_toh"].append(matching_texts["unattributed"])

        
        


class Work:
    def __init__(self, bibl, work_element, kangyur_sheet, tib_sheet, ind_sheet, ns):
        self.attributions = []
        self.bibl = bibl
        self.work_element = work_element
        # bdrc_id = work_element.find("owl:sameAs", ns).attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource']
        # self.bdrc_id = bdrc_id.split("/")[-1]
        self.bdrc_id = self.find_bdrc_id(ns)
        self.toh_num = bibl.attrib["key"][3:]
        self.spread_num = "D" + self.toh_num
        self.kangyur_match = kangyur_sheet.loc[kangyur_sheet["ID"] == self.spread_num]
        if self.kangyur_match.empty:
            Output.unmatched_works["Toh"].append(bibl.attrib["key"])
        self.person_ids = self.kangyur_match["identification"]
        self.roles = self.kangyur_match["role"]
        self.kangyur_names = self.kangyur_match["indicated value"]
        self.possible_individuals = self.find_possible_individuals(tib_sheet, ind_sheet)
        self.initialize_attributions(ns)

    def initialize_attributions(self, ns):
        attributions = self.work_element.findall("default:attribution", ns)
        for attribution_element in attributions:
            attribution_obj = Attribution(attribution_element, self.possible_individuals, self.toh_num, self.kangyur_match, ns)
            self.attributions.append(attribution_obj)

    def find_possible_individuals(self, tib_sheet, ind_sheet):
        possible_individuals = {}
        for (idx, id) in enumerate(self.person_ids):
            possible_individuals[id] = []
            kangyur_name = self.kangyur_names.iloc[idx]
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
    

    def find_unattributed_works(self):
        if len(self.roles) == 0:
            Output.unattributed_works["84000 ID"].append(self.bibl.attrib["key"])

    def find_bdrc_id(self, ns):
        bdrc_id = None
        sameAs = self.work_element.find("owl:sameAs", ns)
        url = ""
        if sameAs is not None:
            url = sameAs.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource']
        if url:
            bdrc_id = url.split("/")[-1]
        return bdrc_id

    def add_attributions(self):
        
        for (idx, role) in enumerate(self.roles):
            attribution = ET.SubElement(self.work_element, "attribution")
            attribution.attrib["role"] = role
            #add a label with corresponding name
            label = ET.SubElement(attribution, "label")
            label.text = self.kangyur_names.iloc[idx]
            sameAs= ET.SubElement(attribution, "owl:sameAs")
            if type(self.person_ids.iloc[idx]) is str:
                person_uri = "http://purl.bdrc.io/resource/" + self.person_ids.iloc[idx]
            sameAs.attrib["rdf:resource"] = person_uri
        # What do I need to do for the spreadsheet

    def add_bdrc_id(self, kangyur_sheet):
        kangyur_sheet.loc[kangyur_sheet["ID"] == self.spread_num, 'text_bdrc_id'] = self.bdrc_id

class Attribution:

    def __init__(self, attribution_element, possible_individuals, toh_num, kangyur_match, ns):
        self.attribution_element = attribution_element
        self.possible_individuals = possible_individuals
        self.label = attribution_element.find("default:label", ns)
        self.name_84000 = Attribution.strip_name(self.label.text)
        self.id_84000 = attribution_element.attrib["resource"]
        self.toh_num = toh_num
        self.kangyur_match = kangyur_match

    @staticmethod
    def strip_name(name):
        pattern = r'\/'
        pattern2 = r' \(k\)'
        name = re.sub(pattern, '', name)
        mod_name = re.sub(pattern2, '', name)
        return mod_name

    def find_discrepant_roles(self, bdrc_id):
        person = self.kangyur_match.loc[self.kangyur_match["identification"] == bdrc_id]
        role = person["role"].item()
        if self.attribution_element.attrib["role"]:
            Output.discrepant_roles["toh"].append(self.toh_num)
            Output.discrepant_roles["84000 ID"].append(self.id_84000)
            Output.discrepant_roles["84000 name"].append(self.name_84000)
            Output.discrepant_roles["BDRC ID"].append(bdrc_id)
            Output.discrepant_roles["84000 role"].append(self.attribution_element.attrib["role"])
            Output.discrepant_roles["BDRC role"].append(role)
    
    def update_attribution(self, bdrc_id):
        person = self.kangyur_match.loc[self.kangyur_match["identification"] == bdrc_id]
        role = person["role"].item()
        print(f"adding role {role}")

        self.attribution_element.attrib["role"] = role
        #add sameAs element with BDRC number
        print(f"same as bdrc {bdrc_id}")
        sameAs = ET.SubElement(self.attribution_element, "owl:sameAs")
        person_uri = "http://purl.bdrc.io/resource/" + bdrc_id
        sameAs.attrib["rdf:resource"] = person_uri

    
    
    def find_matches(self):
        matched = False
        print(f"Looking for matches for person {self.name_84000} from toh {self.toh_num}")
        for bdrc_id, bdrc_names in self.possible_individuals.items():
            for bdrc_name in bdrc_names:
                print(f"checking {bdrc_name} against {self.name_84000}")
                if re.search(self.name_84000, bdrc_name, re.IGNORECASE):
                    matched = True
                    print("match found")
                    if self.id_84000 not in Output.person_matches["84000 ID"]:
                        Output.person_matches["84000 ID"].append(self.id_84000)
                        Output.person_matches["BDRC ID"].append(bdrc_id)
                    self.find_discrepant_roles(bdrc_id)
                    break
        if not matched:
            print("no matches found")
            if self.id_84000 not in Output.unmatched_persons["84000 ID"] and self.possible_individuals not in Output.unmatched_persons["possible BDRC matches"]:
                Output.unmatched_persons["toh"].append(self.toh_num)
                Output.unmatched_persons["84000 ID"].append(self.id_84000)
                Output.unmatched_persons["84000 name"].append(self.name_84000)
                Output.unmatched_persons["possible BDRC matches"].append(self.possible_individuals)



class Output:
    person_matches = { "84000 ID": [], "BDRC ID": []}
    unmatched_persons = { "toh": [], "84000 ID": [], "84000 name": [], "possible BDRC matches": []}
    unmatched_works = {"Toh": []}
    matchable_works = {"matched_toh": [], "unmatched_toh": []}
    attributable_works = {"attributed_toh": [], "unattributed_toh": []}
    unattributed_works = { "84000 ID": []}
    discrepant_roles = { "toh": [], "84000 ID": [], "84000 name": [],"BDRC ID": [], "84000 role": [], "BDRC role": []}
    # correct_data = { "toh": [], "84000 ID": [], "BDRC ID": [], "84000 role": [], "BDRC role": []}