class Database:
    def __init__(self, texts, ns):
        self.texts = []
        self.initialize_texts(self, texts, ns)

    def initialize_texts(self, texts, ns):
        for text in texts:
            bibls = text.findall("default:bibl", ns)
            text_obj = Text.new(bibls)
            self.texts.append(text_obj)

class Text:
    def __init__(self, bibls):
        self.works = []
        self.bibls = bibls
        self.initialize_works(self, bibls)
    
    def initialize_works(self, bibls):
        for bibl in bibls:

            self.works.append(Work.new(bibl))

class Work:
    def __init__(self):
