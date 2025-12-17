# Geofencing Feature - Site System

## Overview
The Site System now includes **location-based check-in validation** (geofencing) that ensures labourers can only check in/out when they are physically present at the project location.

## How It Works

### 1. **Project Boundaries**
- Each project can have GPS coordinate boundaries defined
- Boundaries are stored as polygon coordinates: `[[lat1, lng1], [lat2, lng2], ...]`
- When adding/editing projects, define the boundary coordinates

### 2. **Check-In Process**
1. Supervisor selects the **Project** from dropdown
2. Selects the **Labourer** to check in
3. Clicks "Check In with Camera"
4. System automatically captures GPS location
5. Backend validates if location is inside project boundary
6. If inside → Check-in allowed ✅
7. If outside → Check-in denied ⛔

### 3. **Geofence Validation**
The system uses the **ray-casting algorithm** to determine if a point is inside a polygon:
- Draws a ray from the user's location
- Counts how many times it crosses the boundary
- Odd crossings = inside, Even crossings = outside

## Setting Up Project Boundaries

### Option 1: Using Django Admin
1. Go to Admin Panel → Projects
2. Edit a project
3. Add `boundary_coordinates` as JSON:
```json
[
  [-1.2850, 36.8150],
  [-1.2850, 36.8200],
  [-1.2900, 36.8200],
  [-1.2900, 36.8150]
]
```

### Option 2: Using Tools
Use the **geofence-demo.html** file to:
1. View a map with sample boundaries
2. Test your current location
3. Understand how the validation works
4. Get coordinate examples

### Option 3: Google Maps
1. Open Google Maps
2. Right-click on map corners of your project area
3. Click coordinates to copy them
4. Format as: `[latitude, longitude]`

## Example Coordinates

### Nairobi CBD Area
```json
[
  [-1.2850, 36.8150],
  [-1.2850, 36.8200],
  [-1.2900, 36.8200],
  [-1.2900, 36.8150]
]
```

### Westlands Area
```json
[
  [-1.2650, 36.8050],
  [-1.2650, 36.8100],
  [-1.2700, 36.8100],
  [-1.2700, 36.8050]
]
```

## Database Fields

The system stores the following in `AttendanceLog`:

| Field | Type | Description |
|-------|------|-------------|
| `latitude` | Decimal | User's GPS latitude |
| `longitude` | Decimal | User's GPS longitude |
| `location_accuracy` | Decimal | GPS accuracy in meters |
| `location_verified` | Boolean | Whether location was validated |
| `location_verification_time` | DateTime | When validation occurred |
| `verification_method` | String | Set to "Location" |

## Error Messages

### User Outside Boundary
```
⛔ Check-in denied: You are 150 meters outside the project boundary. 
You must be at the project location to check in.
```

### GPS Unavailable
```
⛔ GPS location is required for check-in. Please enable location services.
```

### No Project Selected
```
⛔ Project selection is required
```

### Location Permission Denied
```
⛔ Unable to get location: Location permission denied. 
Please enable location access.
```

## Testing the Feature

### 1. Test with Demo File
```bash
# Open in browser
geofence-demo.html
```

### 2. Test Live
1. Start Django server: `python manage.py runserver`
2. Go to Attendance page
3. Select a project (must have boundaries defined)
4. Select a labourer
5. Click "Check In with Camera"
6. System will request location permission
7. Check-in will succeed/fail based on location

### 3. Simulate Different Scenarios

**Scenario A: Inside Boundary**
- Be physically at the project site
- Expected: Check-in succeeds ✅

**Scenario B: Outside Boundary**
- Be away from the project site
- Expected: Check-in denied with distance message ⛔

**Scenario C: No Boundary Defined**
- Create a project without boundary_coordinates
- Expected: Check-in allowed with warning ⚠️

## Security Considerations

1. **GPS Spoofing**: Current implementation uses browser GPS which can be spoofed
   - Future: Add IP-based validation
   - Future: Require multiple location checks over time

2. **HTTPS Required**: GPS only works on:
   - `localhost` or `127.0.0.1`
   - HTTPS domains
   - Not on HTTP network IPs (like 192.168.x.x)

3. **Accuracy**: GPS accuracy varies:
   - Indoor: 10-50 meters
   - Outdoor: 5-10 meters
   - Clear sky: 1-5 meters

## Configuration

### Adjust Boundary Tolerance
To allow check-in within X meters of boundary, modify `validate_geofence()` in `views.py`:

```python
def validate_geofence(latitude, longitude, project):
    # ... existing code ...
    
    if is_inside:
        return True, "Location verified", 0
    else:
        # Allow if within 50 meters of boundary
        if min_distance <= 50:
            return True, f"Within {min_distance:.0f}m of boundary - Allowed", min_distance
        else:
            return False, f"You are {min_distance:.0f} meters outside", min_distance
```

### Disable Geofencing for Specific Projects
In Project model, leave `boundary_coordinates` empty:
```python
boundary_coordinates = None  # or []
```
System will allow check-in without validation.

## API Response Examples

### Success Response
```json
{
  "success": true,
  "message": "✅ John Doe checked in successfully at Main Construction Site. Location verified: You are within the project boundary"
}
```

### Failure Response
```json
{
  "success": false,
  "error": "⛔ Check-in denied: You are 250 meters outside the project boundary. You must be at the project location to check in."
}
```

## Troubleshooting

### Location Not Working
1. Check browser permissions (chrome://settings/content/location)
2. Ensure HTTPS or localhost
3. Check console for JavaScript errors
4. Verify GPS is enabled on device

### Always Denied
1. Verify project has `boundary_coordinates` defined
2. Check coordinate format: `[[lat, lng], ...]` not `[[lng, lat], ...]`
3. Test with demo file first
4. Verify coordinates are correct (use Google Maps)

### Always Allowed
1. Check if `boundary_coordinates` is empty
2. Verify point-in-polygon logic in `views.py`
3. Add debug logging to `validate_geofence()`

## Future Enhancements

1. **Visual Boundary Editor**: Draw boundaries on map in admin
2. **Entry Points**: Define specific gates/entrances
3. **Geofence Alerts**: Notify when labourer leaves site
4. **Historical Tracking**: Store GPS trail throughout the day
5. **Multi-Project**: Allow labourers to move between project sites
6. **Offline Support**: Cache boundaries for offline validation

## Files Modified

1. `labourers/templates/labourers/attendance.html`
   - Added project selector dropdowns
   - Added `getCurrentLocation()` function
   - Updated check-in/out functions to send GPS data

2. `labourers/views.py`
   - Added `point_in_polygon()` function
   - Added `calculate_distance()` function
   - Added `validate_geofence()` function
   - Updated `check_in()` view with geofencing
   - Updated `check_out()` view with geofencing

3. `labourers/models.py` (existing fields used)
   - Project: `boundary_coordinates`, `entry_points`
   - AttendanceLog: `latitude`, `longitude`, `location_verified`

## Support

For issues or questions:
1. Check `geofence-demo.html` for visual testing
2. Review browser console for errors
3. Verify project boundaries are defined correctly
4. Test with different GPS locations

---

**Note**: Always test geofencing with actual device GPS in the field before going live. Browser simulation may differ from real-world scenarios.
