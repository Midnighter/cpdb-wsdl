# -*- coding: utf-8 -*-


"""
=======================================
Test Threaded Use of CPDB SOAP/WSDL API
=======================================

:Authors:
    Moritz Emanuel Beber
    Atanas Kamburov
:Date:
    2014-02-05
:Copyright:
    Copyright |c| 2014, Max Plank Institute for Molecular Genetics, all rights reserved.
:File:
    test_cpdb_client_suds.py

.. |c| unicode: U+A9
"""


# stdlib
import logging
import json
import re
import random
# stdlib
from Queue import Queue
# external
import nose.tools as nt
from suds.client import Client, WebFault
# project
from cpdb_client import WSDLQueryThread


logging.basicConfig(level=logging.INFO)
logging.getLogger("suds").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

CONFIG = json.load(open("config.json", "r"))


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


class TestWSDLQueryThread(object):

    def setUp(self):
        self.tasks = Queue()
        self.results = list()
        for _ in range(CONFIG["num_threads"]):
            worker = WSDLQueryThread(CONFIG["wsdl_url"], self.tasks, self.results)
            worker.start()

    def tearDown(self):
        for _ in range(CONFIG["num_threads"]):
            self.tasks.put(WSDLQueryThread.sentinel)
        self.tasks.join()

    def test_version(self):
        version_pattern = re.compile(r"cpdb\d+")
        for _ in range(10):
            self.tasks.put(("getCpdbVersion", (), {}))
        self.tasks.join()
        for response in self.results:
            nt.ok_(version_pattern.match(str(response)))


