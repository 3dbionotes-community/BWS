#! /usr/bin/env python3

import json

from django.http import HttpResponse

from .models import dbptmentries

## Endpoints for the /api/annotation/Dbptm/Uniprot/<id>
## This funcion is called when the API endpoint is hit
def source_Dbptm_from_Uniprot(request, uniprot_id):
    info = dbptmentries.objects.filter(proteinID=uniprot_id)
    if(not info or not info['data']):
        info = {}
    else:
        info = info['data']
    return  HttpResponse(json.dumps(info), content_type='application/json')