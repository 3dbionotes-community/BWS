#! /usr/bin/env python3

import json

from django.http import HttpResponse
from .models import biomutanentries

def source_Biomuta_from_uniprot(request, uniprotAc):
    info = biomutanentries.objects.filter(proteinID=uniprotAc)
    result = []
    if(info and info['data']): 
        for i in info:
            result.append(i['data'])
    return  HttpResponse(json.dumps(result), content_type='application/json')