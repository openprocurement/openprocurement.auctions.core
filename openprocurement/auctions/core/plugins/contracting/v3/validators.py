def validate_contract_document(view, operation):
    if view.request.validated['auction_status'] not in \
        ['active.qualification', 'active.awarded']:
        view.request.errors.add(
            'body',
            'data',
            'Can\'t {0} document in current ({1}) auction status'.format(
                operation,
                view.request.validated['auction_status']
            )
        )
        view.request.errors.status = 403
        return
    if any(
        [
            i.status != 'active' for i in
            view.request.validated['auction'].lots if
            i.id in [a.lotID for a in
            view.request.validated['auction'].awards if
            a.id == view.request.validated['contract'].awardID]
        ]
    ):
        view.request.errors.add(
            'body',
            'data',
            'Can {} document only in active lot status'.format(operation)
        )
        view.request.errors.status = 403
        return
    if view.request.validated['contract'].status not in [
        'pending',
        'active'
    ]:
        view.request.errors.add(
            'body',
            'data',
            'Can\'t {} document in current contract status'.format(
                operation
            )
        )
        view.request.errors.status = 403
        return
    return True
