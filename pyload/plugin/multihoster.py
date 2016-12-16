# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals
from time import time

from pyload.utils import remove_chars

from .account import Account


def normalize(domain):
    """ Normalize domain/plugin name, so they are comparable """
    return remove_chars(domain.strip().lower(), "-.")


#noinspection PyUnresolvedReferences
class MultiHoster(Account):
    """
    Base class for MultiHoster services.
    This is also an Account instance so you should see :class:`Account` and overwrite necessary methods.
    Multihoster becomes only active when an Account was entered and the MultiHoster addon was activated.
    You need to overwrite `loadHosterList` and a corresponding :class:`Hoster` plugin with the same name should
    be available to make your service working.
    """

    #: List of hoster names that will be replaced so pyLoad will recognize them: (orig_name, pyload_name)
    replacements = [("freakshare.net", "freakshare.com"), ("uploaded.net", "uploaded.to")]

    #: Load new hoster list every x seconds
    hoster_timeout = 300

    def __init__(self, *args, **kwargs):

        # Hoster list
        self.hoster = []
        # Timestamp
        self.ts = 0

        Account.__init__(self, *args, **kwargs)

    def load_hoster_list(self, req):
        """Load list of supported hoster

        :return: List of domain names
        """
        raise NotImplementedError


    def is_hoster_usuable(self, domain):
        """ Determine before downloading if hoster should be used.

        :param domain: domain name
        :return: True to let the MultiHoster download, False to fallback to default plugin
        """
        return True

    def get_hoster_list(self, force=False):
        if self.ts + self.hoster_timeout < time() or force:
            req = self.get_account_request()
            try:
                self.hoster = self.load_hoster_list(req)
            except Exception as e:
                self.log_error(e)
                return []
            finally:
                req.close()

            for rep in self.replacements:
                if rep[0] in self.hoster:
                    self.hoster.remove(rep[0])
                    if rep[1] not in self.hoster:
                        self.hoster.append(rep[1])

            self.ts = time()

        return self.hoster