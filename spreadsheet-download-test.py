#urllib.request method
# import urllib.request
# spreadsheet_url = "https://docs.google.com/spreadsheets/d/1BLhfPjUdtwt6JS_yZG5NXqcHA7e9IGFHaLsBH-y3igg/"
# urllib.request.urlretrieve(spreadsheet_url, '/users/williamdewey/Development/code/84000-data-rdf/xml-parsing/data-export/ATII - Tentative template.xlsx')

import requests
# spreadsheet_url = "https://docs.google.com/spreadsheets/d/1BLhfPjUdtwt6JS_yZG5NXqcHA7e9IGFHaLsBH-y3igg/"
spreadsheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRoQ2LY-zLATi0XMd_MUhV94zAMkHLzxbAVHji4EtBLl2gAkzXJmKyq0alkd9B3HJsX-98D6mKzCoyL/pub?output=xlsx"
r = requests.get(spreadsheet_url)

with open('/users/williamdewey/Development/code/84000-data-rdf/xml-parsing/data-export/ATII - Tentative template.xlsx', 'wb') as f:
    f.write(r.content)

print(r.status_code)
print(r.headers['content-type'])
print(r.encoding)