'''
Created on Apr 22, 2012

@author: lordzeus
'''
import sys

PYTHON_VERSION = list(sys.version_info)[0]
if PYTHON_VERSION <= 2:
    import urllib
else:
    import urllib.request, urllib.parse, urllib.error
import re


def get_page(url, filename):
    print("getting page:", url, " saving in file:", filename)
    if re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url,
                flags=re.IGNORECASE):
        print("Valid url downloading", url)
    else:
        print("Invalid url downloading", url)
        return (-1)
    if PYTHON_VERSION <= 2:
        try:
            page = urllib.urlopen(url)
        except:
            return (-1)
    else:
        try:
            page = urllib.request.urlopen(url)
        except:
            return (-1)
    file_save = open(filename, "wt")
    file_save.write(page.read().decode("latin-1"))
    file_save.close()
    page.close()
    return 0


if __name__ == '__main__':
    filename = "html/test_90832910381.html"
    url = "http://yahoo.com"
    get_page(url, filename)
    file_test = open(filename, "rt")
    #	print(file_test.read())
    url = "yahoo.com"
    get_page(url, filename)
