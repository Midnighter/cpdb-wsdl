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
from uuid import uuid4
from Queue import Queue
# external
from suds.client import Client, WebFault


LOGGER = logging.getLogger(__name__)


class WSDLQueryThread(threading.Thread):
    """

    """
    sentinel = uuid4()

    def __init__(self, wsdl, task_queue=None, results=None, wsdl_kw_args={},
            **kw_args):
        """
        """
        super(WSDLQueryThread, self).__init__(**kw_args)
        self.client = Client(wsdl, **wsdl_kw_args)
        self.task_queue = Queue() if task_queue is None else task_queue
        self.results = list() if results is None else results
        self._lock = threading.Lock()

    def run(self):
        """
        """
        for task in iter(self.task_queue.get, self.sentinel):
            (func, args, kw_args) = task
            LOGGER.debug("task found '%s'", str(func))
            try:
                response = getattr(self.client.service, func)(*args, **kw_args)
            except WebFault as err:
                LOGGER.warn(str(err))
            else:
                with self._lock:
                    self.results.append(response)
            finally:
                self.task_queue.task_done()
        LOGGER.debug("sentinel hit")
        self.task_queue.task_done()

