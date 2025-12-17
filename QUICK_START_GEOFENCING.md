# Quick Start - Geofencing Feature

## ⚡ Quick Setup (5 Minutes)

### Step 1: Add Project Boundaries
```bash
cd django-admin
python manage.py shell < add_sample_boundaries.py
```
OR manually in Admin Panel:
1. Go to http://127.0.0.1:8000/admin/
2. Click "Projects"
3. Edit a project
4. Add to "Boundary coordinates" field:
```json
[[-1.2850, 36.8150], [-1.2850, 36.8200], [-1.2900, 36.8200], [-1.2900, 36.8150]]
```
5. Save

### Step 2: Test the Demo
1. Open `geofence-demo.html` in your browser
2. Click "Get My Location"
3. See if you're inside/outside the sample boundary
4. Try "Simulate Outside Location" to see denial message

### Step 3: Test Live Check-In
1. Run server: `python manage.py runserver`
2. Login at: http://127.0.0.1:8000/labourers/login/
3. Go to Attendance page
4. Select a Project (with boundaries)
5. Select a Labourer
6. Click "Check In with Camera"
7. Allow location permission when prompted
8. System validates your location automatically

## 📍 Getting Real Coordinates

### Method 1: Google Maps
1. Open Google Maps: https://maps.google.com
2. Right-click on your project location
3. Click the coordinates (e.g., -1.2850, 36.8150)
4. They're now copied to clipboard
5. Repeat for all corners of your project area

### Method 2: On-Site
1. Go to your project site
2. Open `geofence-demo.html` on your phone
3. Click "Get My Location"
4. Copy the displayed coordinates
5. Walk to each corner and collect coordinates

### Method 3: Use Your Phone
1. Open Google Maps app
2. Long-press on location
3. Coordinates appear at top
4. Tap to copy

## 🎯 Expected Behavior

### ✅ Check-In ALLOWED
- User is inside project boundary
- Message: "✅ John Doe checked in successfully at Main Site. Location verified: You are within the project boundary"

### ⛔ Check-In DENIED
- User is outside project boundary
- Message: "⛔ Check-in denied: You are 150 meters outside the project boundary. You must be at the project location to check in."

### ⚠️ No Boundary
- Project has no boundary_coordinates defined
- Check-in allowed with warning
- Message: "✅ Checked in. No geofence boundary defined for this project"

## 🔧 Troubleshooting

### Location Not Working?
1. **Enable Location Services**
   - Windows: Settings → Privacy → Location → On
   - Chrome: Settings → Privacy → Location → Allow

2. **Use HTTPS or Localhost**
   - ✅ Works: http://127.0.0.1:8000
   - ✅ Works: http://localhost:8000
   - ❌ Won't work: http://192.168.x.x:8000 (use HTTPS)

3. **Check Browser Console**
   - Press F12
   - Click "Console" tab
   - Look for errors

### Always Denied?
1. **Check Coordinates Format**
   - ✅ Correct: `[[-1.2850, 36.8150], ...]` (latitude first)
   - ❌ Wrong: `[[36.8150, -1.2850], ...]` (longitude first)

2. **Verify Boundary is Closed**
   - First point should match last point
   - Example: `[[-1.2850, 36.8150], [-1.2850, 36.8200], ..., [-1.2850, 36.8150]]`

3. **Use Demo to Test**
   - Open `geofence-demo.html`
   - Verify the boundary makes sense on the map

## 📊 View Stored Location Data

### In Django Admin
1. Go to http://127.0.0.1:8000/admin/
2. Click "Attendance logs"
3. Click on any entry
4. See: latitude, longitude, location_verified, location_accuracy

### In Database
```bash
python manage.py shell
```
```python
from labourers.models import AttendanceLog

# Get recent check-ins
logs = AttendanceLog.objects.filter(location_verified=True).order_by('-log_timestamp')[:10]

for log in logs:
    print(f"{log.labourer.full_name}: {log.latitude}, {log.longitude} - {log.location_verified}")
```

## 🎓 Understanding the Algorithm

The system uses **Ray-Casting Algorithm**:

```
1. Draw a ray from user's location to infinity
2. Count how many times it crosses the boundary
3. Odd crossings = INSIDE (allowed)
4. Even crossings = OUTSIDE (denied)
```

Visual example:
```
    Boundary
    +-------+
    |   ✓   |  ← User inside (ray crosses 1 time = odd)
    |       |
    +-------+
         ✗      ← User outside (ray crosses 0 times = even)
```

## 🚀 Production Checklist

Before deploying:
- [ ] All projects have boundary_coordinates defined
- [ ] Test check-in at each project site
- [ ] Verify GPS accuracy is acceptable (5-20m)
- [ ] Train supervisors on the new workflow
- [ ] Test on different devices/browsers
- [ ] Enable HTTPS if using network IPs
- [ ] Document project boundaries for future reference

## 📞 Need Help?

1. Check `GEOFENCING_README.md` for detailed documentation
2. Test with `geofence-demo.html` first
3. Review browser console for errors (F12)
4. Verify coordinates on Google Maps

---

**Pro Tip**: Start with one project, test thoroughly, then roll out to others!
