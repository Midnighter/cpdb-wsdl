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


import logging
import threading

from uuid import uuid4
from Queue import Queue

from suds.client import Client, WebFault


LOGGER = logging.getLogger(__name__)


class WSDLQueryThread(threading.Thread):
    sentinel = uuid4()

    def __init__(self, wsdl, task_queue=Queue(), results=list(),
            wsdl_kw_args=dict(), **kw_args):
        """
        Thread that retrieves SOAP queries from a queue and appends results.

        Parameters
        ----------
        wsdl: str
            URL of the WSDL file.
        task_queue: queue.Queue
            Any object that supports the ``get`` and ``task_done`` methods.
        results: list
            Any container that supports the ``append`` method.
        wsdl_kw_args: dict
            Passed on to the suds.client.Client constructor.

        Note
        ----
        This thread does not need to be daemonized, it can be terminated
        gracefully by putting the class sentinel in the queue.
        The task_queue and results default arguments are intended so that they
        are the same objects across all instances.
        """
        super(WSDLQueryThread, self).__init__(**kw_args)
        self.client = Client(wsdl, **wsdl_kw_args)
        self.task_queue = task_queue
        self.results = results
        self._lock = threading.Lock()

    def run(self):
        """
        Called by the ``start`` method.
        """
        for task in iter(self.task_queue.get, self.sentinel):
            try:
                (func, args, kw_args) = task
                LOGGER.debug("task found '%s'", str(func))
                response = getattr(self.client.service, func)(*args, **kw_args)
            except WebFault as err:
                LOGGER.error("miscommunication with server: '%s'", str(err))
            except StandardError as err:
                LOGGER.error(str(err))
            else:
                with self._lock:
                    self.results.append(response)
            finally:
                self.task_queue.task_done()
        LOGGER.debug("sentinel hit")
        self.task_queue.task_done()

