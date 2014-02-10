#!/usr/bin/python

import random
import sys

from cpdb_services import *


loc = cpdbLocator()
proxy = loc.getcpdb_portType(tracefile=sys.stdout)

if 1:  ## function: getCpdbVersion
    req = getCpdbVersionRequest()
    response = proxy.getCpdbVersion(req)
    result = response._cpdbVersion
    print result

if 1:  ## function: getAvailableAccessionTypes
    req = getAvailableAccessionTypesRequest()
    req._entityType = 'genes'
    response = proxy.getAvailableAccessionTypes(req)
    result = response._accType
    print result
    
if 1:  ## function: mapAccessionNumbers
    req = mapAccessionNumbersRequest()
    req._accType = 'uniprot'
    req._accNumbers = ["MDHM_HUMAN", "MDHC_HUMAN", "DLDH_HUMAN"]
    response = proxy.mapAccessionNumbers(req)
    result = zip(response._accNumber, response._cpdbId)
    print result

if 1:  ## function: getAvailableFsetTypes
    req = getAvailableFsetTypesRequest()
    req._entityType = 'genes'
    response = proxy.getAvailableFsetTypes(req)
    result = zip(response._fsetType, response._description)
    print result

if 1:  ## function: getDefaultBackgroundSize
    req = getDefaultBackgroundSizeRequest()
    req._fsetType = 'P'
    req._accType = 'uniprot'
    response = proxy.getDefaultBackgroundSize(req)
    result = response._bgSize
    print result

if 1:  ## function: overRepresentationAnalysis
    ## first map a list of uniprot IDs to cpdbIds
    req = mapAccessionNumbersRequest()
    req._accType = 'uniprot'
    req._accNumbers = ['MDHM_HUMAN', 'MDHC_HUMAN', 'DLDH_HUMAN', 'DHSA_HUMAN', 'DHSB_HUMAN', 'C560_HUMAN', 'DHSD_HUMAN', 'ODO2_HUMAN', 'ODO1_HUMAN', 'CISY_HUMAN', 'ACON_HUMAN', 'IDH3A_HUMAN', 'IDH3B_HUMAN', 'IDH3G_HUMAN', 'SUCA_HUMAN', 'SUCB1_HUMAN', 'FUMH_HUMAN', 'OGDHL_HUMAN', 'ACOC_HUMAN', 'DHTK1_HUMAN', 'AMAC1_HUMAN']
    response = proxy.mapAccessionNumbers(req)
    result = zip(response._accNumber, response._cpdbId)
    cpdbIds = []
    for r in result:
        if r[1]:
            cpdbIds.append(r[1].split(',')[0])  ## here we take only one of the mappings for simplicity
    
    req = overRepresentationAnalysisRequest()
    req._entityType = 'genes'
    req._fsetType = 'C'
    req._cpdbIdsFg = cpdbIds
    ## req._cpdbIdsFg stays None, thus we have to set req._accType for the program to select the uniprot-specific background
    req._accType = 'uniprot'
    req._pThreshold = 1
    response = proxy.overRepresentationAnalysis(req)
    result = zip(response._name, response._details, response._overlappingEntitiesNum, response._allEntitiesNum, response._pValue, response._qValue)
    print result[:5]  ## only the first five pathways are printed
    
    ## an example with metabolites
    req = mapAccessionNumbersRequest()
    req._accType = 'kegg'
    req._accNumbers = ['C00002', 'C00011', 'C00001', 'C00004', 'C00080', 'C00003', 'C00008', 'C00009', 'C00024', 'C00010', 'C00122', 'C00026', 'C00042', 'C00451', 'C00091', 'C00158', 'C00036', 'C00417', 'C00497']
    response = proxy.mapAccessionNumbers(req)
    result = zip(response._accNumber, response._cpdbId)
    cpdbIds = []
    for r in result:
        if r[1]:
            cpdbIds.append(r[1].split(',')[0])  ## here we take only one of the mappings for simplicity
    
    req = overRepresentationAnalysisRequest()
    req._entityType = 'metabolites'
    req._fsetType = 'P'
    req._cpdbIdsFg = cpdbIds
    ## req._cpdbIdsFg stays None, thus we have to set req._accType for the program to select the uniprot-specific background
    req._accType = 'kegg'
    req._pThreshold = 0.05
    response = proxy.overRepresentationAnalysis(req)
    result = zip(response._name, response._details, response._overlappingEntitiesNum, response._allEntitiesNum, response._pValue, response._qValue)
    print result[:5]  ## only the first five pathways are printed
    
if 1:  ## function: enrichmentAnalysis
    ## first map a list of uniprot IDs to cpdbIds
    req = mapAccessionNumbersRequest()
    req._accType = 'uniprot'
    req._accNumbers = ['MDHM_HUMAN', 'MDHC_HUMAN', 'DLDH_HUMAN', 'DHSA_HUMAN', 'DHSB_HUMAN', 'C560_HUMAN', 'DHSD_HUMAN', 'ODO2_HUMAN', 'ODO1_HUMAN', 'CISY_HUMAN', 'ACON_HUMAN', 'IDH3A_HUMAN', 'IDH3B_HUMAN', 'IDH3G_HUMAN', 'SUCA_HUMAN', 'SUCB1_HUMAN', 'FUMH_HUMAN', 'OGDHL_HUMAN', 'ACOC_HUMAN', 'DHTK1_HUMAN', 'AMAC1_HUMAN']
    response = proxy.mapAccessionNumbers(req)
    result = zip(response._accNumber, response._cpdbId)
    cpdbIds = []
    for r in result:
        if r[1]:
            cpdbIds.append(r[1].split(',')[0])  ## here we take only one of the mappings for simplicity
    for i in xrange(len(cpdbIds)):
        cpdbIds[i] += " %g %g" % (random.gauss(0,1), random.gauss(2,1))
    
    req = enrichmentAnalysisRequest()
    req._entityType = 'genes'
    req._fsetType = 'C'
    req._cpdbIdsMeasurements = cpdbIds
    req._pThreshold = 1
    response = proxy.enrichmentAnalysis(req)
    result = zip(response._name, response._details, response._measuredEntitiesNum, response._allEntitiesNum, response._pValue, response._qValue)
    print result[:5]  ## only the first five pathways are printed

if 1:  ## getCpdbIdsInFset
    req = getCpdbIdsInFsetRequest()
    req._fsetId = 90664
    req._fsetType = 'P'
    req._entsetType = 'metabolites'
    response = proxy.getCpdbIdsInFset(req)
    result = response._cpdbIds
    print result
