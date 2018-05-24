def validate_contract_create(request, **kwargs):
    if request.validated['auction'].status not in ['active.qualification', 'active.awarded']:
        request.errors.add('body', 'data',
                                'Can\'t add contract in current ({}) auction status'.format(request.validated['auction'].status))
        request.errors.status = 403
        return


def validate_contract_update(request, **kwargs):
    if request.validated['auction_status'] not in ['active.qualification', 'active.awarded']:
        request.errors.add('body', 'data', 'Can\'t update contract in current ({}) auction status'.format(
            request.validated['auction_status']))
        request.errors.status = 403
        return
    if any([i.status != 'active' for i in request.validated['auction'].lots if
            i.id in [a.lotID for a in request.validated['auction'].awards if a.id == request.context.awardID]]):
        request.errors.add('body', 'data', 'Can update contract only in active lot status')
        request.errors.status = 403
        return
