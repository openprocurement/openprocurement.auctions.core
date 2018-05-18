from openprocurement.auctions.core.utils import get_auctions_aliases, format_auction_aliases

mock_data = {
    'api': None,
    'auctions.core': {
        'plugins': {
            'auctions.rubble.financial': {'use_default': True, 'migration': False, 'aliases': ['Alias']},
        }
    }
}


def test_get_auctions_aliases():
    auctions = get_auctions_aliases(mock_data)
    assert auctions == [{'auctions.rubble.financial': ['Alias']}]


def test_format_aliases():
    aliases = format_auction_aliases(get_auctions_aliases(mock_data))
    assert aliases == ["auctions.rubble.financial aliases: ['Alias']"]
