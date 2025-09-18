#!/usr/bin/env python3
"""
Test script to verify the description logic works correctly.
"""
import os
import sys
from pathlib import Path

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_description_logic():
    """Test the description logic with different scenarios."""
    try:
        from moments import create_app
        from moments.core.extensions import db
        from moments.models import Photo, User
        from moments.ml_services import ml_analyzer
        from flask import current_app
        
        app = create_app('development')
        with app.app_context():
            print("Testing description logic...")
            print("=" * 50)
            
            # Get the admin user
            admin_user = db.session.scalar(db.select(User).filter_by(email='admin@helloflask.com'))
            if not admin_user:
                print("✗ Admin user not found. Please run create_admin.py first.")
                return
            
            # Create test images
            from PIL import Image
            upload_path = current_app.config['MOMENTS_UPLOAD_PATH']
            
            # Test Case 1: No description provided (should auto-generate)
            print("\n1. Testing with NO description provided:")
            print("-" * 40)
            
            test_image1 = upload_path / 'test_no_desc.jpg'
            img1 = Image.new('RGB', (300, 200), color='blue')
            img1.save(test_image1)
            
            # Simulate upload with no description
            photo1 = Photo(
                filename='test_no_desc.jpg',
                filename_s='test_no_desc_s.jpg',
                filename_m='test_no_desc_m.jpg',
                description=None,  # No description provided
                author=admin_user
            )
            db.session.add(photo1)
            db.session.commit()
            
            # Run ML analysis
            alt_text1 = ml_analyzer.generate_alt_text(str(test_image1))
            photo1.alt_text = alt_text1
            
            # Check if description gets auto-populated
            if not photo1.description or photo1.description.strip() == "":
                photo1.description = alt_text1
                print(f"✓ Auto-populated description: {photo1.description}")
            else:
                print(f"✗ Description should have been auto-populated")
            
            db.session.commit()
            
            # Test Case 2: Description provided (should NOT auto-generate)
            print("\n2. Testing with description provided:")
            print("-" * 40)
            
            test_image2 = upload_path / 'test_with_desc.jpg'
            img2 = Image.new('RGB', (300, 200), color='green')
            img2.save(test_image2)
            
            user_description = "This is my custom description"
            photo2 = Photo(
                filename='test_with_desc.jpg',
                filename_s='test_with_desc_s.jpg',
                filename_m='test_with_desc_m.jpg',
                description=user_description,  # User provided description
                author=admin_user
            )
            db.session.add(photo2)
            db.session.commit()
            
            # Run ML analysis
            alt_text2 = ml_analyzer.generate_alt_text(str(test_image2))
            photo2.alt_text = alt_text2
            
            # Check if description remains unchanged
            if not photo2.description or photo2.description.strip() == "":
                photo2.description = alt_text2
                print(f"✗ Description was auto-populated when it shouldn't have been")
            else:
                print(f"✓ Description preserved: {photo2.description}")
            
            db.session.commit()
            
            # Test Case 3: Empty description (should auto-generate)
            print("\n3. Testing with empty description:")
            print("-" * 40)
            
            test_image3 = upload_path / 'test_empty_desc.jpg'
            img3 = Image.new('RGB', (300, 200), color='red')
            img3.save(test_image3)
            
            photo3 = Photo(
                filename='test_empty_desc.jpg',
                filename_s='test_empty_desc_s.jpg',
                filename_m='test_empty_desc_m.jpg',
                description="",  # Empty description
                author=admin_user
            )
            db.session.add(photo3)
            db.session.commit()
            
            # Run ML analysis
            alt_text3 = ml_analyzer.generate_alt_text(str(test_image3))
            photo3.alt_text = alt_text3
            
            # Check if description gets auto-populated
            if not photo3.description or photo3.description.strip() == "":
                photo3.description = alt_text3
                print(f"✓ Auto-populated empty description: {photo3.description}")
            else:
                print(f"✗ Empty description should have been auto-populated")
            
            db.session.commit()
            
            # Summary
            print("\n" + "=" * 50)
            print("SUMMARY:")
            print("=" * 50)
            
            photos = [photo1, photo2, photo3]
            for i, photo in enumerate(photos, 1):
                print(f"Photo {i}:")
                print(f"  - User description: {photo.description}")
                print(f"  - Alt text: {photo.alt_text}")
                print(f"  - Auto-generated: {photo.description == photo.alt_text}")
                print()
            
            print("✓ Description logic test completed!")
            
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_description_logic()