# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    APIResource,
    get_file,
    upload_file,
    update_file_content_type
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data
)
from openprocurement.auctions.core.utils import (
    apply_patch,
    save_auction,
    opresource,
)
from openprocurement.api.views.complaint_document import STATUS4ROLE


@opresource(
    name='awarding_3_0:Auction Award Complaint Documents',
    collection_path='/auctions/{auction_id}/awards/{award_id}/'
                    'complaints/{complaint_id}/documents',
    path='/auctions/{auction_id}/awards/{award_id}/'
         'complaints/{complaint_id}/documents/{document_id}',
    awardingType='awarding_3_0',
    description="Auction award complaint documents"
)
class AuctionAwardComplaintDocumentResource(APIResource):

    @json_view(permission='view_auction')
    def collection_get(self):
        """Auction Award Complaint Documents List"""
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(permission='edit_complaint', validators=(validate_file_upload,))
    def collection_post(self):
        """Auction Award Complaint Document Upload
        """
        if self.request.validated['auction_status'] not in ['active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t add document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if any([i.status != 'active' for i in self.request.validated['auction'].lots if i.id == self.request.validated['award'].lotID]):
            self.request.errors.add('body', 'data', 'Can add document only in active lot status')
            self.request.errors.status = 403
            return
        if self.context.status not in STATUS4ROLE.get(self.request.authenticated_role, []):
            self.request.errors.add('body', 'data', 'Can\'t add document in current ({}) complaint status'.format(self.context.status))
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.context.documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Created auction award complaint document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_award_complaint_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='view_auction')
    def get(self):
        """Auction Award Complaint Document Read"""
        if self.request.params.get('download'):
            return get_file(self.request)
        document = self.request.validated['document']
        document_data = document.serialize("view")
        document_data['previousVersions'] = [
            i.serialize("view")
            for i in self.request.validated['documents']
            if i.url != document.url
        ]
        return {'data': document_data}

    @json_view(validators=(validate_file_update,), permission='edit_complaint')
    def put(self):
        """Auction Award Complaint Document Update"""
        if self.request.authenticated_role != self.context.author:
            self.request.errors.add('url', 'role', 'Can update document only author')
            self.request.errors.status = 403
            return
        if self.request.validated['auction_status'] not in ['active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if any([i.status != 'active' for i in self.request.validated['auction'].lots if i.id == self.request.validated['award'].lotID]):
            self.request.errors.add('body', 'data', 'Can update document only in active lot status')
            self.request.errors.status = 403
            return
        if self.request.validated['complaint'].status not in STATUS4ROLE.get(self.request.authenticated_role, []):
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) complaint status'.format(self.request.validated['complaint'].status))
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.request.validated['complaint'].documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Updated auction award complaint document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_award_complaint_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_document_data,), permission='edit_complaint')
    def patch(self):
        """Auction Award Complaint Document Update"""
        if self.request.authenticated_role != self.context.author:
            self.request.errors.add('url', 'role', 'Can update document only author')
            self.request.errors.status = 403
            return
        if self.request.validated['auction_status'] not in ['active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if any([i.status != 'active' for i in self.request.validated['auction'].lots if i.id == self.request.validated['award'].lotID]):
            self.request.errors.add('body', 'data', 'Can update document only in active lot status')
            self.request.errors.status = 403
            return
        if self.request.validated['complaint'].status not in STATUS4ROLE.get(self.request.authenticated_role, []):
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) complaint status'.format(self.request.validated['complaint'].status))
            self.request.errors.status = 403
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated auction award complaint document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_award_complaint_document_patch'}))
            return {'data': self.request.context.serialize("view")}

