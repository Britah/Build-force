# Geofencing System Flow

## Complete Check-In Flow with Geofencing

```
┌─────────────────────────────────────────────────────────────────┐
│                    ATTENDANCE CHECK-IN FLOW                      │
└─────────────────────────────────────────────────────────────────┘

STEP 1: Supervisor Opens Attendance Page
┌──────────────────────────────────┐
│  Attendance Page Loads           │
│  - All Projects Listed           │
│  - All Labourers Listed          │
└──────────────────────────────────┘
                ↓

STEP 2: Select Project & Labourer
┌──────────────────────────────────┐
│  Supervisor Selects:             │
│  ✓ Project: "Main Site"          │
│  ✓ Labourer: "John Doe"          │
│  ✓ Clicks: "Check In"            │
└──────────────────────────────────┘
                ↓

STEP 3: Camera Opens (Photo Verification)
┌──────────────────────────────────┐
│  Camera Modal Opens              │
│  - Shows labourer's stored photo │
│  - Captures live photo           │
│  - Supervisor confirms match     │
└──────────────────────────────────┘
                ↓

STEP 4: GPS Location Capture (AUTOMATIC)
┌──────────────────────────────────┐
│  JavaScript:                     │
│  navigator.geolocation           │
│    .getCurrentPosition()         │
│                                  │
│  Captures:                       │
│  - Latitude: -1.2875            │
│  - Longitude: 36.8175           │
│  - Accuracy: 10 meters          │
└──────────────────────────────────┘
                ↓

STEP 5: Send to Backend
┌──────────────────────────────────┐
│  POST /check-in/{labourer_id}/   │
│                                  │
│  FormData:                       │
│  - project_id: 5                 │
│  - latitude: -1.2875            │
│  - longitude: 36.8175           │
│  - accuracy: 10                  │
└──────────────────────────────────┘
                ↓

STEP 6: Backend Validation
┌──────────────────────────────────┐
│  Python: validate_geofence()     │
│                                  │
│  1. Get project boundaries       │
│  2. Run point_in_polygon()       │
│  3. Check if user inside         │
│                                  │
│  Algorithm: Ray-Casting          │
│  - Draw ray from user point      │
│  - Count boundary crossings      │
│  - Odd = INSIDE, Even = OUTSIDE  │
└──────────────────────────────────┘
                ↓
        ┌───────┴───────┐
        ↓               ↓
    INSIDE          OUTSIDE
        │               │
        ↓               ↓

┌──────────────────┐   ┌──────────────────┐
│ ✅ ALLOWED       │   │ ⛔ DENIED         │
│                  │   │                  │
│ Create Record:   │   │ Return Error:    │
│ - AttendanceLog  │   │ "You are 150m    │
│ - Save GPS data  │   │  outside the     │
│ - location_      │   │  project         │
│   verified=True  │   │  boundary"       │
│                  │   │                  │
│ Return:          │   │ No record saved  │
│ "✅ Checked in   │   │                  │
│  successfully"   │   │                  │
└──────────────────┘   └──────────────────┘
        │
        ↓

STEP 7: Database Record
┌──────────────────────────────────┐
│  AttendanceLog Entry:            │
│                                  │
│  labourer: John Doe              │
│  log_type: Check-In              │
│  log_timestamp: 2024-01-15 08:30 │
│  verification_method: Location   │
│  latitude: -1.2875               │
│  longitude: 36.8175              │
│  location_accuracy: 10           │
│  location_verified: True         │
└──────────────────────────────────┘
```

## Point-in-Polygon Algorithm (Ray-Casting)

```
Visual Representation:

     Project Boundary (Polygon)
     
     P1 ────────────── P2
     │                  │
     │    User Point    │
     │       ●          │
     │                  │
     P4 ────────────── P3

Ray-Casting Process:

1. Draw horizontal ray from user point to infinity (→)
2. Count intersections with boundary edges

     P1 ────────────── P2
     │                  │
     │       ● ─────────┼──→ (1 intersection)
     │                  │
     P4 ────────────── P3

Result: 1 intersection = ODD = INSIDE ✅

Outside Example:

     P1 ────────────── P2
     │                  │
     │                  │
     │                  │
     P4 ────────────── P3
                          ● ───→ (0 intersections)

Result: 0 intersections = EVEN = OUTSIDE ⛔
```

## Distance Calculation (Haversine Formula)

```
When user is OUTSIDE boundary:
Calculate distance to nearest boundary point

User Point: (-1.3000, 36.8300)
Boundary Points:
  P1: (-1.2850, 36.8150)
  P2: (-1.2850, 36.8200)
  P3: (-1.2900, 36.8200)
  P4: (-1.2900, 36.8150)

Calculate distance to each point:
  d1 = haversine(-1.3000, 36.8300, -1.2850, 36.8150) = 1850m
  d2 = haversine(-1.3000, 36.8300, -1.2850, 36.8200) = 1720m
  d3 = haversine(-1.3000, 36.8300, -1.2900, 36.8200) = 1615m ← Minimum
  d4 = haversine(-1.3000, 36.8300, -1.2900, 36.8150) = 1745m

Result: "You are 1615 meters outside the project boundary"
```

