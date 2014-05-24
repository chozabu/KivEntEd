__author__ = 'chozabu'

#from http://stackoverflow.com/a/13276237/445831 - Sasha Chedygov
class TwoWayDict(dict):
	#def __init__(self,iterable=None, **kwargs):
	#	super(TwoWayDict,self).__init__(iterable, **kwargs)

    def __setitem__(self, key, value):
        # Remove any previous connections with these values
        if key in self:
            del self[key]
        if value in self:
            del self[value]
        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)

    def __len__(self):
        """Returns the number of connections"""
        # The int() call is for Python 3
        return int(dict.__len__(self) / 2)