# Quick Start Guide - Contract & Role System

## 🚀 Setup (5 Minutes)

### Step 1: Run Database Migrations
```bash
cd django-admin
python manage.py makemigrations labourers
python manage.py migrate
```

### Step 2: Update URLs
Edit `labourers/urls.py` and add at the end:
```python
# Import contract URLs
from .contract_urls import contract_urlpatterns

# Add to your urlpatterns
urlpatterns += contract_urlpatterns
```

### Step 3: Test Employee ID Generation
```bash
python manage.py shell
```
```python
from labourers.models import Labourer

# Check existing labourers - serial_number should auto-generate
labourers = Labourer.objects.all()
for lab in labourers:
    if not lab.serial_number:
        lab.save()  # This will trigger auto-generation
    print(f"{lab.full_name}: {lab.serial_number}")
```

## 📋 Quick Usage

### Create a Role
1. Go to Admin Panel → Roles
2. Click "Add Role"
3. Fill in:
   - Name: "Skilled Mason"
   - Role Type: "Skilled Worker"
   - Base Wage: 2000.00
   - Overtime Rate: 2500.00
4. Save

### Create Contract Template
1. Go to `/labourers/contract-templates/`
2. Click "Create New Template"
3. Fill in:
   - Name: "Standard Employment Contract"
   - Type: "Employment Contract"
   - Template Content:
```
EMPLOYMENT CONTRACT

Date: {{current_date}}
Contract Number: {{contract_number}}

EMPLOYEE DETAILS
Name: {{full_name}}
Employee ID: {{serial_number}}
National ID: {{national_id}}
Phone: {{phone_number}}
Email: {{email}}

POSITION
Role: {{role}}
Project: {{project}}
Location: {{project_location}}

CONTRACT PERIOD
Start Date: {{start_date}}
End Date: {{end_date}}

COMPENSATION
Base Rate: KES {{base_rate}} per day

I, {{full_name}}, agree to the terms above.

_______________________
Signature
```
4. Check "Requires Signature"
5. Save

### Generate Contract for Labourer
1. Go to Labourers list
2. Click on a labourer
3. Click "Generate Contract"
4. Select template
5. Set start date and end date
6. Click "Generate Contract"
7. Contract is created with unique number (CNT-2025-00001)

### Send Contract
1. View the generated contract
2. Click "Send Contract"
3. Choose method (Email/SMS/WhatsApp)
4. Click "Send"
5. Status updates to "Sent"

### Sign Contract (Labourer View)
1. Labourer receives contract link
2. Opens contract signing page
3. Reviews contract content
4. Signs on the digital signature pad
5. Clicks "Confirm & Sign"
6. Signature saved, status → "Signed"

## 🎯 Testing Checklist

- [ ] Employee IDs auto-generate (EMP-2025-XXXXX format)
- [ ] Roles can be created with permissions
- [ ] Contract templates save successfully
- [ ] Template tags display in help text
- [ ] Contracts generate with replaced tags
- [ ] Contract numbers auto-increment
- [ ] Signature pad works (desktop & mobile)
- [ ] Signatures save as images
- [ ] Contract status updates correctly
- [ ] Audit log tracks all actions

## 🔧 Troubleshooting

### Migration Errors
```bash
# If you get "field already exists" errors
python manage.py migrate labourers --fake
python manage.py migrate
```

### Serial Number Not Generating
```python
# Manually trigger for all labourers
from labourers.models import Labourer
for lab in Labourer.objects.filter(serial_number__isnull=True):
    lab.save()
```

### Template Tags Not Replacing
- Check template content has correct tag format: `{{tag_name}}`
- Ensure labourer has all required fields filled
- Review contract_views.py `replace_template_tags()` function

## 📱 Mobile Testing

1. Open signature page on phone
2. Test touch drawing
3. Verify signature saves
4. Check contract display is readable

## 🎓 Advanced Usage

### Custom Role Permissions
```python
role = Role.objects.get(name="Foreman")
role.permissions = {
    'can_approve_timesheets': True,
    'can_manage_equipment': True,
    'can_create_tasks': True,
    'can_view_reports': True,
    'access_level': 3
}
role.save()
```

### Bulk Contract Generation
```python
from labourers.models import Labourer, ContractTemplate, Contract
from labourers.contract_views import replace_template_tags
from datetime import date, timedelta

template = ContractTemplate.objects.get(name="Standard Employment")
labourers = Labourer.objects.filter(status='ACTIVE')

for labourer in labourers:
    contract = Contract.objects.create(
        labourer=labourer,
        template=template,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        created_by=request.user
    )
    contract.generate_contract_number()
    contract.generated_content = replace_template_tags(
        template.template_content,
        labourer,
        contract
    )
    contract.save()
    print(f"Generated {contract.contract_number} for {labourer.full_name}")
```

### Check Contract Status
```python
from labourers.models import Contract

# Pending signatures
pending = Contract.objects.filter(status='SENT', signature_verified=False)
print(f"{pending.count()} contracts awaiting signature")

# Active contracts
active = Contract.objects.filter(status='ACTIVE')
print(f"{active.count()} active contracts")

# Expiring soon (next 30 days)
from datetime import date, timedelta
expiring = Contract.objects.filter(
    end_date__lte=date.today() + timedelta(days=30),
    end_date__gte=date.today(),
    status='ACTIVE'
)
for contract in expiring:
    print(f"{contract.contract_number} expires on {contract.end_date}")
```

## 🎉 You're All Set!

The system is now ready to:
1. ✅ Auto-generate employee IDs
2. ✅ Manage roles with permissions
3. ✅ Create contract templates
4. ✅ Generate customized contracts
5. ✅ Capture digital signatures
6. ✅ Track contract lifecycle
7. ✅ Maintain audit trails

**Next**: Create your first contract template and test the full workflow!
