# -*- coding: utf-8 -*-
from zope.interface import implementer

from openprocurement.auctions.core.utils import (
    save_auction
)

from openprocurement.auctions.core.interfaces import (
    IManager
)


@implementer(IManager)
class AuctionManager(object):

    def __init__(self, request, context):
        self.request = request
        self.context = context
        self.changed = False
        self.saved = False

    def award(self):
        auctioner = self.auctioneer(self.request, self.context)
        if auctioner.award():
            awarding = self.awarding(self.context, self.request)
            awarding.start_awarding()

    def cancel(self):
        canceller = self.canceller(self.request, self.context)
        cancellation = canceller.cancel()
        return cancellation

    def report(self):
        manager = self.changion_manager(self.request, self.context)
        self.changed = manager.manage()
        return self.changed

    def change(self):
        manager = self.changion_manager(self.request, self.context)
        self.changed = manager.manage()
        return self.changed

    def create(self, applicant):
        manager = self.creation_manager(self.request, self.context)
        creature = manager.manage(applicant)
        if creature:
            self.changed = True
        return creature

    def log(self, action, verbose):
        logger = self.log(self.request, self.context)
        logger.log(action, verbose)

    def get_representation_manager(self):
        return self.representation_manager(self.request, self.context)

    def save(self):
        if self.changed:
            self.saved = save_auction(self.request)
        return self.saved


@implementer(IManager)
class BidManager(object):

    def __init__(self, request, context):
        self.request = request
        self.context = context
        self.changed = False
        self.saved = False

    def initialize(self):
        initializator = self.Initializator(self.request, self.context)
        initializator.initialize()

    def change(self):
        manager = self.changion_manager(self.request, self.context)
        self.changed = manager.manage()
        return self.changed

    def create(self, applicant):
        manager = self.creation_manager(self.request, self.context)
        creature = manager.manage(applicant)
        if creature:
            self.changed = True
        return creature

    def log(self, action, verbose):
        logger = self.log(self.request, self.context)
        logger.log(action, verbose)

    def save(self):
        if self.changed:
            self.saved = save_auction(self.request)
        return self.saved

    def delete(self):
        manager = self.deletion_manager(self.request, self.context)
        deleted = manager.manage()
        if deleted:
            self.changed = True
        return deleted

    def get_representation_manager(self):
        return self.representation_manager(self.request, self.context)


@implementer(IManager)
class QuestionManager(object):

    def __init__(self, request, context):
        self.request = request
        self.context = context
        self.changed = False
        self.saved = False

    def change(self):
        manager = self.changion_manager(self.request, self.context)
        self.changed = manager.manage()
        return self.changed

    def save(self):
        if self.changed:
            self.saved = save_auction(self.request)
        return self.saved


@implementer(IManager)
class ItemManager(object):

    def __init__(self, request, context):
        self.request = request
        self.context = context
        self.changed = False
        self.saved = False

    def change(self):
        manager = self.changion_manager(self.request, self.context)
        self.changed = manager.manage()
        return self.changed

    def create(self, applicant):
        manager = self.creation_manager(self.request, self.context)
        creature = manager.manage(applicant)
        if creature:
            self.changed = True
        return creature

    def get_representation_manager(self):
        return self.representation_manager(self.request, self.context)

    def log(self, action, verbose):
        logger = self.log(self.request, self.context)
        logger.log(action, verbose)

    def save(self):
        if self.changed:
            self.saved = save_auction(self.request)
        return self.saved


@implementer(IManager)
class CancellationManager(object):

    def __init__(self, request, context):
        self.request = request
        self.context = context
        self.changed = False
        self.saved = False

    def change(self):
        manager = self.changion_manager(self.request, self.context)
        self.changed = manager.manage()
        return self.changed

    def represent(self, method):
        representer = self.Representer(self.context)
        return representer.represent(method)

    def get_representation_manager(self):
        return self.representation_manager(self.request, self.context)

    def create(self, applicant):
        manager = self.creation_manager(self.request, self.context)
        created = manager.manage(applicant)
        if created:
            self.changed = True
        return created

    def log(self, action, verbose):
        logger = self.log(self.request, self.context)
        logger.log(action, verbose)

    def save(self):
        if self.changed:
            self.saved = save_auction(self.request)
        return self.saved


@implementer(IManager)
class DocumentManager(object):

    def __init__(self, request, context):
        self.request = request
        self.context = context
        self.changed = False
        self.saved = False

    def change(self):
        manager = self.changion_manager(self.request, self.context)
        self.changed = manager.manage()
        return self.changed

    def put(self):
        manager = self.changion_manager(self.request, self.context)
        self.changed = manager.manage()
        return self.changed

    def save(self):
        if self.changed:
            self.saved = save_auction(self.request)
        return self.saved


@implementer(IManager)
class BidDocumentManager(object):

    def __init__(self, request, context):
        self.request = request
        self.context = context
        self.changed = False
        self.saved = False

    def change(self):
        manager = self.changion_manager(self.request, self.context)
        self.changed = manager.manage()
        return self.changed

    def save(self):
        if self.changed:
            self.saved = save_auction(self.request)
        return self.saved


@implementer(IManager)
class CancellationDocumentManager(object):

    def __init__(self, request, context):
        self.request = request
        self.context = context
        self.changed = False
        self.saved = False

    def create(self, applicant):
        pass

    def save(self):
        if self.changed:
            self.saved = save_auction(self.request)
        return self.saved

    def log(self, action, verbose):
        logger = self.log(self.request, self.context)
        logger.log(action, verbose)

    def represent(self, role):
        representer = self.representer(self.context)
        return representer.represent(role)
