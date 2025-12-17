"""
Contract Generation and Management Views
Handles template upload, contract generation, e-signature, and delivery
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.utils import timezone
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from datetime import datetime, timedelta
import base64
import json
import re

from .models import Contract, ContractTemplate, Labourer, User
from .contract_forms import ContractTemplateForm, ContractForm

# ==================== TEMPLATE MANAGEMENT ====================

@login_required
def contract_templates(request):
    """List all contract templates"""
    templates = ContractTemplate.objects.all()
    context = {
        'templates': templates,
    }
    return render(request, 'labourers/contract_templates.html', context)

@login_required
def create_contract_template(request):
    """Create new contract template"""
    if request.method == 'POST':
        form = ContractTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()
            messages.success(request, f'Template "{template.name}" created successfully!')
            return redirect('contract_templates')
    else:
        form = ContractTemplateForm()
    
    context = {
        'form': form,
        'available_tags': ContractTemplate().get_available_tags(),
    }
    return render(request, 'labourers/create_contract_template.html', context)

@login_required
def edit_contract_template(request, template_id):
    """Edit existing contract template"""
    template = get_object_or_404(ContractTemplate, id=template_id)
    
    if request.method == 'POST':
        form = ContractTemplateForm(request.POST, request.FILES, instance=template)
        if form.is_valid():
            # Increment version if content changed
            if form.cleaned_data['template_content'] != template.template_content:
                template.version += 1
            form.save()
            messages.success(request, f'Template "{template.name}" updated successfully!')
            return redirect('contract_templates')
    else:
        form = ContractTemplateForm(instance=template)
    
    context = {
        'form': form,
        'template': template,
        'available_tags': template.get_available_tags(),
    }
    return render(request, 'labourers/edit_contract_template.html', context)

# ==================== CONTRACT GENERATION ====================

def replace_template_tags(template_content, labourer, contract=None):
    """Replace all template tags with actual labourer data"""
    from datetime import date
    
    replacements = {
        '{{full_name}}': labourer.full_name,
        '{{serial_number}}': labourer.serial_number or 'N/A',
        '{{national_id}}': labourer.national_id,
        '{{phone_number}}': labourer.phone_number,
        '{{email}}': labourer.email or 'N/A',
        '{{designation}}': labourer.designation or 'N/A',
        '{{role}}': labourer.role.name if labourer.role else 'N/A',
        '{{project}}': labourer.project.name if labourer.project else 'N/A',
        '{{project_location}}': labourer.project.location if labourer.project else 'N/A',
        '{{current_date}}': date.today().strftime('%B %d, %Y'),
        '{{company_name}}': getattr(settings, 'COMPANY_NAME', 'Site System'),
    }
    
    if contract:
        replacements.update({
            '{{contract_number}}': contract.contract_number or 'PENDING',
            '{{start_date}}': contract.start_date.strftime('%B %d, %Y') if contract.start_date else 'N/A',
            '{{end_date}}': contract.end_date.strftime('%B %d, %Y') if contract.end_date else 'Ongoing',
            '{{base_rate}}': str(labourer.role.base_wage) if labourer.role else 'N/A',
        })
    
    # Replace all tags
    content = template_content
    for tag, value in replacements.items():
        content = content.replace(tag, str(value))
    
    return content

@login_required
def generate_contract(request, labourer_id):
    """Generate contract for a labourer"""
    labourer = get_object_or_404(Labourer, id=labourer_id)
    
    if request.method == 'POST':
        template_id = request.POST.get('template_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        template = get_object_or_404(ContractTemplate, id=template_id)
        
        # Create contract
        contract = Contract(
            labourer=labourer,
            template=template,
            start_date=start_date,
            end_date=end_date if end_date else None,
            created_by=request.user,
            status='GENERATED'
        )
        
        # Generate contract number
        contract.generate_contract_number()
        
        # Generate content
        contract.generated_content = replace_template_tags(
            template.template_content,
            labourer,
            contract
        )
        contract.terms_and_conditions = contract.generated_content
        
        contract.save()
        contract.add_to_audit_log('Contract Generated', request.user)
        
        messages.success(request, f'Contract {contract.contract_number} generated successfully!')
        
        # Auto-send if template has auto_send enabled
        if template.auto_send:
            send_contract(contract, template.default_delivery_method)
        
        return redirect('view_contract', contract_id=contract.id)
    
    # GET request - show template selection
    templates = ContractTemplate.objects.filter(is_active=True)
    context = {
        'labourer': labourer,
        'templates': templates,
    }
    return render(request, 'labourers/generate_contract.html', context)

@login_required
def view_contract(request, contract_id):
    """View generated contract"""
    contract = get_object_or_404(Contract, id=contract_id)
    context = {
        'contract': contract,
    }
    return render(request, 'labourers/view_contract.html', context)

# ==================== CONTRACT DELIVERY ====================

def send_contract(contract, method='EMAIL'):
    """Send contract via specified method"""
    from django.core.mail import send_mail
    
    contract.sent_via = method
    contract.sent_at = timezone.now()
    
    if method == 'EMAIL':
        if contract.labourer.email:
            send_mail(
                subject=f'Employment Contract - {contract.contract_number}',
                message=f'''Dear {contract.labourer.full_name},

Please find your employment contract attached.

Contract Number: {contract.contract_number}
Start Date: {contract.start_date}

Please review and sign the contract.

Best regards,
Site System''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[contract.labourer.email],
                fail_silently=False,
            )
            contract.sent_to = contract.labourer.email
            contract.delivery_status = 'Sent'
            contract.status = 'SENT'
        else:
            contract.delivery_status = 'Failed - No email'
    
    elif method == 'SMS':
        # Implement SMS sending (Twilio, Africa's Talking, etc.)
        contract.sent_to = contract.labourer.phone_number
        contract.delivery_status = 'SMS Not Configured'
    
    elif method == 'WHATSAPP':
        # Implement WhatsApp sending
        contract.sent_to = contract.labourer.phone_number
        contract.delivery_status = 'WhatsApp Not Configured'
    
    contract.save()
    contract.add_to_audit_log(f'Contract Sent via {method}')

@login_required
def send_contract_view(request, contract_id):
    """Send contract to labourer"""
    contract = get_object_or_404(Contract, id=contract_id)
    
    if request.method == 'POST':
        method = request.POST.get('method', 'EMAIL')
        send_contract(contract, method)
        messages.success(request, f'Contract sent via {method}!')
        return redirect('view_contract', contract_id=contract.id)
    
    context = {
        'contract': contract,
    }
    return render(request, 'labourers/send_contract.html', context)

# ==================== E-SIGNATURE ====================

@login_required
def sign_contract(request, contract_id):
    """Digital signature page"""
    contract = get_object_or_404(Contract, id=contract_id)
    
    if request.method == 'POST':
        signature_data = request.POST.get('signature_data')
        
        if signature_data:
            # Save signature
            contract.signature_data = signature_data
            contract.signature_timestamp = timezone.now()
            contract.signature_ip = get_client_ip(request)
            contract.signature_device = request.META.get('HTTP_USER_AGENT', '')
            contract.signature_verified = True
            contract.status = 'SIGNED'
            
            # Convert base64 to image file
            if ',' in signature_data:
                signature_data = signature_data.split(',')[1]
            
            image_data = base64.b64decode(signature_data)
            contract.signature_image.save(
                f'signature_{contract.contract_number}.png',
                ContentFile(image_data),
                save=False
            )
            
            contract.save()
            contract.add_to_audit_log('Contract Signed', request.user, f'IP: {contract.signature_ip}')
            
            messages.success(request, 'Contract signed successfully!')
            return redirect('view_contract', contract_id=contract.id)
    
    context = {
        'contract': contract,
    }
    return render(request, 'labourers/sign_contract.html', context)

@login_required
def acknowledge_contract(request, contract_id):
    """Record contract acknowledgment"""
    contract = get_object_or_404(Contract, id=contract_id)
    
    if request.method == 'POST':
        contract.acknowledged_at = timezone.now()
        contract.acknowledgment_method = 'Web Portal'
        contract.acknowledgment_ip = get_client_ip(request)
        contract.status = 'ACTIVE'
        contract.save()
        contract.add_to_audit_log('Contract Acknowledged', request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Contract acknowledged successfully'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# ==================== HELPER FUNCTIONS ====================

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# ==================== CONTRACT LISTING ====================

@login_required
def list_contracts(request):
    """List all contracts"""
    contracts = Contract.objects.select_related('labourer', 'template').all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        contracts = contracts.filter(status=status)
    
    # Search
    search = request.GET.get('search')
    if search:
        contracts = contracts.filter(
            Q(contract_number__icontains=search) |
            Q(labourer__full_name__icontains=search) |
            Q(labourer__serial_number__icontains=search)
        )
    
    context = {
        'contracts': contracts,
    }
    return render(request, 'labourers/list_contracts.html', context)
