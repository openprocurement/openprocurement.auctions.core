from pyramid.events import subscriber
from openprocurement.api.events import ErrorDesctiptorEvent


@subscriber(ErrorDesctiptorEvent)
def auction_error_handler(event):
    if 'auction' in event.request.validated:
        event.params['AUCTION_REV'] = event.request.validated['auction'].rev
        event.params['AUCTIONID'] = event.request.validated['auction'].auctionID
        event.params['AUCTION_STATUS'] = event.request.validated['auction'].status
