#!/usr/bin/env python3
"""
Test web upload functionality.
"""
import os
import sys
from pathlib import Path
from io import BytesIO
from PIL import Image

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_web_upload():
    """Test web upload functionality."""
    try:
        from moments import create_app
        from moments.core.extensions import db
        from moments.models import User, Photo
        from flask import current_app
        
        app = create_app('development')
        with app.app_context():
            print("Testing web upload functionality...")
            print("=" * 50)
            
            # Get admin user
            admin_user = db.session.scalar(db.select(User).filter_by(email='admin@helloflask.com'))
            if not admin_user:
                print("❌ Admin user not found. Please run create_admin.py first.")
                return
            
            print(f"✓ Using admin user: {admin_user.username}")
            
            # Test the upload route with authentication
            with app.test_client() as client:
                # Create a test image
                img = Image.new('RGB', (100, 100), color='red')
                img_io = BytesIO()
                img.save(img_io, format='JPEG')
                img_io.seek(0)
                
                # Test POST upload directly (bypassing login for now)
                with client.session_transaction() as sess:
                    # Simulate being logged in
                    sess['_user_id'] = str(admin_user.id)
                    sess['_fresh'] = True
                
                upload_response = client.post('/upload', data={
                    'file': (img_io, 'test_web_upload.jpg'),
                    'description': 'Test web upload description'
                }, content_type='multipart/form-data')
                
                print(f"Upload response status: {upload_response.status_code}")
                
                if upload_response.status_code == 200:
                    print("✓ Upload successful!")
                    
                    # Check if photo was created
                    photos_count = db.session.scalar(db.select(db.func.count(Photo.id)))
                    print(f"Total photos in database: {photos_count}")
                    
                    # Check the latest photo
                    latest_photo = db.session.scalar(
                        db.select(Photo).order_by(Photo.id.desc())
                    )
                    if latest_photo:
                        print(f"Latest photo ID: {latest_photo.id}")
                        print(f"Latest photo description: {latest_photo.description}")
                        print(f"Latest photo alt_text: {latest_photo.alt_text}")
                        print(f"Latest photo filename: {latest_photo.filename}")
                else:
                    print(f"❌ Upload failed: {upload_response.status_code}")
                    print(f"Response: {upload_response.data.decode()}")
                    
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_web_upload()