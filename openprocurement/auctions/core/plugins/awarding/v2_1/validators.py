from openprocurement.api.constants import STATUS4ROLE
from openprocurement.api.utils import get_now


def validate_award_patch(request):
    if request.validated['auction'] not in ['active.qualification', 'active.awarded']:
        request.errors.add('body', 'data',
                                'Can\'t update award in current ({}) auction status'.format(request.validated['auction'].status))
        request.errors.status = 403
        return
    if request.context.status in ['unsuccessful', 'cancelled']:
        request.errors.add('body', 'data', 'Can\'t update award in current ({}) status'.format(request.context.status))
        request.errors.status = 403
        return


def validate_complaint_create(request):
    if request.validated['auction'].status not in ['active.qualification', 'active.awarded']:
        request.errors.add('body', 'data',
                                'Can\'t add complaint in current ({}) auction status'.format(auction.status))
        request.errors.status = 403
        return
    if any([i.status != 'active' for i in request.validated['auction'].lots if i.id == request.context.lotID]):
        request.errors.add('body', 'data', 'Can add complaint only in active lot status')
        request.errors.status = 403
        return
    if request.context.complaintPeriod and \
            (request.context.complaintPeriod.startDate and request.context.complaintPeriod.startDate > get_now() or
                     request.context.complaintPeriod.endDate and request.context.complaintPeriod.endDate < get_now()):
        request.errors.add('body', 'data', 'Can add complaint only in complaintPeriod')
        request.errors.status = 403
        return


def validate_complaint_patch(request):
    if request.validated['auction'].status not in ['active.qualification', 'active.awarded']:
        request.errors.add('body', 'data',
                                'Can\'t update complaint in current ({}) auction status'.format(request.validated['auction'].status))
        request.errors.status = 403
        return
    if any([i.status != 'active' for i in request.validated['auction'].lots if i.id == request.validated['award'].lotID]):
        request.errors.add('body', 'data', 'Can update complaint only in active lot status')
        request.errors.status = 403
        return
    if request.context.status not in ['draft', 'claim', 'answered', 'pending']:
        request.errors.add('body', 'data',
                                'Can\'t update complaint in current ({}) status'.format(request.context.status))
        request.errors.status = 403
        return


def validate_complaint_document_create(request):
    if request.validated['auction_status'] not in ['active.qualification', 'active.awarded']:
        request.errors.add('body', 'data', 'Can\'t add document in current ({}) auction status'.format(
            request.validated['auction_status']))
        request.errors.status = 403
        return
    if any([i.status != 'active' for i in request.validated['auction'].lots if
            i.id == request.validated['award'].lotID]):
        request.errors.add('body', 'data', 'Can add document only in active lot status')
        request.errors.status = 403
        return
    if request.context.status not in STATUS4ROLE.get(request.authenticated_role, []):
        request.errors.add('body', 'data',
                                'Can\'t add document in current ({}) complaint status'.format(request.context.status))
        request.errors.status = 403
        return


def validate_complaint_document_update(request):
    if request.authenticated_role != request.context.author:
        request.errors.add('url', 'role', 'Can update document only author')
        request.errors.status = 403
        return
    if request.validated['auction_status'] not in ['active.qualification', 'active.awarded']:
        request.errors.add('body', 'data', 'Can\'t update document in current ({}) auction status'.format(
            request.validated['auction_status']))
        request.errors.status = 403
        return
    if any([i.status != 'active' for i in request.validated['auction'].lots if
            i.id == request.validated['award'].lotID]):
        request.errors.add('body', 'data', 'Can update document only in active lot status')
        request.errors.status = 403
        return
    if request.validated['complaint'].status not in STATUS4ROLE.get(request.authenticated_role, []):
        request.errors.add('body', 'data', 'Can\'t update document in current ({}) complaint status'.format(
            request.validated['complaint'].status))
        request.errors.status = 403
        return
