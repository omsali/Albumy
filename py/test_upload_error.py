#!/usr/bin/env python3
"""
Test script to identify upload errors.
"""
import os
import sys
from pathlib import Path
from io import BytesIO

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_upload_error():
    """Test upload functionality to identify errors."""
    try:
        from moments import create_app
        from moments.core.extensions import db
        from moments.models import User, Role
        from flask import current_app
        from werkzeug.security import generate_password_hash
        from datetime import datetime, timezone
        from sqlalchemy import text
        
        app = create_app('development')
        with app.app_context():
            print("Testing upload functionality...")
            print("=" * 50)
            
            # Initialize roles
            Role.init_role()
            
            # Check if admin user exists
            admin_user = db.session.scalar(db.select(User).filter_by(email='admin@helloflask.com'))
            if not admin_user:
                print("Creating admin user...")
                admin_role = db.session.scalar(db.select(Role).filter_by(name='Administrator'))
                
                result = db.session.execute(text("""
                    INSERT INTO user (username, email, password_hash, name, confirmed, locked, active, 
                                    public_collections, receive_comment_notification, receive_follow_notification, 
                                    receive_collect_notification, role_id, member_since, avatar_s, avatar_m, avatar_l)
                    VALUES (:username, :email, :password_hash, :name, :confirmed, :locked, :active,
                            :public_collections, :receive_comment_notification, :receive_follow_notification,
                            :receive_collect_notification, :role_id, :member_since, :avatar_s, :avatar_m, :avatar_l)
                """), {
                    'username': 'admin',
                    'email': 'admin@helloflask.com',
                    'password_hash': generate_password_hash('moments'),
                    'name': 'Admin User',
                    'confirmed': True,
                    'locked': False,
                    'active': True,
                    'public_collections': True,
                    'receive_comment_notification': True,
                    'receive_follow_notification': True,
                    'receive_collect_notification': True,
                    'role_id': admin_role.id,
                    'member_since': datetime.now(timezone.utc),
                    'avatar_s': 'admin_s.png',
                    'avatar_m': 'admin_m.png',
                    'avatar_l': 'admin_l.png'
                })
                
                db.session.commit()
                admin_user = db.session.scalar(db.select(User).filter_by(email='admin@helloflask.com'))
                print(f"✓ Admin user created: {admin_user.username}")
            else:
                print(f"✓ Admin user exists: {admin_user.username}")
            
            # Test the upload route with authentication
            with app.test_client() as client:
                # Login first
                login_response = client.post('/auth/login', data={
                    'email': 'admin@helloflask.com',
                    'password': 'moments'
                }, follow_redirects=True)
                
                print(f"Login status: {login_response.status_code}")
                
                if login_response.status_code == 200:
                    # Test GET upload page
                    upload_get_response = client.get('/upload')
                    print(f"Upload GET status: {upload_get_response.status_code}")
                    
                    if upload_get_response.status_code != 200:
                        print(f"Upload GET error: {upload_get_response.data.decode()}")
                        return
                    
                    # Test POST upload with a dummy image
                    from PIL import Image
                    img = Image.new('RGB', (100, 100), color='red')
                    img_io = BytesIO()
                    img.save(img_io, format='JPEG')
                    img_io.seek(0)
                    
                    upload_post_response = client.post('/upload', data={
                        'file': (img_io, 'test.jpg'),
                        'description': 'Test description'
                    }, content_type='multipart/form-data')
                    
                    print(f"Upload POST status: {upload_post_response.status_code}")
                    
                    if upload_post_response.status_code != 200:
                        print(f"Upload POST error: {upload_post_response.data.decode()}")
                    else:
                        print("✓ Upload successful!")
                        
                        # Check if photo was created
                        from moments.models import Photo
                        photos = db.session.scalar(db.select(db.func.count(Photo.id)))
                        print(f"Total photos in database: {photos}")
                else:
                    print(f"Login failed: {login_response.data.decode()}")
                    
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_upload_error()