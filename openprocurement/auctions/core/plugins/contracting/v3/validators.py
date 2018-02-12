def validate_contract_document(request, operation):
    if (
        request.validated['auction_status']
        not in ['active.qualification', 'active.awarded']
    ):
        request.errors.add(
            'body',
            'data',
            'Can\'t {0} document in current ({1}) auction status'.format(
                operation,
                request.validated['auction_status']
            )
        )
        request.errors.status = 403
        return
    if any(
        [
            i.status != 'active' for i in
            request.validated['auction'].lots if
            i.id in [a.lotID for a in
            request.validated['auction'].awards if
            a.id == request.validated['contract'].awardID]
        ]
    ):
        request.errors.add(
            'body',
            'data',
            'Can {} document only in active lot status'.format(operation)
        )
        request.errors.status = 403
        return
    if request.validated['contract'].status not in [
        'pending',
        'active'
    ]:
        request.errors.add(
            'body',
            'data',
            'Can\'t {} document in current contract status'.format(
                operation
            )
        )
        request.errors.status = 403
        return
    return True
