
# http://www.garyrobinson.net/2004/03/python_singleto.html
# Gary Robinson
class Singleton(type):
    def __init__(cls, name, bases, dic):
        super().__init__(name, bases, dic)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kw)
        return cls.instance
    