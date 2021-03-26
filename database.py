class Database:
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
            for work in works:
                work_obj = Work(self. bibl, kangyur_sheet)
                self.works.append(work)

class Work:
    def __init__(self, bibl, kangyur_sheet):
        self.attributions = []
        self.toh_num = bibl.attrib["key"][3:]
        self.spread_num = "D" + self.toh_num
        kangyur_match = kangyur_sheet.loc[kangyur_sheet["ID"] == spread_num]
        self.initialize_attributions(self)

    def initialize_attributions(self):
        pass
