<<<<<<< HEAD
def validate_contract_document(request, operation):
    if (
        request.validated['auction_status']
        not in ['active.qualification', 'active.awarded']
    ):
        request.errors.add(
=======
def validate_contract_document(view, operation):
    if view.request.validated['auction_status'] not in \
            ['active.qualification', 'active.awarded']:
        view.request.errors.add(
>>>>>>> f3ed869... Add Prolongation views
            'body',
            'data',
            'Can\'t {0} document in current ({1}) auction status'.format(
                operation,
<<<<<<< HEAD
                request.validated['auction_status']
            )
        )
        request.errors.status = 403
=======
                view.request.validated['auction_status']
            )
        )
        view.request.errors.status = 403
>>>>>>> f3ed869... Add Prolongation views
        return
    if any(
        [
            i.status != 'active' for i in
<<<<<<< HEAD
            request.validated['auction'].lots if
            i.id in [a.lotID for a in
            request.validated['auction'].awards if
            a.id == request.validated['contract'].awardID]
        ]
    ):
        request.errors.add(
=======
            view.request.validated['auction'].lots if
            i.id in [a.lotID for a in
            view.request.validated['auction'].awards if
            a.id == view.request.validated['contract'].awardID]
        ]
    ):
        view.request.errors.add(
>>>>>>> f3ed869... Add Prolongation views
            'body',
            'data',
            'Can {} document only in active lot status'.format(operation)
        )
<<<<<<< HEAD
        request.errors.status = 403
        return
    if request.validated['contract'].status not in [
        'pending',
        'active'
    ]:
        request.errors.add(
=======
        view.request.errors.status = 403
        return
    if view.request.validated['contract'].status not in [
        'pending',
        'active'
    ]:
        view.request.errors.add(
>>>>>>> f3ed869... Add Prolongation views
            'body',
            'data',
            'Can\'t {} document in current contract status'.format(
                operation
            )
        )
<<<<<<< HEAD
        request.errors.status = 403
=======
        view.request.errors.status = 403
>>>>>>> f3ed869... Add Prolongation views
        return
    return True
