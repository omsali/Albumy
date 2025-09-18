#!/usr/bin/env python3
"""
Create admin user and test the upload process.
"""
import os
import sys
from pathlib import Path

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

def create_admin_and_test():
    """Create admin user and test upload."""
    try:
        from moments import create_app
        from moments.core.extensions import db
        from moments.models import Photo, User, Role
        from moments.ml_services import ml_analyzer
        from flask import current_app
        from werkzeug.security import generate_password_hash
        
        app = create_app('development')
        with app.app_context():
            print("Creating admin user and testing upload...")
            print("=" * 50)
            
            # Initialize roles
            Role.init_role()
            print("✓ Roles initialized")
            
            # Check if admin user exists
            admin_user = db.session.scalar(db.select(User).filter_by(email='admin@helloflask.com'))
            if not admin_user:
                # Create user using SQL directly to avoid the __init__ issue
                from sqlalchemy import text
                
                # First, get the Administrator role
                admin_role = db.session.scalar(db.select(Role).filter_by(name='Administrator'))
                
                # Insert user directly
                from datetime import datetime, timezone
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
                print("✓ Admin user created")
                
                # Get the created user
                admin_user = db.session.scalar(db.select(User).filter_by(email='admin@helloflask.com'))
            else:
                print("✓ Admin user already exists")
            
            print(f"✓ Using admin user: {admin_user.username}")
            
            # Create a test image
            from PIL import Image
            upload_path = current_app.config['MOMENTS_UPLOAD_PATH']
            test_image_path = upload_path / 'test_ml_upload.jpg'
            img = Image.new('RGB', (500, 400), color='red')
            img.save(test_image_path)
            print(f"✓ Created test image: {test_image_path}")
            
            # Test the upload process
            filename = 'test_ml_upload.jpg'
            filename_s = 'test_ml_upload_s.jpg'
            filename_m = 'test_ml_upload_m.jpg'
            
            # Create photo object
            photo = Photo(
                filename=filename,
                filename_s=filename_s,
                filename_m=filename_m,
                author=admin_user
            )
            db.session.add(photo)
            db.session.commit()
            print(f"✓ Photo created with ID: {photo.id}")
            
            # ML processing
            try:
                print("Running ML analysis...")
                image_path = current_app.config['MOMENTS_UPLOAD_PATH'] / filename
                
                # Generate alternative text
                alt_text = ml_analyzer.generate_alt_text(str(image_path))
                photo.alt_text = alt_text
                print(f"✓ Alt text generated: {alt_text}")
                
                # Detect objects
                detected_objects = ml_analyzer.detect_objects(str(image_path))
                photo.set_detected_objects(detected_objects)
                print(f"✓ Objects detected: {len(detected_objects)}")
                
                db.session.commit()
                print("✓ ML analysis completed and saved to database")
                
                # Verify the data was saved
                db.session.refresh(photo)
                print(f"✓ Final alt_text: {photo.alt_text}")
                print(f"✓ Final detected_objects: {photo.detected_objects}")
                
                # Test the helper methods
                keywords = photo.get_searchable_keywords()
                print(f"✓ Searchable keywords: {keywords}")
                
                print("\n" + "=" * 50)
                print("SUCCESS: Alt text generation is working correctly!")
                print("The ML features are properly integrated.")
                print("=" * 50)
                
            except Exception as e:
                print(f"✗ ML analysis failed: {e}")
                import traceback
                traceback.print_exc()
            
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_admin_and_test()