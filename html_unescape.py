'''
Created on Apr 22, 2012

@author: lordzeus
'''
import sys
import re

PYTHON_VERSION = list(sys.version_info)[0]
if PYTHON_VERSION <= 2:
    import htmlentitydefs
else:
    import html.entities as htmlentitydefs

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    if PYTHON_VERSION <= 2:
                        return unichr(int(text[3:-1], 16))
                    else:
                        return chr(int(text[3:-1], 16))
                else:
                    if PYTHON_VERSION <= 2:
                        return unichr(int(text[2:-1]))
                    else:
                        return chr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                if PYTHON_VERSION <= 2:
                    text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
                else:
                    text = chr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is

    return re.sub("&#?\w+;", fixup, text)


if __name__ == '__main__':
    links = open("html/about.html", "rt")
    pagina_link = links.read()
    paginas = re.findall(r'<a.*?href=[\'"]([^#].*?)[\'"].*?>(.*?)</a>', pagina_link, flags=re.IGNORECASE)
    print(len(paginas))
    name = ""
    for link in paginas:
        name = re.sub("<.*?>", "", link[1], flags=re.IGNORECASE)
        name = unescape(name)
        print(link[0], " - ", name)
