from openprocurement.auctions.core.plugins.awarding.v2_1.constants import STATUS4ROLE


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
