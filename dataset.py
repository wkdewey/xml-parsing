import re
import pandas as pd
import xml.etree.ElementTree as ET

class Dataset:
    def __init__(self, texts, ns, kangyur_sheet, tib_sheet, ind_sheet, attribution_langs, WD_person_matches):
        self.texts = []
        self.kangyur_sheet = kangyur_sheet
        self.tib_sheet = tib_sheet
        self.ind_sheet = ind_sheet
        self.attribution_langs = attribution_langs
        self.initialize_texts(texts, WD_person_matches, ns)

    def initialize_texts(self, texts, WD_person_matches, ns):
        for text in texts:
            bibls = text.findall("default:bibl", ns)
            text_obj = Text(bibls, self.kangyur_sheet, self.tib_sheet, self.ind_sheet, self.attribution_langs, WD_person_matches, ns)
            self.texts.append(text_obj)

class Text:
    def __init__(self, bibls, kangyur_sheet, tib_sheet, ind_sheet, attribution_langs, WD_person_matches, ns):
        self.works = []
        self.bibls = bibls
        self.initialize_works(bibls, kangyur_sheet, tib_sheet, ind_sheet, attribution_langs, WD_person_matches, ns)
        if len(self.works) > 1:
            self.find_matches()
    
    def initialize_works(self, bibls, kangyur_sheet, tib_sheet, ind_sheet, attribution_langs, WD_person_matches, ns):
        for bibl in bibls:
            works = bibl.findall("./{http://read.84000.co/ns/1.0}work[@type='tibetanSource']")
            for work_element in works:
                work_obj = Work(bibl, work_element, kangyur_sheet, tib_sheet, ind_sheet, attribution_langs, WD_person_matches, ns)
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
    def __init__(self, bibl, work_element, kangyur_sheet, tib_sheet, ind_sheet, attribution_langs, WD_person_matches, ns):
        self.attributions = []
        self.bibl = bibl
        self.work_element = work_element
        # bdrc_id = work_element.find("owl:sameAs", ns).attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource']
        # self.bdrc_id = bdrc_id.split("/")[-1]
        self.title = self.work_element.find("default:label", ns).text
        self.bdrc_id = self.find_bdrc_id(ns)
        self.toh_num = bibl.attrib["key"][3:]
        self.spread_num = "D" + self.toh_num
        self.kangyur_match = kangyur_sheet.loc[kangyur_sheet["ID"] == self.spread_num]
        self.person_ids = self.kangyur_match["identification"]
        self.roles = self.kangyur_match["role"]
        self.kangyur_names = self.kangyur_match["indicated value"]
        self.possible_individuals = self.find_possible_individuals(tib_sheet, ind_sheet)
        self.initialize_attributions(attribution_langs, WD_person_matches, ns)
        if self.kangyur_match.empty:
            Output.unmatched_works["Toh"].append(bibl.attrib["key"])
            if self.attributions:
                Output.unmatched_works["has_attributions"].append(True)
                self.spread_num = "D" + self.toh_num
                self.add_missing_attributions(self.attributions)
            else:
                Output.unmatched_works["has_attributions"].append(False)
        

    def initialize_attributions(self, attribution_langs, WD_person_matches, ns):
        attributions = self.work_element.findall("default:attribution", ns)
        for attribution_element in attributions:
            attribution_obj = Attribution(attribution_element, self.possible_individuals, self.toh_num, self.kangyur_match, self.title, self.bdrc_id, attribution_langs, WD_person_matches, ns)
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

    def add_or_update_attributions(self, person, person_matches):
        # ids_84000 = str(getattr(person, "text_84000_ids"))
        # for attribution in self.attributions:
        #     print(attribution.id_84000, ids_84000)
        #     if attribution.id_84000 in ids_84000:
        #         attribution.update_attribution(person, person_matches)
        #         return
        # self.add_attribution(person)
        bdrc_id = str(getattr(person, "identification"))
        for attribution in self.attributions:
            print(attribution.bdrc_id, bdrc_id)
            if attribution.bdrc_id == bdrc_id and not attribution.updated:
                #how can you tell which ones have been seen?
                attribution.update_attribution(person, person_matches)
                return
        self.add_attribution(person)
        

    def add_attribution(self, person):
        attribution = ET.SubElement(self.work_element, "attribution")
        role = getattr(person, "role")
        number = re.search("\d", role)
        if number:
            number = number.group(0)
            role = ''.join(re.split("\d", role))
            attribution.attrib["role"] = role
            attribution.attrib["revision"] = number
        name = getattr(person, "indicated_value")
        role = re.sub(r"revisor", "reviser", role)
        attribution.attrib["role"] = role
        print(f"New attribution on work toh{self.toh_num} for person/place with name {name} and role {role}")
        bdrc_id = str(getattr(person, "identification")).split(" ")[0]
        if bdrc_id[0] not in "PG":
            bdrc_id = "unknown"
        ids_84000 = str(getattr(person, "text_84000_ids"))
        if ids_84000 == 'nan':
            ids_84000 = "unknown"
        if ids_84000[0] == "{":
            id_84000 = ids_84000.split("'")[1]
            attribution.attrib["resource"] = id_84000
        lang = "bo-Latn"
        label = ET.SubElement(attribution, "label")
        label.text = name
        label.attrib["lang"] = lang
        if type(bdrc_id) == str and bdrc_id != "unknown":
            sameAs = ET.SubElement(attribution, "owl:sameAs")
            person_uri = "http://purl.bdrc.io/resource/" + bdrc_id
            sameAs.attrib["rdf:resource"] = person_uri
        Output.new_attributions["toh"].append(self.toh_num)
        Output.new_attributions["name"].append(name)
        Output.new_attributions["role"].append(role)
        Output.new_attributions["BDRC ID"].append(bdrc_id)
        Output.new_attributions["possible 84000 IDs"].append(ids_84000)
        Output.new_attributions["lang"].append(lang)

    def add_bdrc_id(self, kangyur_sheet):
        kangyur_sheet.loc[kangyur_sheet["ID"] == self.spread_num, 'text_bdrc_id'] = self.bdrc_id

    def find_matching_attributions(self, sheet):
        return sheet.loc[sheet["ID"] == self.spread_num.split("-")[0]]


    def add_missing_attributions(self, attributions):
        for attribution in attributions:
            Output.attributions_to_add["ID"].append("D" + self.toh_num)
            Output.attributions_to_add["title"].append(self.title)
            Output.attributions_to_add["role"].append(attribution.role)
            if hasattr(attribution, "bdrc_id"):
                Output.attributions_to_add["identification"].append(attribution.bdrc_id)
            else:
                Output.attributions_to_add["identification"].append("unknown")
            Output.attributions_to_add["indicated_value"].append(attribution.name_84000)
            Output.attributions_to_add["text_bdrc_id"].append(self.bdrc_id)
            Output.attributions_to_add["text_84000_ids"].append(attribution.id_84000)
            Output.attributions_to_add["attribution_lang"].append(attribution.lang)
            attribution.added = True

