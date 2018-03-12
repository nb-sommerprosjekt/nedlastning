import pickle
import os
import pymarc
import re
from nltk.tokenize import word_tokenize
# This document extract titles from norart, loads the titles from idunn from a pickle dump, and tries  to create meta data for any correct matches that has been found. 

def create_norart_titles():
    titles=[]
    regex = re.compile('[^a-zA-Z1234567890øæåØÆÅ ]')
    filename = "norart20180108.xml"
    print("Loading XML-records. Please wait")
    p=pymarc.marcxml.parse_xml_to_array(filename, strict=False, normalize_form=None)
    print("Loading Complete")
    count=0
    print("Starting scanning")
    for record in p:
        if "082" in record  and "856" in record:
                    tittel = record["245"]['a']
                    undertittel = ""
                    if "b" in record["245"]:
                        undertittel = record["245"]['b']
                    tidsskrift = ""
                    year = ""
                    if "773" in record:
                        if "t" in record["773"]:
                            tidsskrift = record["773"]["t"]
                        if "i" in record["773"]:
                            year = record["773"]["i"]
                    dewey = record["082"]["a"]
                    kategori = str(dewey[:3])
                    keyword=""
                    if "650" in record:
                        keyword = record["650"]["a"]
                    tittel=tittel+" "+ undertittel
                    tittel=tittel.lower()
                    tittel = regex.sub("", tittel)
                    tokenized_tittel = word_tokenize(tittel, language="norwegian")
                    tittel = " ".join(tokenized_tittel)
                    titles.append(tittel)
                    print(count)
                    count+=1


    print(len(titles))
    with open('title_torstein.pickle', 'wb') as f:
        pickle.dump(titles,f)


def write_to_file_meta(tittel,undertittel,year,tidsskrift, dewey,keyword,filnavn, folder):
    print("Sucessfully writing to file")
    with open(folder + "/meta-" + filnavn + ".txt", "w") as d:

        d.write("tittel:::" + str(tittel) + "\n")
        d.write("undertittel:::" + str(undertittel) + "\n")
        d.write("dewey:::" + str(dewey) + "\n")
        d.write("keyword:::" + str(keyword) + "\n")
        d.write("tidsskrift:::" + str(tidsskrift) + "\n")
        d.write("year:::" + str(year) + "\n")
        d.write("idunn:::yes"+"\n")

def write_to_file_text(text,filnavn,folder):
    with open(folder + "/" + filnavn + ".txt", "w") as d:
        d.write(text)

# create_norart_titles()
# exit(0)
with open("idunn_to_norart.pickle","rb") as f:
    idunn_to_norart=pickle.load(f)
with open("norart_to_idunn.pickle","rb") as f:
    norart_to_idunn=pickle.load(f)
with open("title_texts.pickle","rb") as f:
    title_texts=pickle.load(f)

unmatched_norart={}


folder="documents"
regex = re.compile('[^a-zA-Z1234567890øæåØÆÅ ]')
filename = "norart20180108.xml"
print("Loading XML-records. Please wait")
p=pymarc.marcxml.parse_xml_to_array(filename, strict=False, normalize_form=None)
print("Loading Complete")
count=0
print("Starting scanning")
count=0
for record in p:
    if "082" in record  and "856" in record:
                tittel = record["245"]['a']
                print(count)
                count += 1
                original_tittel=tittel
                undertittel = ""
                if "b" in record["245"]:
                    undertittel = record["245"]['b']
                tidsskrift = ""
                year = ""
                if "773" in record:
                    if "t" in record["773"]:
                        tidsskrift = record["773"]["t"]
                    if "i" in record["773"]:
                        year = record["773"]["i"]
                dewey = record["082"]["a"]
                kategori = str(dewey[:3])
                keyword=""
                if "650" in record:
                    keyword = record["650"]["a"]
                tittel=tittel+" "+ undertittel
                tittel=tittel.lower()
                tittel = regex.sub("", tittel)
                tokenized_tittel = word_tokenize(tittel, language="norwegian")
                tittel = " ".join(tokenized_tittel)
                text=""
                if tittel in title_texts:
                    text=title_texts[tittel]
                elif tittel in norart_to_idunn:
                    text=title_texts[norart_to_idunn[tittel]]

                if text!="":

                    filnavn="".join(tokenized_tittel)
                    write_to_file_meta(original_tittel,undertittel,year,tidsskrift,dewey,keyword,filnavn,folder)
                    write_to_file_text(text,filnavn,folder)
                    pass
                if text=="":
                    unmatched_norart[tittel]=original_tittel
print(len(unmatched_norart.keys()))
with open("unmatched_articles_norart.pickle","wb") as f:
    pickle.dump(unmatched_norart,f)