## Data Flow Diagram

```
┌─────────────┐
│   Browser   │
│  (Frontend) │
└──────┬──────┘
       │
       │ 1. User selects project & labourer
       │
       ↓
┌─────────────┐
│ JavaScript  │
│ Geolocation │
└──────┬──────┘
       │
       │ 2. Gets GPS coordinates
       │    (lat, lng, accuracy)
       │
       ↓
┌─────────────┐
│   AJAX      │
│   Request   │
└──────┬──────┘
       │
       │ 3. POST to /check-in/
       │    with GPS data
       │
       ↓
┌─────────────┐
│   Django    │
│   View      │
└──────┬──────┘
       │
       │ 4. validate_geofence()
       │
       ↓
┌─────────────┐
│ Point-in-   │
│  Polygon    │
└──────┬──────┘
       │
       │ 5. Returns True/False
       │
       ↓
  ┌────┴────┐
  │         │
  ↓         ↓
True      False
  │         │
  │         └──→ Return error JSON
  │
  ↓
┌─────────────┐
│   Save to   │
│  Database   │
└──────┬──────┘
       │
       │ 6. Create AttendanceLog
       │
       ↓
┌─────────────┐
│   Return    │
│  Success    │
│    JSON     │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Browser   │
│   Updates   │
└─────────────┘
```

## Security Layers

```
┌─────────────────────────────────────────────────┐
│                 SECURITY LAYERS                  │
└─────────────────────────────────────────────────┘

Layer 1: Camera Verification
┌──────────────────────────────────┐
│ - Captures live photo            │
│ - Compares with stored photo     │
│ - Prevents proxy check-ins       │
└──────────────────────────────────┘
            ↓

Layer 2: GPS Location Capture
┌──────────────────────────────────┐
│ - Automatic (no manual input)    │
│ - High accuracy mode enabled     │
│ - Stores accuracy metadata       │
└──────────────────────────────────┘
            ↓

Layer 3: Geofence Validation
┌──────────────────────────────────┐
│ - Point-in-polygon algorithm     │
│ - Validates against project area │
│ - Calculates distance if outside │
└──────────────────────────────────┘
            ↓

Layer 4: Database Audit Trail
┌──────────────────────────────────┐
│ - Stores GPS coordinates         │
│ - Records validation result      │
│ - Timestamp all actions          │
│ - Immutable log entries          │
└──────────────────────────────────┘
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────┐
│              ERROR HANDLING FLOW                 │
└─────────────────────────────────────────────────┘

Get GPS Location
        ↓
    ┌───┴───┐
    │       │
  Success  Error
    │       │
    │       ├──→ Permission Denied
    │       │    "Enable location services"
    │       │
    │       ├──→ Position Unavailable
    │       │    "Location unavailable"
    │       │
    │       └──→ Timeout
    │            "Request timed out"
    │
    ↓
Validate Geofence
        ↓
    ┌───┴───┐
    │       │
  Inside  Outside
    │       │
    ✅      └──→ "You are Xm outside boundary"
    │
    ↓
Create Record
        ↓
    ┌───┴───┐
    │       │
  Success  Error
    │       │
    ✅      └──→ Database error
             "Failed to save record"
```

## Configuration Options

```
┌─────────────────────────────────────────────────┐
│           CONFIGURATION OPTIONS                  │
└─────────────────────────────────────────────────┘

Project Model:
┌────────────────────────────────────┐
│ boundary_coordinates:              │
│   - Empty/None = No validation     │
│   - List = Strict validation       │
│                                    │
│ entry_points:                      │
│   - Future: Specific gates         │
│   - Future: Multi-entry validation │
└────────────────────────────────────┘

GPS Settings (JavaScript):
┌────────────────────────────────────┐
│ enableHighAccuracy: true           │
│   - Uses GPS (not WiFi/Cell)      │
│                                    │
│ timeout: 10000 (10 seconds)        │
│   - How long to wait for GPS       │
│                                    │
│ maximumAge: 0                      │
│   - Always get fresh location      │
└────────────────────────────────────┘

Validation Settings (Python):
┌────────────────────────────────────┐
│ Modify validate_geofence():        │
│                                    │
│ - Add tolerance zone (meters)      │
│ - Require minimum accuracy         │
│ - Time-based restrictions          │
└────────────────────────────────────┘
```

---

This diagram shows the complete flow from user action to database storage,
including all validation steps, error handling, and security layers.
