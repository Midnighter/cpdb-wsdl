=============================
ConsensusPathDB SOAP/WSDL API
=============================


Outline
-------

ConsensusPathDB_ integrates interaction networks from many different databases
into one seamless network [\ 1_ - 3_]. This Python module provides a class for threaded
access to the SOAP/WSDL interface of CPDB_ and testing.

.. _CPDB: ConsensusPathDB_
.. _ConsensusPathDB: http://consensuspathdb.org/

Usage
-----

You can use ``nose`` to discover and run all tests. In this directory simply
run:

    nosetests

If you prefer an interactive exploration of the API, you can use one of the
provided `IPython Notebooks`_ or look at them in the nbviewer (`suds ipynb`_,
`pysimplesoap ipynb`_).

.. _`IPython Notebooks`: http://ipython.org/notebook.html
.. _`suds ipynb`: http://nbviewer.ipython.org/github/Midnighter/cpdb-wsdl/blob/master/test_cpdb_client_suds.ipynb
.. _`pysimplesoap ipynb`: http://nbviewer.ipython.org/github/Midnighter/cpdb-wsdl/blob/master/test_cpdb_client_pysimplesoap.ipynb

Requirements
------------

* SUDS_ (preferably) or
* pysimplesoap_ or
* ZSI_, SOAPpy_ (inactive)

.. _SUDS: https://bitbucket.org/jurko/suds
.. _pysimplesoap: http://code.google.com/p/pysimplesoap/
.. _SOAPpy: ZSI_
.. _ZSI: http://pywebsvcs.sourceforge.net/

Also take a look at the ``requirements.txt`` file that you can use with ``pip``
to install the necessary packages, e.g.,

    pip install -r requirements.txt

Authors
-------

* Beber, Moritz Emanuel
* Kamburov, Atanas

References
----------
.. [1] `Kamburov, A. *et al*. (2013) *Nucleic Acids Res*.`__
.. __: http://nar.oxfordjournals.org/content/41/D1/D793
.. [2] `Kamburov, A. *et al*. (2011) *Nucleic Acids Res*.`__
.. __: http://nar.oxfordjournals.org/content/39/suppl_1/D712
.. [3] `Kamburov, A. *et al*. (2009) *Nucleic Acids Res*.`__
.. __: http://nar.oxfordjournals.org/content/37/suppl_1/D623

