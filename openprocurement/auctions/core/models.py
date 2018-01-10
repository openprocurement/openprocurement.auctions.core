from schematics.transforms import whitelist
from zope.interface import Interface

auction_view_role = whitelist('auctionID', 'dateModified', 'bids',
                              'auctionPeriod', 'minimalStep', 'auctionUrl',
                              'features', 'lots', 'items',
                              'procurementMethodType', 'submissionMethodDetails')


class IAuction(Interface):
    """ Base auction marker interface """


def get_auction(model):
    while not IAuction.providedBy(model):
        model = model.__parent__
    return model
