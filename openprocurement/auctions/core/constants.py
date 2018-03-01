# -*- coding: utf-8 -*-

PROCEDURE_STATUSES = {
    "dgfInsider": {
        "tender_period_statuses": [
            "active.tendering", "active.auction", "active.auction.dutch",
            "active.auction.sealedbid", "active.auction.bestbid"
        ],
        "auction_statuses": [
            "active.auction", "active.auction.dutch",
            "active.auction.sealedbid", "active.auction.bestbid"
        ],
        "bid_interaction_statuses": [
            "active.tendering", "active.auction", "active.auction.dutch",
            "active.auction.sealedbid", "active.auction.bestbid"
        ],
        "bid_doc_interaction_statuses": [
            "active.tendering", "active.auction", "active.auction.dutch",
            "active.auction.sealedbid", "active.auction.bestbid", "active.qualification"
        ],
        "complaint_statuses": [
            "active.tendering", "active.auction", "active.auction.dutch",
            "active.auction.sealedbid", "active.auction.bestbid",
            "active.qualification", "active.awarded"
        ]

    },
    "dgfOtherAssets": {
        "tender_period_statuses": ["active.tendering", "active.auction"],
        "auction_statuses": ["active.auction"],
        "bid_interaction_statuses": ["active.tendering"],
        "bid_doc_interaction_statuses": ["active.tendering", "active.qualification"],
        "complaint_statuses": ["active.tendering", "active.auction", "active.qualification", "active.awarded"]
    }
}
PROCEDURE_STATUSES["dgfFinancialAssets"] = PROCEDURE_STATUSES["dgfOtherAssets"]
