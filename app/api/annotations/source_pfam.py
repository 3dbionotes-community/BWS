#! /usr/bin/env python

# Django modules to return a response when they are called
# The HttpResponse will hold the Json answer
from django.http import HttpResponse 
import json
import requests
import logging

from .models import PFAMentity
from django.forms.models import model_to_dict
from collections import defaultdict
# This module includes the functions that are executed when the URL under
# $(biourl)/api/annotations/Pfam are called 

# THIS IS FOR TESTING ONLY
# real variable should be obtained from config

PFAM_URL = "https://www.ebi.ac.uk/interpro/api/entry/pfam/protein/UniProt/{}/?extra_fields=short_name&page_size=10000" #/protein/P01308/"
#LOGGER = logging.getLogger("PFAM")
# This function is for /api/annotations/pfam/Uniprot/<id>
def _download_PFAM_from_externalDB(uniprotID) -> dict:
    url:str = PFAM_URL.format(uniprotID) # http://pfam.xfam.org/protein/PF00049?output=xml
    result:dict = {}
    try:
        response = requests.get(url)
        data = json.loads(response.text)
    except Exception as e:
        error = {"error":f"There was an error connecting to {url}", 
                 "error_code":response.error_code,
                 "description": e}
        return error

    info = dict()
    result["acc"] = data["results"][0]["metadata"]["accession"]
    result["start"] = data["results"][0]["proteins"][0]["entry_protein_locations"][0]["fragments"][0]["start"]
    result["end"] = data["results"][0]["proteins"][0]["entry_protein_locations"][0]["fragments"][0]["end"]
    result["id"] = data["results"][0]["extra_fields"]["short_name"]
    info["description"] = data["results"][0]["metadata"]["name"]
    info["go"] = {"process":[],
                      "component":[],
                      "function":[]} 
    go_terms = data["results"][0]["metadata"]["go_terms"]
    if go_terms is None:
        info["go"] = None
    else:
        for element in go_terms:
            if (element["category"]["code"]) == "P":
                info["go"]["process"].append(element["name"])
            if (element["category"]["code"]) == "C":
                info["go"]["component"].append(element["name"])
            if (element["category"]["code"]) == "F":
                info["go"]["function"].append(element["name"])
    result["go"] = info["go"]
    return result

def _load_PFAM_from_DB(proteinID):
    """
	Tries to load elements in the database associated with
        uniprotAC. Returns a List with all annotations fount

        Returns None if no elements found
    """
    query = []
    try:
        """
           Queries the database to get elements with the desired uniprotID
           Then turns it into a dict (to be able to be returned as json
           The behaviour varies depending on the query:
		- 1 or more results -> returned in a dict
                - 0 results -> returns None
                - Error -> returns None and TODO: registers the error
	"""
        query = PFAMentity.objects.filter(proteinID=proteinID)
        query = [json.loads(model_to_dict(result)["data"]) for result in query]
	    # If no elements returned, then return None
        # None means no results, and downstream it will be handled
        # By connecting to the original database and caching the data locally
        if (len(query)) == 0: 
            query = None
    except Exception as e:
        # Unexpected error while connecting to the cache DB 
        # Returning none to show no results could be retrieved
        query = {}
        print(e)
    finally:
        return query

def source_PFAM(request, uniprotID):
    out = _load_PFAM_from_DB(uniprotID)
    if (out is None):
        out = _download_PFAM_from_externalDB(uniprotID)
    status_code = 404 if "error" in out else 200
    return HttpResponse(json.dumps(out), 
                        content_type='application/json',
                        status=status_code)