"""
Script to add sample project boundaries for testing geofencing.
Run this after creating projects in the admin panel.

Usage:
    python manage.py shell < add_sample_boundaries.py
"""

from labourers.models import Project

# Sample boundaries for different areas in Nairobi
SAMPLE_BOUNDARIES = {
    'Nairobi CBD': [
        [-1.2850, 36.8150],
        [-1.2850, 36.8200],
        [-1.2900, 36.8200],
        [-1.2900, 36.8150],
        [-1.2850, 36.8150]
    ],
    'Westlands': [
        [-1.2650, 36.8050],
        [-1.2650, 36.8100],
        [-1.2700, 36.8100],
        [-1.2700, 36.8050],
        [-1.2650, 36.8050]
    ],
    'Kilimani': [
        [-1.2920, 36.7820],
        [-1.2920, 36.7870],
        [-1.2970, 36.7870],
        [-1.2970, 36.7820],
        [-1.2920, 36.7820]
    ],
    'Karen': [
        [-1.3200, 36.7050],
        [-1.3200, 36.7100],
        [-1.3250, 36.7100],
        [-1.3250, 36.7050],
        [-1.3200, 36.7050]
    ],
    'Thika Road': [
        [-1.2300, 36.8950],
        [-1.2300, 36.9000],
        [-1.2350, 36.9000],
        [-1.2350, 36.8950],
        [-1.2300, 36.8950]
    ]
}

def add_boundaries_to_projects():
    """Add sample boundaries to existing projects."""
    projects = Project.objects.all()
    
    if not projects.exists():
        print("❌ No projects found. Please create projects first in the admin panel.")
        print("   Then run this script again.")
        return
    
    print(f"Found {projects.count()} project(s):")
    print("-" * 50)
    
    for i, project in enumerate(projects, 1):
        print(f"\n{i}. Project: {project.name}")
        print(f"   Location: {project.location}")
        print(f"   Current Boundary: {project.boundary_coordinates}")
        
        # Try to match project location to sample boundaries
        matched = False
        for area_name, boundary in SAMPLE_BOUNDARIES.items():
            if area_name.lower() in project.location.lower() or area_name.lower() in project.name.lower():
                project.boundary_coordinates = boundary
                project.save()
                print(f"   ✅ Added {area_name} boundary to project")
                matched = True
                break
        
        if not matched:
            # Assign default boundary (Nairobi CBD)
            project.boundary_coordinates = SAMPLE_BOUNDARIES['Nairobi CBD']
            project.save()
            print(f"   ⚠️  No match found. Added default Nairobi CBD boundary")
    
    print("\n" + "=" * 50)
    print("✅ Boundaries added successfully!")
    print("\nNext steps:")
    print("1. Open geofence-demo.html to test the boundaries")
    print("2. Go to Attendance page to test check-in")
    print("3. Or manually adjust boundaries in Admin Panel")
    print("\nAvailable sample areas:")
    for area in SAMPLE_BOUNDARIES.keys():
        print(f"   - {area}")

def show_project_boundaries():
    """Display current boundaries for all projects."""
    projects = Project.objects.all()
    
    if not projects.exists():
        print("❌ No projects found.")
        return
    
    print("\n" + "=" * 50)
    print("CURRENT PROJECT BOUNDARIES")
    print("=" * 50)
    
    for project in projects:
        print(f"\nProject: {project.name}")
        print(f"Location: {project.location}")
        if project.boundary_coordinates:
            print(f"Boundary Points: {len(project.boundary_coordinates)}")
            print("Coordinates:")
            for point in project.boundary_coordinates:
                print(f"   {point}")
        else:
            print("❌ No boundary defined")
        
        if project.entry_points:
            print(f"Entry Points: {len(project.entry_points)}")
        else:
            print("No entry points defined")
        print("-" * 50)

def create_custom_boundary(project_id, coordinates):
    """Add custom boundary to a specific project."""
    try:
        project = Project.objects.get(id=project_id)
        project.boundary_coordinates = coordinates
        project.save()
        print(f"✅ Custom boundary added to {project.name}")
    except Project.DoesNotExist:
        print(f"❌ Project with ID {project_id} not found")

# Main execution
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("GEOFENCING BOUNDARY SETUP")
    print("=" * 50)
    
    choice = input("\nWhat would you like to do?\n1. Add sample boundaries\n2. View current boundaries\n3. Exit\n\nChoice (1-3): ")
    
    if choice == '1':
        add_boundaries_to_projects()
    elif choice == '2':
        show_project_boundaries()
    else:
        print("Exiting...")

# For Django shell usage (non-interactive)
# Uncomment the lines below and comment out the interactive part above
# add_boundaries_to_projects()
# show_project_boundaries()
