from openprocurement.api.adapters import (
    ContentConfigurator,
    AwardingNextCheckAdapter
)


class AuctionConfigurator(ContentConfigurator):
    name = 'Auction Configurator'
    model = None
    award_model = None


class AuctionAwardingNextCheckAdapter(AwardingNextCheckAdapter):
    name = 'Auction Awarding Next Check Adapter' 
