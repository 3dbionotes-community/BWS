#! /usr/bin/env python3

## Function for annotations for:
# 

import json
import requests

from django.http import HttpResponse
from django.forms.models import model_to_dict

from .models import PhosphositeEntity

def _load_phosphosite_from_DB(id) -> PhosphositeEntity:
    data = PhosphositeEntity.objects.filter(proteinID=id)
    return None if not data else data
    
#def _save_phosposite_in_DB(id, info):
    # TO IMPLEMENT as there is no original ruby implementation on this
    # (No upstream database)
    # I'll leave it here if this may change in the future
    # So there is no source of data to parse
#    pass

def get_phosphositeFromUniprot(request, ensemblid):
    results = _load_phosposite_from_DB(ensemblid)
    if results is None:
        results = [{"error": f"{ensemblid} not found in db"}]
    return HttpResponse(json.dumps(results),content_type='application/json')
