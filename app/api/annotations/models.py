#! /usr/bin/env python3

# Database models for annotation

from django.db import models
from django.contrib import admin
from django.apps import apps

###########################################
# Database Models for annotation endpoints#
###########################################

# This section contains all "Entries" models
# They all store data in a similar way:
# A protein/gen ID, timestamps and the data as a json dump to a string

class biomutanentries(models.Model):
    proteinID = models.CharField(max_length=255, blank=True, null=True, default="")
    data = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)

    def __str__(self):
        return self.proteinID

class dbptmentries(models.Model):
    proteinID = models.CharField(max_length=255, blank=True, null=True, default="")
    data = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)

    def __str__(self):
        return self.proteinID

class dsysmapentries(models.Model):
    proteinID = models.CharField(max_length=255, blank=True, null=True, default="")
    data = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)

    def __str__(self):
        return self.proteinID
        
class ebifeaturesentries(models.Model):
    proteinID = models.CharField(max_length=255, blank=True, null=True, default="")
    data = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)
    features_type = models.CharField(max_length=255, blank=True, null=True, default="")

    def __str__(self):
        return self.geneID

class EnsemblAnnotation(models.Model):
    geneName = models.CharField(max_length=30, blank=True, null=True, default="")
    transcriptName = models.CharField(max_length=30, blank=True, null=True, default="")
    start = models.IntegerField(null=True, blank=True)
    end = models.IntegerField(null=True, blank=True)
    type= models.CharField(max_length=30, blank=True, null=True, default="")

    def __str__(self):
        return f"{self.geneName}-{self.transcriptName}_{self.start}-{self.end}"

class EnsemblVariantEntry(models.Model):
    geneID = models.CharField(max_length=255, blank=True, null=True, default="")
    data = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)

    def __str__(self):
        return self.geneID

class intrproentries(models.Model):
    proteinID = models.CharField(max_length=255, blank=True, null=True, default="")
    data = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)

    def __str__(self):
        return self.proteinID

class mobientries(models.Model):
    proteinID = models.CharField(max_length=255, blank=True, null=True, default="")
    data = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)

    def __str__(self):
        return self.proteinID

class molprobityentries(models.Model):
    PDBID = models.CharField(max_length=255, blank=True, null=True, default="")
    data = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)

    def __str__(self):
        return self.PDBID

class PDBEntry(models.Model):
    PDBID = models.CharField(max_length=255, blank=True, null=True, default="")
    data = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)

    def __str__(self):
        return self.PDBID

class PDBRedoEntry(models.Model):
    PDBID = models.CharField(max_length=255, blank=True, null=True, default="")
    data = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)

    def __str__(self):
        return self.PDBID

class PFAMentity(models.Model):
    proteinID = models.CharField(max_length=255, blank=True, null=True, default="")
    data = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)

    def __str__(self):
        return self.proteinID

class PhosphoEntries(models.Model):
    proteinID = models.CharField(max_length=255, blank=True, null=True, default="")
    data = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)
    updated_at = models.DateTimeField(auto_now=False, auto_now_add=False, default=None)

    def __str__(self):
        return self.proteinID


# Model for SMART data
class SMARTentity(models.Model):
     uniprotid = models.CharField(max_length=30, blank=True, null=True, default="")
     domain = models.CharField(max_length=30, blank=True, null=True, default="")
     start = models.IntegerField(null=True, blank=True)
     end = models.IntegerField(null=True, blank=True)
     evalue = models.CharField(max_length=20, blank=True, null=True, default="1")
     type = models.CharField(max_length=30, blank=False, null=True, default="")

     def __str__(self):
         return self.uniprotid

class swissvarentries(models.Model):
     uniprotid = models.CharField(max_length=30, blank=True, null=True, default="")
     domain = models.CharField(max_length=30, blank=True, null=True, default="")
     start = models.IntegerField(null=True, blank=True)
     end = models.IntegerField(null=True, blank=True)
     evalue = models.CharField(max_length=20, blank=True, null=True, default="1")
     type = models.CharField(max_length=30, blank=False, null=True, default="")

     def __str__(self):
         return self.uniprotid

class uniprotmappingentries(models.Model):
     uniprotid = models.CharField(max_length=30, blank=True, null=True, default="")
     domain = models.CharField(max_length=30, blank=True, null=True, default="")
     gene = models.TextField(default=None, null=True)
     transcript = models.TextField(default=None, null=True)
     start = models.IntegerField(null=True, blank=True)
     end = models.IntegerField(null=True, blank=True)
     evalue = models.CharField(max_length=20, blank=True, null=True, default="1")
     type = models.CharField(max_length=30, blank=False, null=True, default="")

     def __str__(self):
         return self.uniprotid

admin.site.register(biomutanentries)
admin.site.register(dbptmentries)
admin.site.register(ebifeaturesentries)
admin.site.register(EnsemblAnnotation)
admin.site.register(EnsemblVariantEntry)
admin.site.register(intrproentries)
admin.site.register(mobientries)
admin.site.register(molprobityentries)
admin.site.register(PDBEntry)
admin.site.register(PDBRedoEntry)
admin.site.register(PFAMentity)
admin.site.register(PhosphoEntries)
admin.site.register(SMARTentity)
admin.site.register(swissvarentries)
admin.site.register(uniprotmappingentries)