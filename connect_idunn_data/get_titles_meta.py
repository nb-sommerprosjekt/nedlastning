import os
import re
from shutil import copyfile

rootdir="documents_without_rubbish"
old_root="tgc"

new_titles=set()



def traverse_folders(rootdir,look):
    new_set=set()
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            if str(file)[:5]=="meta-":
                f = open(os.path.join(subdir, file), "r+")
                tekst = f.read()
                keyword = re.search('tittel:::(.+?)\n', tekst)

                if keyword:


                    tittel = keyword.group(1)
                    new_set.add(tittel)
                    if "trospåvirkning" in tittel:
                        print(file)
                    if look:
                        #print("looking for this title: {}".format(tittel))
                        temp=""
                        for title in part_titles.keys():
                            if title in tittel:
                                temp+=str(part_titles[title])+"\n"
                        if temp!="":
                            print("looking for this title: {}".format(tittel))
                            print(temp)

    return new_set

def move_files(rootdir,title_set):

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            if str(file)[:5]=="meta-":
                f = open(os.path.join(subdir, file), "r+")
                tekst = f.read()
                keyword = re.search('tittel:::(.+?)\n', tekst)

                if keyword:


                    tittel = keyword.group(1)
                    if "trospåvirkning" in tittel:
                        print(file)
                    continue
                    if tittel in title_set:
                        if os.path.isfile(os.path.join(subdir, file[5:])):
                            copyfile(os.path.join(subdir, file[5:]), os.path.join("new_tcg2", file[5:]))
                            copyfile(os.path.join(subdir, file), os.path.join("new_tcg2", file))




part_titles={}

new_titles=traverse_folders("documents_without_rubbish",False)
old_titles=traverse_folders(old_root,False)


for title in new_titles:
    if title in old_titles:
        old_titles.remove(title)

move_files("tgc",old_titles)