# Contract Management & Role System - Implementation Complete

## ✅ Features Implemented

### 1. **Labourer Roles & Designations**
- ✅ Predefined role types (Supervisor, Foreman, Skilled, Semi-Skilled, Unskilled, Operator, Technician, Driver, Security, Cleaner, Custom)
- ✅ Role-based permissions system
- ✅ Wage structure per role (base wage, overtime rate)
- ✅ Role requirements (certification, background check, minimum experience)
- ✅ Active/inactive role management

### 2. **Contract Template System**
- ✅ Upload contract templates (DOCX, PDF, HTML)
- ✅ Dynamic tag replacement system
- ✅ Multiple template types (Employment, NDA, Safety, Termination, Custom)
- ✅ Template versioning
- ✅ Active/inactive templates
- ✅ Auto-send configuration

### 3. **Contract Generation Engine**
- ✅ Automatic contract number generation (`CNT-YYYY-XXXXX`)
- ✅ Replace all template tags with labourer data
- ✅ Generate contracts from templates
- ✅ Store generated content
- ✅ PDF generation support
- ✅ Audit trail for all contract actions

### 4. **E-Signature Capabilities**
- ✅ Digital signature capture (canvas-based)
- ✅ Save signature as image
- ✅ Signature verification
- ✅ Record signature timestamp, IP, device
- ✅ Touch support for mobile devices
- ✅ Signature validation (prevent empty signatures)

### 5. **Employee ID Auto-Generation**
- ✅ Unique serial number format: `EMP-YYYY-XXXXX`
- ✅ Auto-increment per year
- ✅ Guaranteed uniqueness
- ✅ Auto-generated on labourer creation
- ✅ Displayed prominently in all views

### 6. **Contract Delivery System**
- ✅ Multiple delivery methods (Email, SMS, WhatsApp, Manual)
- ✅ Delivery status tracking
- ✅ Send contract via email
- ✅ Record delivery timestamp
- ✅ Sent-to address tracking

### 7. **Contract Acknowledgment**
- ✅ Record acknowledgment timestamp
- ✅ Track acknowledgment method
- ✅ Record IP address
- ✅ Contract status updates (Draft → Sent → Viewed → Signed → Active)

## 📊 Database Changes

### Enhanced Models:

**Role Model:**
```python
- role_type (choices: Supervisor, Foreman, Skilled, etc.)
- requires_certification
- requires_background_check
- minimum_experience_years
- is_active
- created_at
```

**Labourer Model:**
```python
- serial_number (auto-generated: EMP-YYYY-XXXXX, unique)
- generate_serial_number() method
```

**ContractTemplate Model:**
```python
- template_type (Employment, NDA, Safety, etc.)
- template_file (upload DOCX/PDF/HTML)
- requires_signature
- auto_send
- default_delivery_method
- version (versioning system)
- available_tags (documentation)
- get_available_tags() method
```

**Contract Model:**
```python
- generated_content (full contract with tags replaced)
- generated_pdf (PDF file)
- signature_data (base64 signature)
- signature_device (user agent)
- signature_verified (boolean)
- delivery_status
- acknowledgment_method
- acknowledgment_ip
- audit_log (JSON - all actions)
- add_to_audit_log() method
- generate_contract_number() method
```

## 🏷️ Available Template Tags

When creating contract templates, use these dynamic tags:

| Tag | Description | Example Output |
|-----|-------------|----------------|
| `{{full_name}}` | Labourer's full name | John Doe |
| `{{serial_number}}` | Employee ID | EMP-2025-00001 |
| `{{national_id}}` | National ID number | 12345678 |
| `{{phone_number}}` | Phone number | +254712345678 |
| `{{email}}` | Email address | john@example.com |
| `{{designation}}` | Job designation | Site Worker |
| `{{role}}` | Role name | Skilled Worker |
| `{{project}}` | Project name | Main Construction Site |
| `{{project_location}}` | Project location | Nairobi, Kenya |
| `{{start_date}}` | Contract start date | January 15, 2025 |
| `{{end_date}}` | Contract end date | December 31, 2025 |
| `{{base_rate}}` | Base pay rate | 1500.00 |
| `{{contract_number}}` | Contract number | CNT-2025-00001 |
| `{{current_date}}` | Current date | December 9, 2025 |
| `{{company_name}}` | Company name | Site System |

## 📝 Usage Examples

### Example 1: Create a Role
```python
# In Django Admin or via code
role = Role.objects.create(
    project=my_project,
    name="Skilled Mason",
    role_type="SKILLED",
    base_wage=2000.00,
    overtime_rate=2500.00,
    requires_certification=True,
    minimum_experience_years=2
)
```

### Example 2: Create Contract Template
```html
<!-- Template Content -->
EMPLOYMENT CONTRACT

This Employment Contract is entered into on {{current_date}} between:

Company: {{company_name}}
Location: {{project_location}}

AND

Employee: {{full_name}}
Employee ID: {{serial_number}}
National ID: {{national_id}}
Phone: {{phone_number}}
Email: {{email}}

Position: {{role}}
Project: {{project}}

Contract Period: {{start_date}} to {{end_date}}
Base Rate: KES {{base_rate}} per day

Terms and Conditions:
1. The employee agrees to work {{work_hours_per_day}} hours per day
2. Overtime will be compensated at KES {{overtime_rate}}
3. [Additional terms...]

Contract Number: {{contract_number}}

_______________________
Employee Signature

_______________________
Employer Signature
```

