#! /usr/bin/env python3

import json
import requests

from .models import InterproDatum
from django.http import HttpResponse

def _filter_downloaded_interpro(line):
    return "/interpro/popup/supermatch" in line


interpro_URL = "http://www.ebi.ac.uk/interpro/protein/{}"

def create_InterproDatum(id, data):
    pass

def read_InterproDatum(uniprotAc):
    data = InterproDatum.object.filter(proteinID=uniprotAc)
    if len(data) == 0:
        return None
    return data['data']

def download_from_interpro(uniprotAc):
    ### API changed and info is unavailable
    ###
    url = URL.format(uniprotAc)
    data = requests.get(url).text.split("\n")
    result = []
    for line in filter(_filter_downloaded_interpro, data):
        pass
    pass

def source_Interpro_from_Uniprot(uniprotAc):
    data = read_InterproDatum(uniprotAc)
    if data is None:
        data = download_from_interpro(uniprotAc)
        if len(data) > 0: 
            create_InterproDatum(uniprotAc, data)
    return HttpResponse(json.dumps(data), content_type='application/json')
