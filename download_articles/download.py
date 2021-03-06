import re
import requests
import time
import os
import sys
import pickle

from bs4 import BeautifulSoup
import html2text
import httplib2
import validators
import PyPDF2
import urllib
from urllib.parse import urlparse
from datetime import datetime

import pymarc


import multiprocessing.pool
import functools

def timeout(max_timeout):
    """Timeout decorator, parameter in seconds."""
    def timeout_decorator(item):
        """Wrap the original function."""
        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            # raises a TimeoutError if execution exceeds max_timeout
            return async_result.get(max_timeout)
        return func_wrapper
    return timeout_decorator


@timeout(10.0)
def pdf_url(url, res):
    try:
        parsed_uri = urlparse(url)

        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        temp_url = url

        resp = res

        soup = BeautifulSoup(resp, 'html.parser', from_encoding=resp.info().get_param('charset'))

        for link in soup.find_all('a', href=True):
            if "pdf" in link['href']:
                temp_url = link['href']
                break
        if temp_url == url:
            return url
        if not validators.url(temp_url):
            if validators.url(domain + temp_url):
                return domain + temp_url
            else:
                print(domain + temp_url)
                return ""

        return temp_url
    except Exception as e:
        print(e)
        raise e

def retrieve_pdf_text(url, filnavn):
    content = ""
    try:

        urllib.request.urlretrieve(url, "PDFs/"+str(re.sub('\W+', '', str(url)))+".pdf")
        with open("PDFs/"+str(re.sub('\W+', '', str(url)))+".pdf", 'rb') as f:
            pdfReader = PyPDF2.PdfFileReader(f)
            for page_num in range(pdfReader.getNumPages()):
                content += pdfReader.getPage(page_num).extractText()

    except Exception as e:
        print("FAILURE AT PDF CONVERTING")
        print(url)
        print(e)
        raise(e)
        return type(e)(e.message + ' happens at PDF retrieval')

    htmlDoc = urllib.request.urlopen(url)
    soup = BeautifulSoup(htmlDoc, 'html.parser')
    save_html_file(soup, filnavn)
    save_html_file(soup, filnavn)

    return str(content)


def retrieve_html_text(url, res,filnavn):
    try:
        htmlDoc = urllib.request.urlopen(url)
        soup = BeautifulSoup(htmlDoc, 'html.parser')
        save_html_file(soup,filnavn)
        str = soup.get_text()
        str.encode("utf8")
        text = html2text.html2text(str)
    except Exception as e:
        print("Failed at HTML retrieval")
        print (e)
        raise type(e)(e.message + ' happens at Text retrieval from HTML-page')
    return text

def save_html_file(soup,filnavn):
    with open("html/"+filnavn+".html","w") as f:
        f.write(str(soup))

def write_to_file(tittel,undertittel,year,tidsskrift, dewey,keyword,filnavn, text, original_url, url, pdf_link):
    print("Sucessfully writing to file")
    try:
        if not os.path.exists(folder + "/" + kategori):
            os.makedirs(folder + "/" + kategori)
        with open(folder + "/" + kategori + "/meta-" + filnavn + ".txt", "w") as d:

            d.write("tittel:::" + str(tittel) + "\n")
            d.write("undertittel:::" + str(undertittel) + "\n")
            d.write("dewey:::" + str(dewey) + "\n")
            d.write("keyword:::" + str(keyword) + "\n")
            d.write("url:::" + str(url) + "\n")
            d.write("tidsskrift:::" + str(tidsskrift) + "\n")
            d.write("year:::" + str(year) + "\n")
            d.write("pdf_link:::" + str(pdf_link) + "\n")
            d.write("original_url:::"+ str(original_url) + "\n")

        with open(folder + "/" + kategori + "/" + filnavn + ".txt", "w") as f:
            f.write(str(text))

    except Exception as e:
        print(e)

# def write_to_file_failure(filnavn,kategori,original_url, url,feilsted, feilmelding):
#     print("Printing failure")
#     print(feilmelding)
#     print(feilsted)
#     print(kategori)
#     print(filnavn)
#     try:
#         if not os.path.exists(folder + "/"+"failure"+ "/" + kategori):
#             os.makedirs(folder + "/"+"failure" + "/" + kategori)
#         with open(folder + "/"+"failure" + "/" + kategori + "/meta-" + filnavn + ".txt", "w") as d:
#             d.write("tidspunkt:::" + str(datetime.now())+ "\n")
#             d.write("original_url:::" + str(original_url) + "\n")
#             d.write("url:::" + str(url) + "\n")
#             d.write("feilsted:::" + str(feilsted) + "\n")
#             d.write("feilmelding:::" + str(feilmelding) + "\n")
#
#     except Exception as e:
#         print(e)


