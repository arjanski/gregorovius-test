from dataclasses import dataclass
from pathlib import Path
from bs4 import BeautifulSoup
import re


# Create Soup for input file
def read_tei(tei_file):
    with open(tei_file, "r") as tei:
        soup = BeautifulSoup(tei, "xml")
        return soup
    raise RuntimeError("Error: Cannot generate a soup from file:", tei_file)


# Return text element for given node
def elem_to_text(elem, default=""):
    if elem:
        return elem.getText()
    else:
        return default


@dataclass
class Person:
    firstname: str
    middlename: str
    surname: str


# TEIFile class holds attributes that are derived from passed TEI file
class TEIFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.soup = read_tei(filename)
        self._urn = ""
        self._text_plain = ""
        self._text_xml = ""
        self._textteaser = ""
        self._date = ""
        self._title = ""
        self._sent = None
        self._received = None
        self._licence = ""
        self._revisiondate = ""
        self._revisionauthor = ""
        self._abstract = ""

    # Returns filename (without file type)
    def basename(self):
        stem = Path(self.filename).stem
        if stem.endswith(".tei"):
            return stem[0:-4]
        else:
            return stem

    # Returns relative file path
    def filepath(self):
        path = Path(self.filename).parent
        return str(path)

    # Returns <idno> 'type' attribute
    def idno(self, type):
        idno_elem = self.soup.find("idno", type=type)
        if not idno_elem:
            return ""
        else:
            return idno_elem.getText()

    # <title> text
    @property
    def title(self):
        if not self._title and self.soup.title:
            try:
                self._title = self.soup.title.getText()
            except:
                pass
        return self._title

    # <correspAction> type "sent"
    @property
    def sent(self):
        if not self._sent and self.soup.find("correspAction"):
            try:
                correspAction = self.soup.find("correspAction")
                type = correspAction.get("type")
                if type == "sent":
                    sent = {
                        "date": {
                            "when": correspAction.find("date").get("when"),
                            "cert": correspAction.find("date").get("cert"),
                        },
                        "person": {
                            "name": correspAction.find("persName").getText(),
                            "key": correspAction.find("persName").get("key")
                        },
                        "place": {
                            "name": correspAction.find("placeName").getText(),
                            "key": correspAction.find("placeName").get("key")
                        }
                    }
                    self._sent = sent
            except:
                pass
        return self._sent

    # <correspAction> type "received"
    @property
    def received(self):
        if not self._received and self.soup.find("correspAction"):
            try:
                correspAction = self.soup.find("correspAction")
                type = correspAction.get("type")
                if type == "received":
                    received = {
                        "person": {
                            "name": correspAction.find("persName").getText(),
                            "key": correspAction.find("persName").get("key")
                        },
                        "place": {
                            "name": correspAction.find("placeName").getText(),
                            "key": correspAction.find("placeName").get("key")
                        }
                    }
                    self._received = received
            except:
                pass
        return self._received

    # <date> text
    @property
    def date(self):
        if not self._date and self.soup.date:
            try:
                self._date = self.soup.date.getText()
            except:
                pass
        return self._date

    # <licence> text
    @property
    def licence(self):
        if not self._licence and self.soup.licence:
            try:
                self._licence = self.soup.licence.getText()
            except:
                pass
        return self._licence

    # <change> 'when' attribute
    @property
    def revisiondate(self):
        if not self._revisiondate and self.soup.change:
            try:
                self._revisiondate = self.soup.change["when"]
            except:
                pass
        return self._revisiondate

    # <change> 'who' attribute
    @property
    def revisionauthor(self):
        if not self._revisionauthor and self.soup.change:
            try:
                self._revisionauthor = self.soup.change["who"]
            except:
                pass
        return self._revisionauthor

    # <abstract> text
    @property
    def abstract(self):
        if not self._abstract:
            try:
                abstract = self.soup.abstract.getText(separator=" ", strip=True)
                self._abstract = abstract
            except:
                pass
        return self._abstract

    # <author> texts
    def authors(self):
        authors_in_header = self.soup.analytic.find_all("author")

        result = []
        for author in authors_in_header:
            persname = author.persname
            if not persname:
                continue
            firstname = elem_to_text(persname.find("forename", type="first"))
            middlename = elem_to_text(persname.find("forename", type="middle"))
            surname = elem_to_text(persname.surname)
            person = Person(firstname, middlename, surname)
            result.append(person)
        return result

    # <text> text (parsed as string)
    @property
    def text_plain(self):
        if not self._text_plain:
            body = self.soup.body.getText()
            self._text_plain = body
        return self._text_plain

    # <text> xml node as string
    @property
    def text_xml(self):
        if not self._text_xml and self.soup.find("body"):
            body = self.soup.body
            print(type (body) )
            self._text_xml = str(body)
        return self._text_xml

    # Text teaser: first 200 characters of <text>
    @property
    def textteaser(self):
        if not self._text:
            divs_text = []
            for div in self.soup.body.find_all(subtype="section"):
                div_text = div.get_text(separator=" ", strip=True)
                divs_text.append(div_text)

            plain_text = " ".join(divs_text)
            self._text = plain_text[:200].rstrip()
            re.sub("\s+", " ", self._text)
        return self._text
