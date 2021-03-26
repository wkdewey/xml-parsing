class Dataset:
    def __init__(self, texts, ns, kangyur_sheet):
        self.texts = []
        self.kangyur_sheet = kangyur_sheet
        self.initialize_texts(self, texts, ns)

    def initialize_texts(self, texts, ns, kangyur_sheet):
        for text in texts:
            bibls = text.findall("default:bibl", ns)
            text_obj = Text(bibls)
            self.texts.append(text_obj)

class Text:
    def __init__(self, bibls):
        self.works = []
        self.bibls = bibls
        self.initialize_works(self, bibls)
    
    def initialize_works(self, bibls, kangyur_sheet):
        for bibl in bibls:
            works = bibl.findall("./{http://read.84000.co/ns/1.0}work[@type='tibetanSource']")
            for work_element in works:
                work_obj = Work(self, bibl, work_element, kangyur_sheet, ns)
                self.works.append(work_obj)

class Work:
    def __init__(self, bibl, work_element, kangyur_sheet, ns):
        self.attributions = []
        self.work_element = work_element
        self.toh_num = bibl.attrib["key"][3:]
        self.spread_num = "D" + self.toh_num
        kangyur_match = kangyur_sheet.loc[kangyur_sheet["ID"] == self.spread_num]
        if kangyur_match.empty:
            Output.unmatched_works["Toh"].append(bibl.attrib["key"])
        self.person_ids = kangyur_match["identification"]
        self.roles = kangyur_match["role"]
        self.kangyur_names = kangyur_match["indicated value"]
        self.initialize_attributions(self, ns)

    def initialize_attributions(self, ns):
        attributions = self.work_element.findall("default:attribution", ns)
        for attribution_element in attributions:
            attribution_obj = Attribution(self, self.person_ids, self.kangyur_names)


    def match_attributions(self):
        pass

    def add_attributions(self):
        pass

class Attribution:

    def __init__(self, person_ids, kangyur_names):
        possible_individuals = self.find_possible_individuals(person_ids, kangyur_names)

    def update_attribution(self):
        pass

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


class Output:

    person_matches = { "84000 ID": [], "BDRC ID": []}
    unmatched_persons = { "84000 ID": [], "84000 name": [], "possible BDRC matches": []}
    unmatched_works = {"Toh": []}
    unattributed_works = { "84000 ID": []}
    unmatched_texts = {"ID": []}
    unattributed_texts = {"ID": []}