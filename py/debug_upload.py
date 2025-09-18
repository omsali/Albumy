#!/usr/bin/env python3
"""
Debug script to test the upload process and ML integration.
"""
import os
import sys
from pathlib import Path

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_upload_process():
    """Test the upload process with ML integration."""
    try:
        from moments import create_app
        from moments.core.extensions import db
        from moments.models import Photo, User, Role
        from moments.ml_services import ml_analyzer
        from flask_login import login_user
        
        app = create_app('development')
        with app.app_context():
            # Create a test user if it doesn't exist
            user = db.session.scalar(db.select(User).filter_by(email='test@example.com'))
            if not user:
                # Create roles first
                Role.init_role()
                
                user = User(
                    username='testuser',
                    email='test@example.com',
                    name='Test User'
                )
                user.password = 'testpass'
                db.session.add(user)
                db.session.commit()
            
            # Create a test image
            from PIL import Image
            test_image_path = '/tmp/test_upload.jpg'
            img = Image.new('RGB', (200, 200), color='green')
            img.save(test_image_path)
            
            print("Testing upload process...")
            print("=" * 50)
            
            # Simulate the upload process
            filename = 'test_upload.jpg'
            filename_s = 'test_upload_s.jpg'
            filename_m = 'test_upload_m.jpg'
            
            # Create photo object (like in upload route)
            photo = Photo(
                filename=filename,
                filename_s=filename_s,
                filename_m=filename_m,
                author=user
            )
            db.session.add(photo)
            db.session.commit()
            print(f"✓ Photo created with ID: {photo.id}")
            
            # Test ML processing (like in upload route)
            try:
                print("Testing ML processing...")
                
                # Generate alternative text
                alt_text = ml_analyzer.generate_alt_text(test_image_path)
                photo.alt_text = alt_text
                print(f"✓ Alt text generated: {alt_text}")
                
                # Detect objects
                detected_objects = ml_analyzer.detect_objects(test_image_path)
                photo.set_detected_objects(detected_objects)
                print(f"✓ Objects detected: {len(detected_objects)}")
                
                db.session.commit()
                print("✓ ML analysis completed and saved to database")
                
                # Verify the data was saved
                db.session.refresh(photo)
                print(f"✓ Photo alt_text in DB: {photo.alt_text}")
                print(f"✓ Photo detected_objects in DB: {photo.detected_objects}")
                
            except Exception as e:
                print(f"✗ ML processing failed: {e}")
                import traceback
                traceback.print_exc()
            
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_upload_process()