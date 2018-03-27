# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    APIResource,
    get_file,
    upload_file,
    update_file_content_type,
)
from openprocurement.api.validation import (
    validate_patch_document_data
)

from openprocurement.auctions.core.utils import (
    apply_patch,
    save_auction,
    opresource,
)
from openprocurement.auctions.core.validation import (
    validate_file_update,
    validate_file_upload,
    validate_file_upload_post_common,
    validate_file_update_put_common,
    validate_patch_document_data_patch_common
)


@opresource(
    name='awarding_1_0:Auction Award Complaint Documents',
    collection_path='/auctions/{auction_id}/awards/{award_id}/complaints/{complaint_id}/documents',
    path='/auctions/{auction_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}',
    awardingType='awarding_1_0',
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

    @json_view(permission='edit_complaint',
               validators=(validate_file_upload, validate_file_upload_post_common))
    def collection_post(self):
        """Auction Award Complaint Document Upload
        """
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

    @json_view(validators=(validate_file_update, validate_file_update_put_common),
               permission='edit_complaint')
    def put(self):
        """Auction Award Complaint Document Update"""
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.request.validated['complaint'].documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Updated auction award complaint document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_award_complaint_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json",
               validators=(validate_patch_document_data, validate_patch_document_data_patch_common),
               permission='edit_complaint')
    def patch(self):
        """Auction Award Complaint Document Update"""
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated auction award complaint document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_award_complaint_document_patch'}))
            return {'data': self.request.context.serialize("view")}
