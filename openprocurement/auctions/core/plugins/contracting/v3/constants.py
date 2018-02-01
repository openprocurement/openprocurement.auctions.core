from datetime import timedelta


# Periods of prolongations, that can be applied on Contract
PROLONGATION_SHORT_PERIOD = timedelta(days=42)
PROLONGATION_LONG_PERIOD = timedelta(days=132)

# Period, that limits time period between `datePublished` of
# Prolongation and it's actual creation time `dateCreated`
PROLONGATION_DATE_PUBLISHED_LIMIT_PERIOD = timedelta(days=20)
