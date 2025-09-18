#!/usr/bin/env python3
"""
End-to-end test of the upload process with ML integration.
"""
import os
import sys
from pathlib import Path

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_upload_end_to_end():
    """Test the complete upload process."""
    try:
        from moments import create_app
        from moments.core.extensions import db
        from moments.models import Photo, User
        from moments.ml_services import ml_analyzer
        from flask import current_app
        
        app = create_app('development')
        with app.app_context():
            print("Testing end-to-end upload process...")
            print("=" * 50)
            
            # Get the admin user
            admin_user = db.session.scalar(db.select(User).filter_by(email='admin@helloflask.com'))
            if not admin_user:
                print("✗ Admin user not found. Please run start_app.py first.")
                return
            
            print(f"✓ Using admin user: {admin_user.username}")
            
            # Create a test image
            from PIL import Image
            upload_path = current_app.config['MOMENTS_UPLOAD_PATH']
            test_image_path = upload_path / 'test_end_to_end.jpg'
            img = Image.new('RGB', (400, 300), color='green')
            img.save(test_image_path)
            print(f"✓ Created test image: {test_image_path}")
            
            # Simulate the upload process exactly as in the route
            filename = 'test_end_to_end.jpg'
            filename_s = 'test_end_to_end_s.jpg'
            filename_m = 'test_end_to_end_m.jpg'
            
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
            
            # ML processing (exactly as in upload route)
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
                
            except Exception as e:
                print(f"✗ ML analysis failed: {e}")
                import traceback
                traceback.print_exc()
            
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_upload_end_to_end()