class Attribution:

    def __init__(self, attribution_element, possible_individuals, toh_num, kangyur_match, title, text_bdrc_id, attribution_langs, WD_person_matches, ns):
        self.attribution_element = attribution_element
        self.possible_individuals = possible_individuals
        self.label = self.attribution_element.find("default:label", ns)
        self.name_84000 = Attribution.strip_name(self.label.text)
        self.id_84000 = ""
        self.lang = ""
        if "resource" in self.attribution_element.attrib:
            self.id_84000 = self.attribution_element.attrib["resource"]
        if "lang" in self.attribution_element.attrib:
            self.lang = self.attribution_element.attrib["lang"]
        elif self.id_84000:
            lang_attribute = attribution_langs.loc[attribution_langs["name"] == self.name_84000, 'lang']
            if len(lang_attribute) > 0:
                self.lang = lang_attribute.values[0]
        self.role = self.attribution_element.attrib["role"]
        self.toh_num = toh_num
        self.title = title
        self.kangyur_match = kangyur_match
        self.bdrc_id = self.find_bdrc_id(WD_person_matches)
        self.text_bdrc_id = text_bdrc_id
        self.updated = False
        self.added = False
        Output.existing_attributions["toh"].append(self.toh_num)
        Output.existing_attributions["name"].append(self.name_84000)
        Output.existing_attributions["role"].append(self.role)
        Output.existing_attributions["84000 ID"].append(self.id_84000)
        Output.existing_attributions["lang"].append(self.lang)

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
    
    def update_attribution(self, person, person_matches):
        # person = self.kangyur_match.loc[self.kangyur_match["identification"] == bdrc_id]
        print(f"updating attribution for 84000 id {self.id_84000}")
        new_role = getattr(person, "role")
        print(f"current role is {self.role} new role is {new_role}")
        self.role = new_role
        number = re.search("\d", self.role)
        if number:
            number = number.group(0)
            self.role = ''.join(re.split("\d", self.role))
            self.attribution_element.attrib["role"] = self.role
            self.attribution_element.attrib["revision"] = number
        self.role = re.sub(r"revisor", "reviser", self.role)
        # lang = getattr(person, "attribution_lang")
        self.bdrc_id = getattr(person, "identification").split(" ")[0]
        possible_matches = person_matches.loc[person_matches["BDRC ID"] == self.bdrc_id, "84000 ID"]
        if len(possible_matches) > 0:
            self.id_84000 = possible_matches.values[0]
        
        self.attribution_element.attrib["role"] = self.role
        label = self.attribution_element.find("{http://read.84000.co/ns/1.0}label")
        label.attrib["lang"] = self.lang + "-Latn"
        self.attribution_element.attrib["resource"] = self.id_84000
        print(f"same as bdrc {self.bdrc_id}")
        sameAs = ET.SubElement(self.attribution_element, "owl:sameAs")
        if self.bdrc_id[0] == "P":
            person_uri = "http://purl.bdrc.io/resource/" + self.bdrc_id
            sameAs.attrib["rdf:resource"] = person_uri
        self.updated = True
    
    def find_matches(self):
        matched = False
        print(f"Looking for matches for person {self.name_84000} from toh {self.toh_num}")
        #see if the attribution has a match
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
        if not matched and not self.added:
            print("no matches found")

            if self.id_84000 not in Output.unmatched_persons["84000 ID"] and self.possible_individuals not in Output.unmatched_persons["possible BDRC matches"]:
                Output.unmatched_persons["toh"].append(self.toh_num)
                Output.unmatched_persons["84000 ID"].append(self.id_84000)
                Output.unmatched_persons["84000 name"].append(self.name_84000)
                Output.unmatched_persons["possible BDRC matches"].append(self.possible_individuals)
            Output.attributions_to_add["ID"].append("D" + self.toh_num)
            Output.attributions_to_add["title"].append(self.title)
            Output.attributions_to_add["role"].append(self.role)
            if hasattr(self, "bdrc_id"):
                Output.attributions_to_add["identification"].append(self.bdrc_id)
            else:
                Output.attributions_to_add["identification"].append("unknown")
            Output.attributions_to_add["indicated_value"].append(self.name_84000)
            Output.attributions_to_add["text_bdrc_id"].append(self.text_bdrc_id)
            Output.attributions_to_add["text_84000_ids"].append(self.id_84000)
            Output.attributions_to_add["attribution_lang"].append(self.lang)
            self.added = True

    def find_bdrc_id(self, person_matches):
        bdrc_id = "unknown"
        match = person_matches.loc[person_matches["84000 ID"] == self.id_84000, "BDRC ID"]
        if len(match) > 0:
            bdrc_id = match.values[0]
        return bdrc_id

    def find_matching_attributions(self, sheet):
        work_matches = sheet.loc[sheet["ID"] == "D" + self.toh_num]
        if len(work_matches) == 0:
            return None
        matches = work_matches.loc[work_matches["identification"] == self.bdrc_id]
        if len(matches) > 1:
            matches = matches.loc[matches["indicated_value"] == self.name_84000]
            person = list(matches.itertuples())[0]
        else:
            person = list(matches.itertuples())[0]
            return person

class Output:
    person_matches = { "84000 ID": [], "BDRC ID": []}
    unmatched_persons = { "toh": [], "84000 ID": [], "84000 name": [], "possible BDRC matches": []}
    unmatched_works = {"Toh": [], "has_attributions": []}
    matchable_works = {"matched_toh": [], "unmatched_toh": []}
    attributable_works = {"attributed_toh": [], "unattributed_toh": []}
    unattributed_works = { "84000 ID": []}
    discrepant_roles = { "toh": [], "84000 ID": [], "84000 name": [],"BDRC ID": [], "84000 role": [], "BDRC role": []}
    existing_attributions = { "toh": [], "name": [], "role": [], "84000 ID": [], "lang": [] }
    new_attributions = { "toh": [], "name": [], "role": [], "BDRC ID": [], "possible 84000 IDs": [], "lang": []}
    attributions_to_add = {"ID": [], "title": [], "role": [], "identification": [], "indicated_value": [], "text_bdrc_id": [], "text_84000_ids": [], "attribution_lang": []}