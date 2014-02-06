# -*- coding: utf-8 -*-


"""
==================================
Threaded Use of CPDB SOAP/WSDL API
==================================

:Authors:
    Moritz Emanuel Beber
:Date:
    2014-02-05
:Copyright:
    Copyright |c| 2014, Max-Plank-Institute for Molecular Genetics, all rights reserved.
:File:
    cpdb_wsdl_client.py

.. |c| unicode: U+A9
"""


__all__ = ["WSDLQueryThread"]


# stdlib
import logging
import threading
# stdlib
from queue import Queue
# external
#from pysimplesoap.client import SoapClient, SoapFault
from suds.client import Client, WebFault


LOGGER = logging.getLogger(__name__)


class WSDLQueryThread(threading.Thread):
    """

    """

    def __init__(self, wsdl, task_queue=None, results=None, wsdl_kw_args={},
            **kw_args):
        """
        """
        super(WSDLQueryThread, self).__init__(**kw_args)
#        self.client = SoapClient(wsdl=wsdl, **soap_kw_args)
        self.client = Client(wsdl, **wsdl_kw_args)
        self.task_queue = Queue() if task_queue is None else task_queue
        self.results = list() if results is None else results
        self._lock = threading.Lock()

    def run(self):
        """
        """
        while True: # maybe use `while not self.queue.empty():`
            (func, args, kw_args) = self.queue.get()
            try:
                response = getattr(self.client.service, func)(*args, **kw_args)
#            except SoapFault as err:
            except WebFault as err:
                LOGGER.warn(str(err))
            else:
                self._lock.acquire()
                self.results.append(response)
                self._lock.release()
            finally:
                self.task_queue.task_done()

