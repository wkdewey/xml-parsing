#import the necessary modules
import xml.etree.ElementTree as ET
#load the XML file/copy the file?
tree = ET.parse('sample-data.xml')
root = tree.getroot()
#import the BDRC spreadsheet

#iterate through XML entries (texts)

#get ID from spreadsheet

#match with ID in this doc

#add IDs from spreadsheet

#add roles from spreadsheet

#some query to get associated places, likely from BDRC

#write to file, probably