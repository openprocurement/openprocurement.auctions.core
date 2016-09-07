from zope.interface import Interface


class IAuction(Interface):
    """ Base auction marker interface """


def get_auction(model):
    while not IAuction.providedBy(model):
        model = model.__parent__
    return model
