#! /usr/bin/env python3

from django.http import HttpResponse

from .model import dbptmentries

## Endpoints for the /api/annotation/Dbptm/Uniprot/<id>
## This funcion is called when the API endpoint is hit
def source_Dbptm_from_Uniprot(request, uniprot_id):
    info = dbptmentries.filter(proteinID=uniprot_id)
    if(not info):
        info = []
    return  HttpResponse(json.dumps(info), content_type='application/json')