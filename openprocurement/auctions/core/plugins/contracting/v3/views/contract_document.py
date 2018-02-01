# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_file,
    upload_file,
    update_file_content_type,
    json_view,
    context_unpack,
    APIResource,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data,
)
from openprocurement.auctions.core.utils import (
    save_auction,
    apply_patch,
    opresource,
)
from openprocurement.auctions.core.plugins.contracting.v3.validators import (
    validate_contract_document
)


@opresource(
    name='awarding_3_0:Auction Contract Documents',
    collection_path='/auctions/{auction_id}/contracts/{contract_id}/documents',
    path='/auctions/{auction_id}/contracts/{contract_id}/documents/{document_id}',
    awardingType='awarding_3_0',
    description="Financial auction contract documents"
)
class BaseAuctionAwardContractDocumentResource(APIResource):

    @json_view(permission='view_auction')
    def collection_get(self):
        """Auction Contract Documents List"""
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(permission='edit_auction', validators=(validate_file_upload,))
    def collection_post(self):
        """Auction Contract Document Upload
        """
        if not validate_contract_document(self, 'add'):
            return
        document = upload_file(self.request)
        self.context.documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Created auction contract document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_contract_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='view_auction')
    def get(self):
        """Auction Contract Document Read"""
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

    @json_view(validators=(validate_file_update,), permission='edit_auction')
    def put(self):
        """Auction Contract Document Update"""
        if not validate_contract_document(self, 'update'):
            return
        document = upload_file(self.request)
        self.request.validated['contract'].documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Updated auction contract document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_contract_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_document_data,), permission='edit_auction')
    def patch(self):
        """Auction Contract Document Update"""
        if not validate_contract_document(self, 'update'):
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated auction contract document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_contract_document_patch'}))
            return {'data': self.request.context.serialize("view")}

