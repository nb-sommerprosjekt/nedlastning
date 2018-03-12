import pymarc
import os
from lxml import etree as ET
import pickle

from bs4 import BeautifulSoup
import os

from difflib import SequenceMatcher
from nltk.tokenize import word_tokenize
import re

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def write_to_file(tittel,undertittel,year,tidsskrift, dewey,keyword,filnavn, folder):
    print("Sucessfully writing to file")
    with open(folder + "/meta-" + filnavn + ".txt", "w") as d:

        d.write("tittel:::" + str(tittel) + "\n")
        d.write("undertittel:::" + str(undertittel) + "\n")
        d.write("dewey:::" + str(dewey) + "\n")
        d.write("keyword:::" + str(keyword) + "\n")
        d.write("tidsskrift:::" + str(tidsskrift) + "\n")
        d.write("year:::" + str(year) + "\n")
        d.write("idunn:::yes"+"\n")

def save_like_titler(tittel,tittel2,filnavn):
    filnavn=filnavn.split("/")[-1]
    with open("destination/"+str(filnavn)+".txt", "w") as d:
        d.write(tittel+":::"+tittel2+":::"+str(similar(tittel,tittel2)))

def printRecur(root):
    """Recursively prints the tree."""
    if root.tag in ignoreElems:
        return
    try:
        if str(root.tag.title())=="Article-Title":
            title.append(root.text)
    except Exception as e:
        print(e)
    for elem in root.getchildren():
        printRecur(elem)

xml=0
rootdir="data"
destination="destination"
ignoreElems = ['displayNameKey', 'displayName']
title_texts={}

with open("title_torstein.pickle","rb") as f:
    titles=pickle.load(f)

with open('title_idunn.pickle', 'rb') as f:
    titles2=pickle.load(f)
perfect_titles={}
for t in titles:
    perfect_titles[t]=""
titles.sort()
titles2.sort()

print(len(titles))
print(len(titles2))



#print(similar("Blir handlingsrommet større med egen europaminister?".encode('utf-8'),"Blir  st\n\n\n\nørrpe med  europaminister?".encode('utf-8')))
title=[]
regex = re.compile('[^a-zA-Z1234567890øæåØÆÅ ]')
for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            if ".xml" in file:
                xml+=1
                #if xml%1000==0:
                print(xml)
                title = []
                relDir = os.path.relpath(subdir, rootdir)
                relFile = os.path.join(relDir, file)
                relFile=os.path.join(rootdir,relFile)
                soup = BeautifulSoup(open(relFile))    # txt is simply the a string with your XML file
                pageText = soup.findAll(text=True)
                text= ' '.join(pageText)
                try:
                    tree = ET.ElementTree(file=relFile)
                except Exception as e:
                    print(e)
                    continue
                root = tree.getroot()
                printRecur(root)

                if len(title)>0:
                    if title[0] is not None:
                        tittel=title[0].lower()
                        tittel=regex.sub("",tittel)
                        tokenized_tittel = word_tokenize(tittel, language="norwegian")
                        tittel=" ".join(tokenized_tittel)

                        title_texts[tittel] = text
                        #print(tittel)
                    else:
                        print("Title is None")
                else:
                    print("NO TITLE FOUND!!!!")

                max_sum=0
                closest_title=""
                if tittel in perfect_titles:
                    max_sum=1
                    closest_title=tittel
                else:
                    for a in titles:
                            if a is not None and tittel is not None:
                                temp=similar(a,tittel)
                                if  temp>max_sum:
                                    closest_title=a
                                    max_sum=temp

                if max_sum>0:
                    save_like_titler(tittel,closest_title,relFile.replace(".xml",""))

# for key in title_texts.keys():
#     print(key,len(title_texts[key]))
# titles_idunn=list(title_texts.keys())
# with open('title_idunn.pickle', 'wb') as f:
#     pickle.dump(titles_idunn, f)

with open('title_texts.pickle', 'wb') as f:
    pickle.dump(title_texts, f)







titles=[]

# filename = "norart.xml"
# print("Loading XML-records. Please wait")
# p=pymarc.marcxml.parse_xml_to_array(filename, strict=False, normalize_form=None)
# print("Loading Complete")
# count=0
# print("Starting scanning")
# for record in p:
#     if "082" in record  and "856" in record:
#                 tittel = record["245"]['a']
#                 undertittel = ""
#                 if "b" in record["245"]:
#                     undertittel = record["245"]['b']
#                 tidsskrift = ""
#                 year = ""
#                 if "773" in record:
#                     if "t" in record["773"]:
#                         tidsskrift = record["773"]["t"]
#                     if "i" in record["773"]:
#                         year = record["773"]["i"]
#                 dewey = record["082"]["a"]
#                 kategori = str(dewey[:3])
#                 keyword=""
#                 if "650" in record:
#                     keyword = record["650"]["a"]
#                 tittel=tittel+" "+ undertittel
#                 tittel=tittel.lower()
#                 tittel = regex.sub("", tittel)
#                 tokenized_tittel = word_tokenize(tittel, language="norwegian")
#                 tittel = " ".join(tokenized_tittel)
#                 titles.append(tittel)
#                 if tittel in title_texts:
#                     count+=1
#                     print (count)

#
# print(len(titles))
# with open('title_torstein.pickle', 'wb') as f:
#     pickle.dump(titles,f)

#

# print(len(titles)*len(titles2))
# for a in titles:
#     for b in titles2:
#         if a is not None and b is not None:
#             if similar(a,b)>0.90:
#                 print(a,b,similar(a,b))
#                 break
