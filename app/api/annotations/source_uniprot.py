#! /usr/bin/env python3

import json
import requests

from django.http import HttpResponse


UNIPROT_URL:str = "https://rest.uniprot.org/uniprotkb/{}.fasta"

def get_uniprot_sequence(uniprotAc):
    url = UNIPROT_URL.format(uniprotAc)
    data = requests.get(url).text
    data = data.split("\n")[1:] # Ignore header
    return "".join(data)

####################
#                  #
#   API ENDPOINTS  #
#                  #
####################

def get_uniprot_length(request, uniprotAc):
    seq = get_uniprot_sequence(uniprotAc)
    return HttpResponse(json.dumps([len(seq)]), content_type='application/json')

def fetch_uniprot_multiple_sequences(request, uniprotAcs,sep=","):
    return_values = {}
    fastas = []
    accessions_ids = []
    ids = uniprotAcs.split(sep)
    if (len(ids)) > 1:
        for id in ids:
            fastas.append(get_uniprot_sequence(id))
            ids.append(id)
    else:
            fastas.append(get_uniprot_sequence(uniprotAcs))
            ids.append(uniprotAcs)
    for entry, acc in zip(fastas, accessions_ids):
        entry_definition = "unknown" # explicitely set

