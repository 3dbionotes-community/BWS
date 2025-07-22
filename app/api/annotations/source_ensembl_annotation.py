#! /usr/bin/env python3

## Function for annotations for:
# /api/annotation/ensembl/annotations/:name

import itertools
import json
import requests

from django.http import HttpResponse
from django.forms.models import model_to_dict

from .models import EnsemblAnnotation

# FOR TESTING ONLY
EnsemblURL = "http://rest.ensembl.org/overlap/id/{}?feature=transcript;feature=exon;content-type=application/json" #Settings.GS_EnsemblServer

def _create_ENSEMBL_annotation(id, type, name, start, end):
    annotation = EnsemblAnnotation()
    annotation.geneName = id
    annotation.transcriptName = name
    annotation.start = start
    annotation.end = end
    annotation.type = type
    return annotation

def getENSEMBLfromDB(ensembleid):
    query = None
    try:
        """
            Queries the database to get elements with the desired uniprotID
            Then turns it into a dict (to be able to be returned as json
            The behaviour varies depending on the query:
		    1 or more results -> returned in a dict
                - 0 results -> returns None
                - Error -> returns None and TODO: registers the error
	    """
        query = EnsemblAnnotation.objects.filter(geneName=ensembleid)
        query = [model_to_dict(result) for result in query]
	    # If no elements returned, then return None
        # None means no results, and downstream it will be handled
        # By connecting to the original database and caching the data locally
        if (len(query)) == 0: 
            query = {"error": f"{ensembleid} not found in DB",}
    except Exception as e:
        # Unexpected error while connecting to the cache DB 
        # Returning none to show no results could be retrieved
        query =  {"error":f"Error while connecting to DB"}
    finally:
        return query

def save_ENSEMBL_to_DB(geneID, data):
    for transcripts in data.keys():
        for type in data[transcripts]:
            for transcript in data[transcripts][type]:
                for exon in data[transcripts][type][transcript]:
                    start = exon['x']
                    end = exon['y']
                    Model = _create_ENSEMBL_annotation(geneID, type, transcript, start, end)
                    Model.save()

def _connect_to_ENSEMBL(URL, ensemblid):
        try:
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
    out = {}#out = {'repeat':[], 'simple':[], "constrained":[], "motif":[]}
    out['transcripts'] = {'coding':{},'non_coding':{}}
    transcript = {}
    for element in data:
        if str(element['feature_type']) == 'transcript' and element['Parent'] == id:
            transcript[element['transcript_id']] = {'external_name': element['external_name'], 'biotype':element['biotype']}
        # Originally this until end of loop was in another for loop which is a waste of cpu cycles and time
        # because iterated over the same element 
        flag = False
        if (element['feature_type'] != 'exon') or (not element['Parent'] in transcript):
            # Ignoring non-exons or those elements not assigned to a known transcript
            continue
        flag = True
        type = 'non_coding'
        if transcript[element['Parent']]['biotype'] == 'protein_coding':
            type = 'coding'
        name = transcript[element['Parent']]['external_name']
        if (not name in out['transcripts'][type]):
            out['transcripts'][type][name] = []
        out['transcripts'][type][name].append({'x':element['start'],'y':element['end']})
    if flag:
        save_ENSEMBL_to_DB(id, out)
    return out

def getENSEMBLannotations(request, ensemblid: str):
    ensembl = getENSEMBLfromDB(ensemblid)
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
        # Once processed, save the data...
        save_ENSEMBL_to_DB(ensemblid, ensembl)
        # ...and return them to the user
    return HttpResponse(json.dumps(ensembl),content_type='application/json')
