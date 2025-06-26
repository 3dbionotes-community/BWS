#! /usr/bin/env python3

DsysmapURL = "https://dsysmap.irbbarcelona.org/api/getMutationsForProteins?protein_ids={}"

def _get_Dsys_data_fromDB(uniprotID):
    return None

def _save_Dsys_data_in_DB(uniprotID, data):
    pass

def _get_Dsys_data_from_uniprot(uniprotID):
    pass

def sourceDsysmapFromUniprot(request, uniprotID):
    data = _get_Dsys_data_fromDB(uniprotID)
    if data is None:
        data = _get_Dsys_data_from_uniprot(uniprotID)
        if len(data) > 0:
            _save_Dsys_data_in_DB(uniprotID, data)
    return HttpResponse(json.dumps(data),content_type='application/json')