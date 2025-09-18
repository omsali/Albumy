#!/usr/bin/env python3
"""
Test CSRF token functionality.
"""
import os
import sys
from pathlib import Path
from io import BytesIO
from PIL import Image

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_csrf_fix():
    """Test CSRF token functionality."""
    try:
        from moments import create_app
        from moments.core.extensions import db
        from moments.models import User, Photo
        from flask import current_app
        
        app = create_app('development')
        with app.app_context():
            print("Testing CSRF token functionality...")
            print("=" * 50)
            
            # Get admin user
            admin_user = db.session.scalar(db.select(User).filter_by(email='admin@helloflask.com'))
            if not admin_user:
                print("❌ Admin user not found. Please run create_admin.py first.")
                return
            
            print(f"✓ Using admin user: {admin_user.username}")
            
            # Test the upload route with proper session handling
            with app.test_client() as client:
                # First, login properly
                login_response = client.post('/auth/login', data={
                    'email': 'admin@helloflask.com',
                    'password': 'moments',
                    'csrf_token': ''  # Will be filled by the form
                }, follow_redirects=True)
                
                print(f"Login response status: {login_response.status_code}")
                
                if login_response.status_code == 200:
                    print("✅ Login successful!")
                    
                    # Get the upload page to extract CSRF token
                    upload_page_response = client.get('/upload')
                    print(f"Upload page status: {upload_page_response.status_code}")
                    
                    if upload_page_response.status_code == 200:
                        print("✅ Upload page accessible!")
                        
                        # Extract CSRF token from the page
                        page_content = upload_page_response.data.decode()
                        import re
                        csrf_match = re.search(r'const csrfToken = "([^"]+)"', page_content)
                        if csrf_match:
                            csrf_token = csrf_match.group(1)
                            print(f"✅ Found CSRF token: {csrf_token[:20]}...")
                            
                            # Test upload with proper CSRF token
                            img = Image.new('RGB', (100, 100), color='green')
                            img_io = BytesIO()
                            img.save(img_io, format='JPEG')
                            img_io.seek(0)
                            
                            upload_response = client.post('/upload', data={
                                'file': (img_io, 'test_csrf_fix.jpg'),
                                'description': 'Test CSRF fix',
                                'csrf_token': csrf_token
                            }, content_type='multipart/form-data')
                            
                            print(f"Upload response status: {upload_response.status_code}")
                            
                            if upload_response.status_code == 200:
                                print("✅ Upload successful with CSRF token!")
                                
                                # Check if photo was created
                                latest_photo = db.session.scalar(
                                    db.select(Photo).order_by(Photo.id.desc())
                                )
                                if latest_photo:
                                    print(f"✅ Photo created: ID {latest_photo.id}, Description: {latest_photo.description}")
                            else:
                                print(f"❌ Upload failed: {upload_response.status_code}")
                                print(f"Response: {upload_response.data.decode()[:500]}...")
                        else:
                            print("❌ Could not find CSRF token in page")
                    else:
                        print(f"❌ Upload page failed: {upload_page_response.status_code}")
                        print(f"Response: {upload_page_response.data.decode()[:500]}...")
                else:
                    print(f"❌ Login failed: {login_response.status_code}")
                    print(f"Response: {login_response.data.decode()[:500]}...")
                    
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_csrf_fix()