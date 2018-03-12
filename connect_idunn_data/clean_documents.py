import os
import re
from shutil import copyfile

import preprocessor

count=0
rootdir="documents"
destination="documents_without_rubbish"
test_set_folder=""
keywords={}
K=5
full_fasttext=""

errors=0
for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        if str(file)[:5]=="meta-":
            count += 1
            if count%100==0:
                print(count)
            f = open(os.path.join(subdir,file), "r+")
            tekst = f.read()
            keyword = re.search('tidsskrift:::(.+?)\n', tekst)
            try:
                tekst= preprocessor.text_to_clean_stemmed_text(tekst, False, False)
            except Exception as e:
                print(e)
                errors+=1
                print("mistakes {}".format(errors))
                continue

            if keyword:

                found = keyword.group(1)
                # found=found[:3].replace("\n","")
                tf = open(os.path.join(subdir, file[5:]), "r+")

                tekst=tf.read()
                if found == "Apollon":
                    tekst = preprocessor.fix_apollon1(tekst)
                    tekst = preprocessor.fix_apollon2(tekst)
                tekst = preprocessor.remove_backslash_dash(tekst)

                tekst = preprocessor.remove_redundant_space(tekst)
                tekst = preprocessor.fix_line_split(tekst)
                tekst = preprocessor.remove_html_noise(tekst)
                tekst = preprocessor.remove_redundant_space(tekst)

                copyfile(os.path.join(subdir, file[5:]), os.path.join(destination, file[5:]))
                copyfile(os.path.join(subdir, file), os.path.join(destination, file))
                f=open(os.path.join(destination, file[5:]),"w")
                f.write(tekst)
                #full_fasttext+="__label__"+str(found)+" "+tekst+"\n"


print(errors)
print(count)
#f=open("full_text_non_stemmed_oktober3_fra_processed.txt", "w")
#f.write(full_fasttext)
