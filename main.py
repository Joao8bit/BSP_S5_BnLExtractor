#!/usr/bin/python3
"""
Import section:
All imports were thought following good practice methods
"""
import os
import src.xml.xml_manipulation as xml
import src.csv.csv as csv
import src.nlp.spacy as spacy
import pandas as pd
from multiprocessing import Process

"""
CSV CREATION STEPS
"""
def get_csv_data(root_dir, tree):
    """
    This function will gather all the information about a single XML file that will be written
    Inside the CSV file, along with the language detection data.
    """
    #This will be the full row data list
    full_data=[] 
    #This is the xml part of the data, only tag extraction
    xml_data = [xml.extract_tag(tree, xml.tag_dict["source"]),
                xml.extract_tag(tree, str(xml.tag_dict["date"])),
                xml.extract_tag(tree, xml.tag_dict["publisher"]),
                xml.extract_tag(tree, xml.tag_dict["description"])
                ]
    #This is the language detection data
    spacy_data = spacy.get_lang(xml.extract_tag(tree, xml.tag_dict["description"]))
    xml_data.append(spacy_data["language"])
    xml_data.append(spacy_data["score"])
    full_data = xml_data
    return full_data

def write_to_csv(root_dir, file_list, csv_name):
    """
    Opens a csv file, writes the header (Source, Date, Publisher and Description).
    Then, writes in a sequence all extracted tag data from XML files.
    """
    with open(csv_name, 'w', encoding='UTF8') as f:
        # Opens the CSV and writes the Header titles
        csv.writer(f).writerow(csv.header)
        # For each file, tag data will be extracted, and written into the CSV file
        for file in file_list:
            tree = xml.open_xml(root_dir, file)
            file_data = get_csv_data(root_dir, tree)
            csv.writer(f).writerow(file_data)
    f.close()

def filter_csv(filename, index):
    #Read CSV file
    df = pd.read_csv(filename)
    #Filter CSV by target Lnguage
    df = df[(df['Language']=='fr') | (df['Language']=='de')]
    df[df['Language']=='fr'].to_csv('Ads'+str(index)+'FR.csv', index=False)
    df[df['Language']=='de'].to_csv('Ads'+str(index)+'DE.csv', index=False)

def main_csv():
    """
    1. XML to CSV file transition
    
    This function writes csv files, divided in 30 000 rows each
    Where each row is composed of:
        - Source 
        - Date 
        - Publisher 
        - Description
        - Language
        - Score
    Each and every row gets its data extracted from the XML files in columns, 
    While the Language and Score columns get their data using spaCy langdetect.

    2. CSV extraction

    The second step writes all CSV rows into several smaller-sized CSV files,
    separated by four processes for performance reasons.

    3. CSV language filter

    The last step will create a single CSV file for each language,
    gathering all data from all previous generated files.

    DE: AdsFullDE
    FR: AdsFullFR
    """
    #Variables declaration
    root_dir = './ADS/'
    files = os.listdir(root_dir)
    range1 = files[:30000]
    range2 = files[30000:60000]
    range3 = files[60000:90000]
    range4 = files[100000:140000]
    range_total = len(range1+range2+range3+range4)

    process_1 = Process(target=write_to_csv, args=(root_dir,  range1, './advertisements1.csv'))
    process_2 = Process(target=write_to_csv, args=(root_dir,  range2, './advertisements2.csv'))
    process_3 = Process(target=write_to_csv, args=(root_dir,  range3, './advertisements3.csv'))
    process_4 = Process(target=write_to_csv, args=(root_dir,  range3, './advertisements4.csv'))
    print('Writing to CSV and analysing language...')

    process_1.start()
    process_2.start()
    process_3.start()
    process_4.start()
    process_1.join()
    process_2.join()
    process_3.join()
    process_4.join()
    print('Operation complete!')

    filter_csv('advertisements1.csv', 1)  
    filter_csv('advertisements2.csv', 2)
    filter_csv('advertisements3.csv', 3)
    filter_csv('advertisements4.csv', 4)

    csv.csv_concatenator('Ads1FR.csv', 'Ads2FR.csv', 'Ads12FR.csv')
    csv.csv_concatenator('Ads3FR.csv', 'Ads4FR.csv', 'Ads34FR.csv')
    csv.csv_concatenator('Ads12FR.csv', 'Ads12FR.csv', 'AdsFullFR.csv')

    csv.csv_concatenator('Ads1DE.csv', 'Ads2DE.csv', 'Ads12DE.csv')
    csv.csv_concatenator('Ads3DE.csv', 'Ads4DE.csv', 'Ads34DE.csv')
    csv.csv_concatenator('Ads12DE.csv', 'Ads12DE.csv', 'AdsFullDE.csv')

if __name__=="__main__":
  main_csv()