#! /usr/bin/env python3

## Function for annotations for:
# /api/annotation/ensembl/variantion/:name

import json
import requests

from django.http import HttpResponse
from django.forms.models import model_to_dict

from .models import SMARTentity

def _load_variants_from_DB(id):
    return {}

def _save_variants_in_DB(id, variants):
    pass

def getENSEMBLvariations(request, ensemblid):
    variants = _load_variants_from_DB(ensemblid)
    if variants is None:
        pass
    return HttpResponse(json.dumps(variants),content_type='application/json')