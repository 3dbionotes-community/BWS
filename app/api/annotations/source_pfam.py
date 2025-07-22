#! /usr/bin/env python

# Django modules to return a response when they are called
# The HttpResponse will hold the Json answer
from django.http import HttpResponse 
import json
import requests
import logging

from .models import PFAMentity
from django.forms.models import model_to_dict
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
        data = response.text
    except Exception as e:
        error = {"error":f"There was an error connecting to {url}", 
                 "error_code":response.error_code,
                 "description": e}
        return error
    return data

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
        query = None
        print(e)
    finally:
        return query

def source_PFAM(request, uniprotID):
    out = _load_PFAM_from_DB(uniprotID)
    if (out is None):
        out = _download_PFAM_from_externalDB(uniprotID)
    return HttpResponse(json.dumps(out), 
                        content_type='application/json')