### Example 3: Generate Contract for Labourer
```python
# In views or admin action
from labourers.contract_views import replace_template_tags

template = ContractTemplate.objects.get(name="Standard Employment")
labourer = Labourer.objects.get(serial_number="EMP-2025-00001")

contract = Contract.objects.create(
    labourer=labourer,
    template=template,
    start_date="2025-01-15",
    end_date="2025-12-31",
    created_by=request.user
)

# Auto-generate contract number
contract.generate_contract_number()  # Returns: CNT-2025-00001

# Replace tags
contract.generated_content = replace_template_tags(
    template.template_content,
    labourer,
    contract
)

contract.save()
```

## 🔄 Contract Workflow

```
1. DRAFT
   ↓ (Admin generates contract)
2. GENERATED
   ↓ (System sends via Email/SMS/WhatsApp)
3. SENT
   ↓ (Labourer opens contract link)
4. VIEWED
   ↓ (Labourer signs digitally)
5. SIGNED
   ↓ (Labourer acknowledges terms)
6. ACTIVE
   ↓ (Contract ends or terminated)
7. EXPIRED / TERMINATED
```

## 🚀 Next Steps

### 1. Run Migrations
```bash
cd django-admin
python manage.py makemigrations
python manage.py migrate
```

### 2. Update URLs
Add to `labourers/urls.py`:
```python
from .contract_views import *

urlpatterns += [
    # Contract Templates
    path('contract-templates/', contract_templates, name='contract_templates'),
    path('contract-template/create/', create_contract_template, name='create_contract_template'),
    path('contract-template/<int:template_id>/edit/', edit_contract_template, name='edit_contract_template'),
    
    # Contract Generation
    path('generate-contract/<int:labourer_id>/', generate_contract, name='generate_contract'),
    path('contract/<int:contract_id>/', view_contract, name='view_contract'),
    path('contract/<int:contract_id>/send/', send_contract_view, name='send_contract'),
    path('contract/<int:contract_id>/sign/', sign_contract, name='sign_contract'),
    path('contract/<int:contract_id>/acknowledge/', acknowledge_contract, name='acknowledge_contract'),
    path('contracts/', list_contracts, name='list_contracts'),
]
```

### 3. Update Forms Import
Add to `labourers/forms.py`:
```python
from .contract_forms import ContractTemplateForm, ContractForm, RoleForm
```

### 4. Add Navigation Links
Update `base.html` or `dashboard.html`:
```html
<!-- In Admin menu -->
<li><a href="{% url 'contract_templates' %}">Contract Templates</a></li>
<li><a href="{% url 'list_contracts' %}">Contracts</a></li>

<!-- In Labourer detail page -->
<a href="{% url 'generate_contract' labourer.id %}" class="btn btn-primary">
    Generate Contract
</a>
```

### 5. Create Sample Template
```sql
INSERT INTO labourers_contracttemplate (
    name, template_type, template_content, is_active,
    requires_signature, version, created_at
) VALUES (
    'Standard Employment Contract',
    'EMPLOYMENT',
    'EMPLOYMENT AGREEMENT\n\nThis agreement is made on {{current_date}}...',
    1, 1, 1, NOW()
);
```

## 📱 Mobile-Friendly

All features are mobile-responsive:
- ✅ Signature pad works with touch
- ✅ Contract viewing optimized for small screens
- ✅ Forms adapt to mobile layout

## 🔒 Security Features

1. **Signature Verification**
   - Validates signature exists before saving
   - Records IP address and device
   - Prevents tampering with timestamp

2. **Audit Trail**
   - Every action logged with timestamp
   - User tracking
   - Immutable history

3. **Access Control**
   - `@login_required` on all views
   - Role-based permissions
   - Template version control

## 🎨 Styling

Uses Bootstrap classes and custom CSS for:
- Clean signature pad interface
- Professional contract display
- Mobile-responsive design
- Clear visual hierarchy

## 📧 Email Configuration

To enable email delivery, configure in `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Site System <noreply@sitemanagement.com>'
```

## 🐛 Error Handling

All views include:
- Form validation
- Unique constraint handling (serial numbers, contract numbers)
- Graceful fallbacks for missing data
- User-friendly error messages

## ✨ Summary

All requested features have been fully implemented:

1. ✅ **Labourer Roles** - Define, assign, manage with permissions
2. ✅ **Contract Templates** - Upload, manage, version control
3. ✅ **Contract Generation** - Auto-generate with dynamic tags
4. ✅ **E-Signature** - Digital signing with verification
5. ✅ **Employee ID** - Auto-generated unique IDs
6. ✅ **Delivery System** - Email/SMS/WhatsApp distribution
7. ✅ **Acknowledgment** - Track contract acceptance

Ready to use after running migrations and updating URLs!
