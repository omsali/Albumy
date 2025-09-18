#!/usr/bin/env python3
"""
Test upload without description (should auto-populate).
"""
import os
import sys
from pathlib import Path
from io import BytesIO
from PIL import Image

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_upload_no_description():
    """Test upload without description (should auto-populate)."""
    try:
        from moments import create_app
        from moments.core.extensions import db
        from moments.models import User, Photo
        from flask import current_app
        
        app = create_app('development')
        with app.app_context():
            print("Testing upload WITHOUT description (auto-population)...")
            print("=" * 60)
            
            # Get admin user
            admin_user = db.session.scalar(db.select(User).filter_by(email='admin@helloflask.com'))
            if not admin_user:
                print("❌ Admin user not found. Please run create_admin.py first.")
                return
            
            print(f"✓ Using admin user: {admin_user.username}")
            
            # Test the upload route with authentication and CSRF
            with app.test_client() as client:
                # First, get the upload page to get CSRF token
                with client.session_transaction() as sess:
                    # Simulate being logged in
                    sess['_user_id'] = str(admin_user.id)
                    sess['_fresh'] = True
                
                # Get the upload page to extract CSRF token
                upload_page_response = client.get('/upload')
                csrf_token = None
                if upload_page_response.status_code == 200:
                    page_content = upload_page_response.data.decode()
                    import re
                    csrf_match = re.search(r'const csrfToken = "([^"]+)"', page_content)
                    if csrf_match:
                        csrf_token = csrf_match.group(1)
                        print(f"✓ Found CSRF token")
                
                if not csrf_token:
                    print("❌ Could not get CSRF token")
                    return
                
                # Create a test image
                img = Image.new('RGB', (200, 150), color='purple')
                img_io = BytesIO()
                img.save(img_io, format='JPEG')
                img_io.seek(0)
                
                # Test POST upload WITHOUT description (should auto-populate)
                upload_response = client.post('/upload', data={
                    'file': (img_io, 'test_no_desc_upload.jpg'),
                    'csrf_token': csrf_token
                    # No description provided
                }, content_type='multipart/form-data')
                
                print(f"Upload response status: {upload_response.status_code}")
                
                if upload_response.status_code == 200:
                    print("✅ Upload successful!")
                    
                    # Check the latest photo
                    latest_photo = db.session.scalar(
                        db.select(Photo).order_by(Photo.id.desc())
                    )
                    if latest_photo:
                        print(f"Latest photo ID: {latest_photo.id}")
                        print(f"Latest photo description: {latest_photo.description}")
                        print(f"Latest photo alt_text: {latest_photo.alt_text}")
                        print(f"Latest photo filename: {latest_photo.filename}")
                        
                        # Check if description was auto-populated
                        if latest_photo.description and latest_photo.description == latest_photo.alt_text:
                            print("✅ SUCCESS: Description was auto-populated with alt text!")
                        elif latest_photo.description:
                            print(f"⚠️  Description exists but doesn't match alt text: {latest_photo.description}")
                        else:
                            print("❌ Description was not auto-populated")
                else:
                    print(f"❌ Upload failed: {upload_response.status_code}")
                    print(f"Response: {upload_response.data.decode()[:500]}...")
                    
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_upload_no_description()