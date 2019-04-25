class Context(object):
    _lastContent = None

    def __init__(self):
        Context._lastContent = self

def getCurrentContext():
        return Context._lastContent