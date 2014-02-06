# -*- coding: utf-8 -*-


"""
=======================================
Test Threaded Use of CPDB SOAP/WSDL API
=======================================

:Authors:
    Moritz Emanuel Beber
:Date:
    2014-02-05
:Copyright:
    Copyright |c| 2014, Max-Plank-Institute for Molecular Genetics, all rights reserved.
:File:
    test_cpdb_wsdl_client.py

.. |c| unicode: U+A9
"""


# stdlib
import logging
import re
import random
# external
import nose.tools as nt
# stdlib
#from pysimplesoap.client import SoapClient, SoapFault
from suds.client import Client, WebFault


logging.basicConfig(level=logging.INFO)
logging.getLogger("suds").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

CONFIG={
        "wsdl_url": "http://cpdb.molgen.mpg.de/download/CPDB.wsdl",
        "valid_gene_acc_types": [
                "sgd-symbol", "hgnc-id", "sgd-id", "entrez-gi", "humancyc",
                "intact", "unigene", "cygd", "entrez-gene", "hprd",
                "mgi-symbol", "mgi-id", "hgnc-symbol", "refseq", "uniprot",
                "ensembl", "reactome", "dip", "pdb"],
        "valid_gene_func_types": ["P", "N", "G2", "G3", "G4", "G5", "C"],
        "gene_func_descriptions": [
                "manually curated pathways from pathway databases",
                "interaction network neighborhood-based functional sets",
                "Gene Ontology-based sets, GO level 2",
                "Gene Ontology-based sets, GO level 3",
                "Gene Ontology-based sets, GO level 4",
                "Gene Ontology-based sets, GO level 5",
                "protein complex-based sets"
        ],
        "small_gene_set": ["DLDH_HUMAN", "MDHC_HUMAN", "MDHM_HUMAN"],
        "small_gene_set_ids": [
                "entrez-gene:1738", "entrez-gene:4190", "entrez-gene:4191"
        ],
        "large_gene_set": [
                "MDHM_HUMAN", "MDHC_HUMAN", "DLDH_HUMAN", "DHSA_HUMAN",
                "DHSB_HUMAN", "C560_HUMAN", "DHSD_HUMAN", "ODO2_HUMAN",
                "ODO1_HUMAN", "CISY_HUMAN", "ACON_HUMAN", "IDH3A_HUMAN",
                "IDH3B_HUMAN", "IDH3G_HUMAN", "SUCA_HUMAN", "SUCB1_HUMAN",
                "FUMH_HUMAN", "OGDHL_HUMAN", "ACOC_HUMAN", "DHTK1_HUMAN",
                "AMAC1_HUMAN"
        ],
        "large_metabolite_set": [
                "C00002", "C00011", "C00001", "C00004", "C00080", "C00003",
                "C00008", "C00009", "C00024", "C00010", "C00122", "C00026",
                "C00042", "C00451", "C00091", "C00158", "C00036", "C00417",
                "C00497"
        ]
}


class TestCPDBAPI(object):

    def setUp(self):
        self.client = Client(CONFIG["wsdl_url"])
        LOGGER.info(str(self.client))

    def test_version(self):
        response = self.client.service.getCpdbVersion()
        nt.ok_(re.match(r"cpdb\d+", str(response)))

    def test_accession_types(self):
        response = self.client.service.getAvailableAccessionTypes("genes")
        valid_types = frozenset(CONFIG["valid_gene_acc_types"])
        for gene_type in response:
            nt.assert_in(str(gene_type), valid_types)

    def test_functional_types(self):
        valid_types = CONFIG["valid_gene_func_types"]
        valid_descriptions = CONFIG["gene_func_descriptions"]
        response = self.client.service.getAvailableFsetTypes("genes")
        result = zip(response["fsetType"], response["description"])
        for pair in result:
            nt.assert_equal(valid_types.index(pair[0]),
                    valid_descriptions.index(pair[1]))

    def test_accession_map(self):
        valid_numbers = CONFIG["small_gene_set"]
        valid_ids = CONFIG["small_gene_set_ids"]
        response = self.client.service.mapAccessionNumbers("uniprot",
                CONFIG["small_gene_set"])
        result = zip(response["accNumber"], response["cpdbId"])
        for pair in result:
            nt.assert_equal(valid_numbers.index(pair[0]),
                    valid_ids.index(pair[1]))

    def test_default_background(self):
        response = self.client.service.getDefaultBackgroundSize("P", "uniprot")
        nt.assert_equal(int(response), 10205)

    @nt.raises(AssertionError)
    def test_cpdb_ids_in_fset(self):
        response = self.client.service.getCpdbIdsInFset(90664, "P", "metabolites")
        nt.ok_(response)

    def test_wrong_access(self):
        nt.assert_raises(WebFault, self.client.service.getAvailableAccessionTypes,
                "malicious code")
# could further test here with malicious SQL statements or the like

    def check_gene_over_representation(self, numbers):
        response = self.client.service.mapAccessionNumbers("uniprot", numbers)
        # some results have no mapping, i.e., are `None`
        cpdb_ids = [str(num) for num in response["cpdbId"] if num is not None]
        response = self.client.service.overRepresentationAnalysis("genes", "C",
                cpdb_ids, [], "uniprot", 1.0)
        result = zip(response["name"], response["details"],
                response["overlappingEntitiesNum"], response["allEntitiesNum"],
                response["pValue"], response["qValue"])
        for multi in result[:5]:
            LOGGER.info("\t".join(multi))

    def check_metabolite_over_representation(self, numbers):
        response = self.client.service.mapAccessionNumbers("kegg", numbers)
        # some results have no mapping `None` and we limit the number
        cpdb_ids = [str(num) for num in response["cpdbId"] if num is not None]
        response = self.client.service.overRepresentationAnalysis("metabolites", "P",
                cpdb_ids, [], "kegg", 0.05)
        result = zip(response["name"], response["details"],
                response["overlappingEntitiesNum"], response["allEntitiesNum"],
                response["pValue"], response["qValue"])
        for multi in result[:5]:
            LOGGER.info("\t".join(multi))

    def test_over_representation(self):
        self.check_gene_over_representation(CONFIG["large_gene_set"])
        self.check_metabolite_over_representation(CONFIG["large_metabolite_set"])

    def test_enrichment(self):
        numbers = CONFIG["large_gene_set"]
        response = self.client.service.mapAccessionNumbers("uniprot", numbers)
        # some results have no mapping, i.e., are `None`
        cpdb_ids = ["%s %g %g" % (str(num), random.gauss(0.0, 1.0),
                random.gauss(2.0, 1.0)) for num in response["cpdbId"] if num is not None]
        response = self.client.service.enrichmentAnalysis("genes", "C", cpdb_ids, 1.0)
        result = zip(response["name"], response["details"],
                response["measuredEntitiesNum"], response["allEntitiesNum"],
                response["pValue"], response["qValue"])
        for multi in result[:5]:
            LOGGER.info("\t".join(multi))

