# test_gdal_final.py
import os
import sys

print("=" * 60)
print("FINAL GDAL TEST - Using EXACT path")
print("=" * 60)

# Set the EXACT path
conda_prefix = r"C:\Users\User\miniconda3\envs\labour-gis"
gdal_path = r"C:\Users\User\miniconda3\envs\labour-gis\Library\bin\gdal.dll"
geos_path = r"C:\Users\User\miniconda3\envs\labour-gis\Library\bin\geos_c.dll"

print(f"GDAL path: {gdal_path}")
print(f"GEOS path: {geos_path}")
print(f"Files exist: {os.path.exists(gdal_path)}")

# Set environment variables
os.environ['GDAL_LIBRARY_PATH'] = gdal_path
os.environ['GEOS_LIBRARY_PATH'] = geos_path

# Add bin directory to PATH
bin_dir = r"C:\Users\User\miniconda3\envs\labour-gis\Library\bin"
os.environ['PATH'] = bin_dir + ';' + os.environ['PATH']

print("\nTrying to import Django GIS...")

try:
    # Configure Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labourer_admin.settings')
    
    import django
    django.setup()
    
    print("✅ Django setup successful!")
    
    # Try to import GDAL
    from django.contrib.gis.geos import Point
    print("✅ GDAL import successful!")
    
    # Create a point
    p = Point(36.8219, -1.2921)  # Nairobi
    print(f"✅ Created point: {p}")
    print(f"   Longitude: {p.x}")
    print(f"   Latitude: {p.y}")
    
    print("\n" + "=" * 60)
    print("🎉 SUCCESS! GDAL IS WORKING!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING:")
    print("1. Check if Django can find the files")
    print("2. Try loading DLL directly...")
    
    try:
        import ctypes
        ctypes.CDLL(gdal_path)
        print("✅ Can load GDAL DLL directly")
    except Exception as e2:
        print(f"❌ Cannot load DLL: {e2}")
    
    print("=" * 60)