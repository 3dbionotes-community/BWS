#! /usr/bin/env python3

# Database models for annotation

from django.db import models
from django.contrib import admin

###########################################
# Database Models for annotation endpoints#
###########################################

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

admin.site.register(SMARTentity)
