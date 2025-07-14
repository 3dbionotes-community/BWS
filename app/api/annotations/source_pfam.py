#! /usr/bin/env python

# Django modules to return a response when they are called
# The HttpResponse will hold the Json answer
from django.http import HttpResponse 
import json
import requests
import logging

from .models import PFAMentity
# This module includes the functions that are executed when the URL under
# $(biourl)/api/annotations/Pfam are called 

# THIS IS FOR TESTING ONLY
# real variable should be obtained from config

PFAM_URL = "http://pfam.xfam.org" #/protein/P01308/"
#LOGGER = logging.getLogger("PFAM")
# This function is for /api/annotations/pfam/Uniprot/<id>
def _download_PFAM_from_externalDB(uniprotID):
    url:str = f"{PFAM_URL}/protein/{uniprotID}?output=xml" # http://pfam.xfam.org/protein/PF00049?output=xml
    try:
        response = requests.get(url)
        status = 200
        pass
    except Exception as e:
        status = 400
    data = [{"status":status}, {"start":"25","end":"25","evidences":"1959628","type":"Proteolytic Cleavage"}]
    return data

def _load_PFAM_from_DB(proteinID):
    print("Loading from DB")
    data = PFAMentity.objects.filter(proteinID = proteinID)
    print(data)
    print("Loaded from DB")
    return None if not data else data

def source_PFAM(request, uniprotID):
    out = _load_PFAM_from_DB(uniprotID)
    if (out is None):
        out = _download_PFAM_from_externalDB(uniprotID)
    return HttpResponse(json.dumps(out), 
                        content_type='application/json')