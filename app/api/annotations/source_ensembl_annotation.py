#! /usr/bin/env python3

## Function for annotations for:
# /api/annotation/ensembl/annotations/:name

import json
import requests

from django.http import HttpResponse
from django.forms.models import model_to_dict

from .models import SMARTentity

# FOR TESTING ONLY
EnsemblURL = "http://rest.ensembl.org/overlap/id/{}?feature=transcript;feature=exon;content-type=application/json" #Settings.GS_EnsemblServer

def save_ENSEMBL_to_DB(geneID, data):
    pass

def _connect_to_ENSEMBL(URL, ensemblid):
        try:
            print(EnsemblURL)
            print(ensemblid)
            url = EnsemblURL.format(ensemblid)
            print(url)
            response = requests.get(url)
        except Exception as e:
            # TODO: Handle error request
            print(e)
            error:dict = {'error':'Error when connecting to ENSEMBL'}
            return json.dumps(error)
        if (response.status_code != 200):
            # Error while connecting to the server, return a
            # response saying so and the status code
            return {'error':response.status_code}
        # Else we got a 200 code, request was ok: continue parsing the data
        return json.loads(response.content)

def _process_response_from_ENSEMBL(data: dict, id:str) -> dict:
    ## Preparing the dict with the needed strcuture
    out = {'repeat':[], 'simple':[], "constrained":[], "motif":[]}
    out['transcripts'] = {'coding':{},'non_coding':{}}
    transcript = {}
    for element in data:
        if str(element['feature_type']) == 'transcript' and element['Parent'] == id:
            transcript[element['transcript_id']] = {'external_name': element['external_name'], 'biotype':element['biotype']}
        # Originally this until end of loop was in another for look which is a waste of cpu cycles and time
        # because iterated over the same element returnValue
        flag = False
        if (element['feature_type'] != 'exon') or (not element['Parent'] in transcript):
            continue
        flag = True
        type = 'non_coding'
        if transcript[element['Parent']]['biotype'] == 'protein_coding':
            type = 'coding'
        name = transcript[element['Parent']]['external_name']
        print(out['transcripts'][type])
        if (not name in out['transcripts'][type]):
            out['transcripts'][type][name] = []
        out['transcripts'][type][name].append({'x':element['start'],'y':element['end']})
    if flag:
        save_ENSEMBL_to_DB(id, out)
    return out

def getENSEMBLannotations(request, ensemblid: str):
    ensembl = None # getENSEMBLfromDB(ensembleid)
    print(ensemblid)
    if ensembl is None:
        # Not present in DB
        # Download it and cache it
        data:dict = _connect_to_ENSEMBL(EnsemblURL, ensemblid)
        if "error" in data:
            # Error returned by the API, probably ID not found
            # TO DO expand the error to be more informative
            return HttpResponse(json.dumps(data),content_type='application/json')
        # Else no error found, continue processing the data
        ensembl = _process_response_from_ENSEMBL(data, ensemblid)
    return HttpResponse(json.dumps(ensembl),content_type='application/json')
