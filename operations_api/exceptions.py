class ImproperlyConfigured(Exception):
    """ Raised in the event ``operations-api`` has not been properly configured
    """
    pass


class HTTPError(Exception):
    """ Raised in the event ``operations-api`` was not able to get data from remote server
    """
    pass
