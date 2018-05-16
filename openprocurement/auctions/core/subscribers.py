from pyramid.events import subscriber
from openprocurement.api.events import ErrorDesctiptorEvent
from openprocurement.auctions.core.interfaces import IAuction


@subscriber(ErrorDesctiptorEvent)
def auction_error_handler(event):
    if 'auction' in event.request.validated and IAuction.providedBy(event.request.validated['auction']):
        event.params['AUCTION_REV'] = event.request.validated['auction'].rev
        event.params['AUCTIONID'] = event.request.validated['auction'].auctionID
        event.params['AUCTION_STATUS'] = event.request.validated['auction'].status
