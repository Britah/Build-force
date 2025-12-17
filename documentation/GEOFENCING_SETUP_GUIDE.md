# Geofencing Setup Guide for Labour Management System

## Overview
The system now enforces **location-based check-ins**. Labourers can only check in or out when they are **physically within the project's defined boundary**.

---

## ✅ How It Works

### 1. **Backend Validation (Already Implemented)**
- When a labourer attempts to check in/out, the system:
  1. Gets their GPS coordinates from their device
  2. Checks if they're within the project's boundary coordinates
  3. **ALLOWS** check-in if inside ✅
  4. **DENIES** check-in if outside ⛔

### 2. **Key Functions** (in `labourers/views.py`)

```python
validate_geofence(latitude, longitude, project)
# Returns: (is_valid, message, distance_from_boundary)

point_in_polygon(point, polygon)
# Checks if GPS point is inside boundary polygon
```

---

## 🗺️ Setting Up Project Boundaries

### **Step 1: Access Geofence Setup Page**
1. Login to supervisor dashboard
2. Click **"Project Geofencing"** card
3. You'll see an interactive map

### **Step 2: Select Project**
1. Choose project from dropdown menu
2. If boundary exists, it will display on map
3. If not, you'll draw a new one

### **Step 3: Draw Boundary**
1. Click **"Go to My Location"** to center map on you
2. Or manually navigate to project location
3. Click **"Draw Boundary"** button
4. Click points on map to create polygon
5. Close polygon by clicking first point
6. Review the boundary visually

### **Step 4: Save Boundary**
1. Click **"Save Boundary"** button
2. Coordinates are saved to database
3. Confirmation message appears

### **Step 5: Test Geofence**
1. Click **"Test Current Location"** button
2. System checks if you're inside/outside
3. Shows distance if outside
4. ✅ Green = Inside (check-in allowed)
5. ⛔ Red = Outside (check-in denied)

---

## 📍 How Check-In/Out Works with Geofencing

### **Check-In Process:**
1. Labourer opens attendance page
2. Selects project and their name
3. Clicks "Check In with Camera"
4. System gets GPS coordinates automatically
5. **Validates location against project boundary**
6. If **outside boundary**:
   - ❌ Check-in **DENIED**
   - Error: "You are X meters outside the project boundary"
7. If **inside boundary**:
   - ✅ Camera opens for facial verification
   - Check-in proceeds normally

### **Check-Out Process:**
Same validation as check-in - must be at project location.

---

## 🔧 Technical Details

### **Database Field:**
```python
Project Model:
- boundary_coordinates = JSONField
  Format: [[lat1, lng1], [lat2, lng2], [lat3, lng3], ...]
  Example: [
    [-1.289617, 36.791410],
    [-1.288617, 36.792410],
    [-1.287617, 36.791410],
    [-1.289617, 36.791410]  # Closes polygon
  ]
```

### **Validation Code (in views.py):**
```python
# In check_in view (line 1051-1061):
is_valid, message, distance = validate_geofence(
    Decimal(latitude), 
    Decimal(longitude), 
    project
)

if not is_valid:
    return JsonResponse({
        'success': False,
        'error': f'⛔ Check-in denied: {message}. You must be at the project location to check in.'
    })
```

---

## 📊 Testing Examples

### **Test Scenario 1: Inside Boundary**
```
GPS: -1.2886, 36.7914 (inside polygon)
Result: ✅ Check-in ALLOWED
Message: "Location verified: You are within the project boundary"
```

### **Test Scenario 2: Outside Boundary**
```
GPS: -1.3000, 36.8000 (100m outside)
Result: ⛔ Check-in DENIED
Message: "You are 100 meters outside the project boundary"
```

---

## 🛠️ Troubleshooting

### **Problem: No GPS coordinates captured**
**Solution:** 
- Ensure browser has location permission
- Use HTTPS (required for geolocation)
- Check device GPS is enabled

### **Problem: Check-in denied but I'm at site**
**Solution:**
1. Go to Geofence Setup page
2. Test your current location
3. Check if boundary is drawn correctly
4. Adjust boundary if needed
5. Save updated boundary

### **Problem: Boundary not showing on map**
**Solution:**
1. Select project from dropdown
2. If no boundary, click "Draw Boundary"
3. Create new boundary polygon
4. Click "Save Boundary"

---

## 📱 Device Requirements

### **For Check-In:**
- GPS-enabled device (smartphone/tablet)
- Location services enabled
- Browser with geolocation support
- Internet connection

### **For Geofence Setup:**
- Desktop or mobile browser
- Internet connection
- Supervisor/admin login

---

## 🎯 Best Practices

1. **Draw accurate boundaries**
   - Include entire work area
   - Add 10-20m buffer for GPS accuracy
   - Don't make boundaries too large

2. **Test before deployment**
   - Use "Test Current Location" feature
   - Walk around site perimeter
   - Verify check-ins work everywhere on site

3. **Regular updates**
   - Update boundaries if site expands
   - Adjust for new work areas
   - Review monthly

4. **Multiple projects**
   - Each project has separate boundary
   - Labourers check in to correct project
   - System validates against selected project

---

## 🔍 Sample Boundary Coordinates

### **Small Construction Site (50m x 50m):**
```json
[
  [-1.2886, 36.7914],
  [-1.2886, 36.7919],
  [-1.2881, 36.7919],
  [-1.2881, 36.7914],
  [-1.2886, 36.7914]
]
```

### **Irregular Shape Site:**
```json
[
  [-1.2886, 36.7914],
  [-1.2887, 36.7918],
  [-1.2883, 36.7921],
  [-1.2880, 36.7917],
  [-1.2882, 36.7913],
  [-1.2886, 36.7914]
]
```

---

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Test with "Test Current Location" button
3. Verify GPS permissions are granted
4. Contact system administrator

---

## ✨ Summary

**What Changed:**
- ✅ Geofencing now **ENFORCES** location checking
- ⛔ Check-ins **DENIED** if outside boundary
- 🗺️ Interactive map for setting boundaries
- 🧪 Built-in testing feature

**What You Need to Do:**
1. Set up project boundaries using the geofence setup page
2. Test boundaries before deployment
3. Inform labourers they must be on-site to check in
4. Monitor and adjust boundaries as needed

**Result:**
✅ Only valid on-site check-ins are allowed!