def check_URL(url):
    try:
        if validators.url(url):
            return url
        elif validators.url("http://dx.doi.org/" + str(url)):
            res = urllib.request.urlopen("http://dx.doi.org/" + str(url)).geturl()
            return str(res)
        return ""
    except Exception as e:
        print("Failed at checking the URL")
        raise type(e)(e.message + ' Could not get the URL')

#parameters
filename = "norart20180108.xml"
folder="nedlastninger/"
failures_folder="failures/"



# with open("sucessful_urls.pickle", "rb") as open_file:
#     old_urls = pickle.load(open_file)
#
# with open("start_september.txt","r+") as p:
#    start=int(p.read())




records=[]
print("Loading XML-records. Please wait")
p=pymarc.marcxml.parse_xml_to_array(filename, strict=False, normalize_form=None)
print("Loading Complete")
count=0
count2=0
start=int(sys.argv[1])#2842#2721
end=start+1000
print("Starting download")
for record in p:

    if "082" in record and '650' in record and "856" in record:

        try:
            count2 += 1
            if count2 >= start and count2<end:

                print()
                print(count2)
                print(str(datetime.now()))
                tid = time.time()

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
                if str(year)!="":
                    if int(year)<2000:
                        print("TOOOO OLD!")
                        continue
                dewey = record["082"]["a"]
                kategori = str(dewey[:3])
                keyword=""
                if "650" in record:
                    keyword = record["650"]["a"]
                original_url = record["856"]['u'].replace(" ","")
                pdf_link=""
                text=""
                filnavn = str(re.sub('\W+', '', str(original_url) + str(tittel)))
                if len(filnavn) > 240:
                    filnavn = filnavn[:240]

                print("Orginale URLen fra XMLen: "+str(original_url))
                print("Filnavn: {}".format(filnavn))
                print("Sjekker link:" + str(time.time() - tid))
                time.sleep(1)
                url = check_URL(original_url)

                if "cook" in url:
                    try:
                        print(url)
                        cookie = {"Cookie JSESSIONID=": "aaarp3yCRmLzTatzMpt0v"}
                        res = requests.get(str("http://dx.doi.org/" + str(original_url)), cookies=cookie)
                        url=res.url
                    except Exception as e:
                        print(e)
                        # write_to_file_failure(filnavn, kategori, original_url, url,
                        #                       "DOI/URN conversion",e)

                print("URL som faktisk kan funke: " + str(url))
                if url != "":
                    try:
                        #time.sleep(2.0)
                        print("Skaffer en request fra siden:" + str(time.time() - tid))
                        res = urllib.request.urlopen(url)
                    except Exception as e:
                        print(e)
                        # write_to_file_failure(filnavn, kategori, original_url, url, "requesting response from URL", e)
                        continue
                    if res.getcode()== 200:
                        try:
                            print("Før pdf: " + str(time.time() - tid))
                            pdf_link = pdf_url(url, res)
                        except Exception as e:
                            print("FAILURE AT HTML TO PDF " + str(e))
                            if str(type(e)) == "<class 'multiprocessing.context.TimeoutError'>":
                                e = "This process used more than 10 seconds to access the PDF and was therefor terminated."
                            # write_to_file_failure(filnavn, kategori, original_url, url,
                            #                       "getting the pdf-link", e)


                        try:
                            print("Etter PDF: " + str(time.time() - tid))
                            if url != pdf_link:
                                print("Starting PDF retrieval: " + str(time.time() - tid))
                                text = retrieve_pdf_text(pdf_link,filnavn)
                        except Exception as e:
                            print(e)
                            # write_to_file_failure(filnavn, kategori, original_url, url, "downloading the PDF", e)
                        if text == "":
                            try:
                                print("før HTML: " + str(time.time() - tid))
                                text = retrieve_html_text(url,res,filnavn)
                                print("Etter HTML: " + str(time.time() - tid))
                            except Exception as e:
                                print("FAILURE AT HTML TO TEXT" + str(e))
                                # write_to_file_failure(filnavn, kategori, original_url, url,
                                #                       "Could not retrieve HTML text",e)
                                continue
                        write_to_file(tittel, undertittel, year, tidsskrift, dewey,keyword,filnavn, text, original_url, url, pdf_link)
                        print("FINISHED with this article: {}".format(str(time.time() - tid)))
                    else:
                        count+=1
                        # write_to_file_failure(filnavn, kategori, original_url, url, "Did not receive a 200-response",Exception("No response from URL") )

        except Exception as e:
            # write_to_file_failure(filnavn,kategori,original_url, url,"Something went wrong,this is the catch alll Exception", e)
            count+=1
# with open("start_september.txt","w") as p:
#     p.write(str(stop))
print ("Runnet failet: " +str(count)+" ganger.")

