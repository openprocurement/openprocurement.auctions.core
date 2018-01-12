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
from openprocurement.auctions.core.validation import (
    validate_file_upload_award_post_common,
    validate_file_update_award_put_common,
    validate_patch_document_data_award_patch_common
)
from openprocurement.auctions.core.utils import (
    apply_patch,
    save_auction,
    opresource,
)


@opresource(
    name='dgfInsider:Auction Award Documents',
    collection_path='/auctions/{auction_id}/awards/{award_id}/documents',
    path='/auctions/{auction_id}/awards/{award_id}/documents/{document_id}',
    awardingType='awarding_2_0',
    description="Insider auction award documents"
)
@opresource(
    name='dgfFinancialAssets:Auction Award Documents',
    collection_path='/auctions/{auction_id}/awards/{award_id}/documents',
    path='/auctions/{auction_id}/awards/{award_id}/documents/{document_id}',
    awardingType='awarding_2_0',
    description="Financial auction award documents"
)
@opresource(
    name='dgfOtherAssets:Auction Award Documents',
    collection_path='/auctions/{auction_id}/awards/{award_id}/documents',
    path='/auctions/{auction_id}/awards/{award_id}/documents/{document_id}',
    awardingType='awarding_2_0',
    description="Auction award documents"
)
class AuctionAwardDocumentResource(APIResource):

    def validate_award_document(self, operation):
        if operation == 'update' and self.request.authenticated_role != self.context.author:
            self.request.errors.add('url', 'role', 'Can update document only author')
            self.request.errors.status = 403
            return
        if self.request.validated['auction_status'] != 'active.qualification':
            self.request.errors.add('body', 'data', 'Can\'t {} document in current ({}) auction status'.format(operation,
                                                                                                              self.request.validated[
                                                                                                                  'auction_status']))
            self.request.errors.status = 403
            return
        if any([i.status != 'active' for i in self.request.validated['auction'].lots if
                i.id == self.request.validated['award'].lotID]):
            self.request.errors.add('body', 'data', 'Can {} document only in active lot status'.format(operation))
            self.request.errors.status = 403
            return
        return True

    @json_view(permission='view_auction')
    def collection_get(self):
        """Auction Award Documents List"""
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(validators=(validate_file_upload, validate_file_upload_award_post_common),
               permission='edit_auction_award')
    def collection_post(self):
        """Auction Award Document Upload
        """
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.context.documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Created auction award document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_award_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='view_auction')
    def get(self):
        """Auction Award Document Read"""
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

    @json_view(validators=(validate_file_update, validate_file_update_award_put_common),
               permission='edit_auction_award')
    def put(self):
        """Auction Award Document Update"""
        if self.request.authenticated_role != self.request.context.author:
            self.request.errors.add('url', 'role', 'Can update document only author')
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.request.validated['award'].documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Updated auction award document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_award_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json",
               permission='edit_auction_award',
               validators=(validate_patch_document_data,
                           validate_patch_document_data_award_patch_common))
    def patch(self):
        """Auction Award Document Update"""
        if self.request.authenticated_role != self.request.context.author:
            self.request.errors.add('url', 'role', 'Can update document only author')
            self.request.errors.status = 403
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated auction award document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_award_document_patch'}))
            return {'data': self.request.context.serialize("view")}

