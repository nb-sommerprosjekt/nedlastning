import os
import re
import pickle
from langdetect import detect
from nltk.stem import snowball
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords




def text_to_clean_stemmed_text(tekst,pdf,stemming):
    norStem = snowball.NorwegianStemmer()
    with open('vocabulary.pickle', 'rb') as f:
        vocabulary=pickle.load(f)
    with open('vocabulary_stemmed.pickle', 'rb') as f:
        vocab_stemmed=pickle.load(f)
    if tekst != "":
        try:
            lang = detect(tekst)
        except Exception as e:
            raise Exception("Noe gikk galt da vi prøvde å finne ut språket i teksten. Feilmeldingen er: ", e)


        if lang=="no":
            tekst = tekst.replace("-\n", "")
            # regexeses to remove all urls and emails
            tekst = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', "", tekst)
            tekst = re.sub(
                r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''',
                "", tekst)
            if pdf:
                #Done to fix incorrect word-splits from pfd converting
                lines = tekst.splitlines(True)
                lines = [x for x in lines if x != "\n"]
                for i in range(len(lines)):
                    if i < len(lines) - 1:
                        temp1 = lines[i].split(" ")
                        temp2 = lines[i + 1].split(" ")
                        word = temp1[-1] + temp2[0]
                        word = word.replace("\n", "")
                        word = word.lower()
                        word = re.sub('[^a-zA-ZæøåÆØÅ]+', ' ', word)
                        if word in vocabulary:
                            lines[i]=lines[i].replace("\n", "")
                        elif norStem.stem(word) in vocab_stemmed:
                            lines[i] =lines[i].replace("\n", "")
                        else:
                            lines[i] =lines[i].replace("\n", " ")
                temp = ""
                for line in lines:
                    temp += line + ""
                tekst = temp
            # tekst = tekst.replace("\n", " ")
            # tekst = tekst.lower()
            tekst = re.sub('[^a-zA-ZæøåÆØÅ.,?!]+', ' ', tekst)
            tekst = tekst.replace("  ", " ")

            if stemming:
                tokens = word_tokenize(tekst)
                filtered_words = [word for word in tokens if word not in set(stopwords.words('norwegian'))]

                stemmed_words = list()
                for word in filtered_words:
                    stemmed_words.append(norStem.stem(word))

                tekst = ' '.join(stemmed_words)

            return tekst
        else:
            raise Exception("Teksten er ikke norsk, og kunnes derfor ikke testes.")
    else:
        raise Exception("Teksten er tom.")

# tekst1="Dette er bare en test, for å sjekke om det fung\nerer ytter\nlig. Det er ing\nen garant\ni foas\ndasr at det fakt\nisk gjør det \n Men hva så?  Det burde gå fin\nt"
# tekst1=text_to_clean_stemmed_text(tekst1,True,False)
# print(tekst1)

def add_space_after_period(text):
    return text.replace(".", " . ")

def remove_backslash_dash(text):
    return text.replace("\-"," ")

def remove_redundant_space(text):
    return text.replace("  "," ")

def remove_html_noise(text):
    with open('noise.pickle', 'rb') as f:
        noise=pickle.load(f)
    for word in noise:
        #print(word)
        if len(word)<12:
            text=text.replace(" "+word+" "," ")
        else:
            text=text.replace(word," ")

    return text

def remove_lines_page(text):
    text=text.splitlines()
    temp=""
    skip=0
    for line in text:
        if skip==0:
            if "book  Page" in line:
                skip=3
            else:
                temp+=line
        else:
            skip-=1
    return temp

def fix_apollon1(text):
    text=text.replace("Hovednavigasjon  hopp  Hovedinnholdet  hopp  Temanavigasjon  hopp  Kontaktinformasjon  hopp     Søk i Søk Meny   Ledere   Artikler","")
    text=text.replace("Ikke UiOeller Feide-bruker ? Opprett en WebID-bruker for å kommentere UiO","")
    text=text.replace("Blindern  kart  Problemveien","")
    text=text.replace("e-post      apollon  admin.uio.no","")
    return text

def fix_apollon2(text):
    text = word_tokenize(text)
    return " ".join(text[:-40])

def create_noise_pickle():
    noise=set()
    f = open("noise.txt","r")
    for line in f.readlines():
        noise.add(line.strip().replace("\n",""))
    for line in noise:
        print(line)
    with open('noise.pickle', 'wb') as f:
        pickle.dump(noise, f)
    print(len(noise))
create_noise_pickle()

# def fix_line_split(text):
#     text=text.replace("\n\n","\n")
#     with open('nsf2016.pickle', 'rb') as f:
#         vocabulary=pickle.load(f)
#     lines = text.splitlines(True)
#     lines = [x for x in lines if x != "\n"]
#     for i in range(len(lines)):
#         #print(lines[i])
#         if i < len(lines) - 1:
#             #print(lines[i][-2])
#             if lines[i][-2]=="-":
#                 print(i)
#                 print(lines[i])
#                 lines[i][-2]=""
#                 temp1 = lines[i].split(" ")
#                 temp2 = lines[i + 1].split(" ")
#                 word = temp1[-1] + temp2[0]
#                 word = word.replace("\n", "")
#                 word = word.lower()
#                 word = re.sub('[^a-zA-ZæøåÆØÅ]+', ' ', word)
#                 if word in vocabulary:
#                     lines[i] = lines[i].replace("\n", "")
#
#     temp = ""
#     for line in lines:
#         temp += line + ""
#     text = temp
#     return text
def fix_line_split(text):
    text=text.replace("\n\n","\n")
    with open('nsf2016.pickle', 'rb') as f:
        vocabulary=pickle.load(f)
    text=word_tokenize(text)
    for i,word in enumerate(text):
        if len(word)>0 and len(text)>i+1:
            if word[-1]=="-":
                text[i]=text[i][:-1]+text[i+1]
                text[i+1]=""

            if word[0]=="-":
                text[i-1] = text[i-1] + text[i][1:]
                text[i] = ""
    for i,word in enumerate(text):
        text[i] = re.sub('[^a-zA-ZæøåÆØÅ,.?!-]+', ' ', word)

    return " ".join(text)