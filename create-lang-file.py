import pandas as pd
from pathlib import Path

language_path = '/users/williamdewey/Development/code/84000-data-rdf/xml-parsing/data-export/WD_BDRC_data_with_langs.xlsx'
languages = Path(language_path)
if languages.exists():
    WD_language_attributions = pd.read_excel(languages)
language_attributions = pd.DataFrame(WD_language_attributions)

names = set(language_attributions["indicated_value"].to_list())
matching_langs = []
for name in names:
    matching_lang = language_attributions.loc[language_attributions['indicated_value'] == name, "attribution_lang"].values[0]
    matching_langs.append(matching_lang)

language_matches = pd.DataFrame({"name": list(names), "lang": list(matching_langs)})
language_matches.to_excel("WD_language_attributions.xlsx")