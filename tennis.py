# -*- coding: utf-8 -*-

import pycurl
import re
import urllib
import time
from bs4 import BeautifulSoup
import sys
import json

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

def _raiseIfSuperiorTo(var, maxValue, message=None):
    if (len(var) > maxValue):
        print "[KO] : " + str(message)
        raise

headers = {}
def header_function(header_line):
    header_line = header_line.decode('iso-8859-1')
    if ':' not in header_line:
        return
    name, value = header_line.split(':', 1)
    name = name.strip()
    value = value.strip()
    name = name.lower()
    headers[name] = value
    

def getCookie():
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'https://teleservices.paris.fr/srtm/jsp/web/index.jsp')
    c.setopt(c.WRITEFUNCTION, buffer.write)
    # Set our header function.
    c.setopt(c.HEADERFUNCTION, header_function)
    c.perform()
    c.close()
    return headers['set-cookie']
    

def searchCourt(cookie=None):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'https://teleservices.paris.fr/srtm/reservationCreneauListe.action')
    post_data = dict()
    ## Mandatory
    post_data['provenanceCriteres']='true'
    post_data['libellePlageHoraire']='Soirée (18h-21h)'
    post_data['nomCourt']=''
    post_data['actionInterne']='recherche'
    post_data['champ']=''
    post_data['recherchePreferee']='on'
    post_data['tennisArrond']=''#René et André Mourlon@15'
    post_data['arrondissement']='15'
    post_data['arrondissement2']=''
    post_data['arrondissement3']=''
    post_data['tousArrondissements']=''#on'
    post_data['dateDispo']=''
    post_data['heureDispo']=''
    post_data['plageHoraireDispo']='18@21'
    post_data['revetement']=''
    post_data['courtEclaire']=''#on'
    post_data['courtCouvert']=''#on'
    post_data['court']=''
    post_data['valider']='RECHERCHER'
    post_data['annuler']='ANNULER'

    postfields = urllib.urlencode(post_data)
    c.setopt(c.POSTFIELDS, postfields)
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.setopt(c.HEADERFUNCTION, header_function)
    if cookie:
        c.setopt(c.COOKIE, cookie)
    c.perform()
    c.close()
    with open("searchCourt.html", "w") as fd:
        fd.write(buffer.getvalue())
    soup = BeautifulSoup(buffer.getvalue())

    sys.exit(0)
    # Impossible de parser derrière....
    firstLevel = soup.find_all('input')
    print firstLevel
    sys.exit(0)
    #_raiseIfSuperiorTo(table,1)

    rows = courtTable.find_all('tr')
    print rows
    data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values
    print data


def initSearch(cookie=None):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'https://teleservices.paris.fr/srtm/reservationCreneauInit.action')
    c.setopt(c.HEADERFUNCTION, header_function)
    c.setopt(c.WRITEFUNCTION, buffer.write)
    if cookie:
        print cookie
        c.setopt(c.COOKIE, cookie)    
    c.perform()
    c.close()
    with open("initSearch.html", "w") as fd:
        fd.write(buffer.getvalue())


def connect(cookie=None):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'https://teleservices.paris.fr/srtm/authentificationConnexion.action')
    post_data = dict()
    try:
        json_data=open("credentials.json").read()
        credentials = json.loads(json_data)
        post_data['login']=credentials["login"]
        post_data['password']=credentials["password"]
    except Exception, e:
        print "Error with credentials: " + str(e)
        sys.exit(-1)


    postfields = urllib.urlencode(post_data)
    c.setopt(c.POSTFIELDS, postfields)
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.setopt(c.HEADERFUNCTION, header_function)
    if cookie:
        c.setopt(c.COOKIE, cookie) 
    c.perform()
    c.close()
    with open("connect.html", "w") as fd:
        fd.write(buffer.getvalue())
    
    soup = BeautifulSoup(buffer.getvalue())
    results = soup.find_all('legend')
    if len(results) > 0:
        print "Already a reservation"
        #sys.exit(0)
    
if __name__=='__main__':
    cookie=getCookie();
    connect(cookie)
    initSearch(cookie)
    searchCourt(cookie)
    
    
