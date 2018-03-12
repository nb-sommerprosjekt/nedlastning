import pandas as pd
import sys
import pickle
import os
import re
from shutil import move
from shutil import copy
from nltk.tokenize import word_tokenize
from langdetect import detect

data=[]
count=1
with open("allmatches.log") as logg:
	for line in logg.readlines():
		if "######" not in line:
			line=line.replace(" matches ","|||")
			line=line.replace("\n","")
			temp=line.split("|||")
			print(len(temp))
			if len(temp)==10:
				data.append(line.split("|||"))
				line=line.split("|||")
				if len(line[-1])<3:
					print(line[-1])
					print (count)
					count+=1


df=pd.DataFrame(data)
df.columns=["Idunn-tidsskrift","Idunn-forfatter","Idunn-tittel","Idunn-år","norart-tidsskrift","norart-forfatter", "norart-tittel","norart-år","norart-url","dewey"]
print(df)

with open("new_titler_adresse.pickle","rb") as f:
    new_titler_adresse=pickle.load(f)
count=0
cell= df[["dewey","norart-tittel","Idunn-tittel"]]
#print(cell)
titler=set()
regex = re.compile('[^a-zA-Z1234567890øæåØÆÅ ]')
new_titler={}
for i in df.iterrows():
	if len(i[1]["dewey"])>2:
		# if i[1]["Idunn-tittel"] in new_titler_adresse:
		#filnavn=new_titler_adresse[i[1]["Idunn-tittel"]]
		filnavn=i[1]["Idunn-tittel"]
		new_titler[str(filnavn)] = [i[1]["dewey"],i[1]["norart-tidsskrift"],i[1]["norart-tittel"],i[1]["norart-år"],i[1]["norart-url"]]

print(len(new_titler))


rootdir="extra"
for subdir, dirs, files in os.walk(rootdir):
	for file in files:
		file_tittel=file.replace(".xml.txt","")
		#print(file_tittel)
		if file_tittel in new_titler:
			relDir = os.path.relpath(subdir, rootdir)
			relFile = os.path.join(relDir, file)
			relFile = os.path.join(rootdir, relFile)
			d=open(relFile,"r")
			tekst=d.read()
			if tekst=="":
				continue
			lang = detect(tekst)
			print(lang)

			if lang=="no":
				copy(relFile, "fikset_dump/" + file)
				f=open("fikset_dump/meta-"+file_tittel+".txt","w")
				f.write("dewey:::"+new_titler[file_tittel][0]+"\n")
				f.write("tidsskrift:::"+new_titler[file_tittel][1]+"\n")
				f.write("tittel:::"+new_titler[file_tittel][2]+"\n")
				f.write("year:::"+new_titler[file_tittel][3]+"\n")
				f.write("url:::"+new_titler[file_tittel][4]+"\n")
				f.write("language:::"+lang)
			else:
				copy(relFile, "fikset_dump_ikke_norsk/" + file)
				f = open("fikset_dump_ikke_norsk/meta-" + file_tittel + ".txt", "w")
				f.write("dewey:::" + new_titler[file_tittel][0] + "\n")
				f.write("tidsskrift:::" + new_titler[file_tittel][1] + "\n")
				f.write("tittel:::" + new_titler[file_tittel][2] + "\n")
				f.write("year:::" + new_titler[file_tittel][3] + "\n")
				f.write("url:::" + new_titler[file_tittel][4] + "\n")
				f.write("language:::" + lang)

			print(file_tittel)