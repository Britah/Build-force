"""
URL Configuration for Contract Management System
Add these to your main labourers/urls.py file
"""

from django.urls import path
from .contract_views import (
    # Template Management
    contract_templates,
    create_contract_template,
    edit_contract_template,
    
    # Contract Generation
    generate_contract,
    view_contract,
    
    # Contract Delivery
    send_contract_view,
    
    # E-Signature
    sign_contract,
    acknowledge_contract,
    
    # Contract Listing
    list_contracts,
)

# Add these patterns to your existing urlpatterns
contract_urlpatterns = [
    # Contract Templates
    path('contract-templates/', contract_templates, name='contract_templates'),
    path('contract-template/create/', create_contract_template, name='create_contract_template'),
    path('contract-template/<int:template_id>/edit/', edit_contract_template, name='edit_contract_template'),
    
    # Contract Generation
    path('generate-contract/<int:labourer_id>/', generate_contract, name='generate_contract'),
    path('contract/<int:contract_id>/', view_contract, name='view_contract'),
    
    # Contract Delivery
    path('contract/<int:contract_id>/send/', send_contract_view, name='send_contract'),
    
    # E-Signature
    path('contract/<int:contract_id>/sign/', sign_contract, name='sign_contract'),
    path('contract/<int:contract_id>/acknowledge/', acknowledge_contract, name='acknowledge_contract'),
    
    # Contract Listing
    path('contracts/', list_contracts, name='list_contracts'),
]
