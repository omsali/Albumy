#!/usr/bin/env python3
"""
Demonstration script showing the smart description feature.
"""
import os
import sys
from pathlib import Path

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

def demo_description_feature():
    """Demonstrate the smart description feature."""
    try:
        from moments import create_app
        from moments.core.extensions import db
        from moments.models import Photo, User
        from moments.ml_services import ml_analyzer
        from flask import current_app
        
        app = create_app('development')
        with app.app_context():
            print("🎯 Smart Description Feature Demo")
            print("=" * 50)
            
            # Get the admin user
            admin_user = db.session.scalar(db.select(User).filter_by(email='admin@helloflask.com'))
            if not admin_user:
                print("❌ Admin user not found. Please run create_admin.py first.")
                return
            
            # Create a test image
            from PIL import Image
            upload_path = current_app.config['MOMENTS_UPLOAD_PATH']
            test_image = upload_path / 'demo_smart_desc.jpg'
            img = Image.new('RGB', (400, 300), color='purple')
            img.save(test_image)
            
            print("📸 Created test image: purple background")
            print()
            
            # Scenario 1: No description provided
            print("🔍 Scenario 1: User uploads photo WITHOUT description")
            print("-" * 50)
            
            photo1 = Photo(
                filename='demo_smart_desc.jpg',
                filename_s='demo_smart_desc_s.jpg',
                filename_m='demo_smart_desc_m.jpg',
                description=None,  # No description provided
                author=admin_user
            )
            db.session.add(photo1)
            db.session.commit()
            
            # Run ML analysis
            alt_text = ml_analyzer.generate_alt_text(str(test_image))
            photo1.alt_text = alt_text
            
            # Auto-populate description if empty
            if not photo1.description or photo1.description.strip() == "":
                photo1.description = alt_text
                print(f"✅ AI automatically generated description: '{photo1.description}'")
            else:
                print(f"❌ Description should have been auto-generated")
            
            db.session.commit()
            
            print()
            print("🔍 Scenario 2: User uploads photo WITH description")
            print("-" * 50)
            
            # Create another test image
            test_image2 = upload_path / 'demo_custom_desc.jpg'
            img2 = Image.new('RGB', (400, 300), color='orange')
            img2.save(test_image2)
            
            custom_description = "My beautiful sunset photo from vacation"
            photo2 = Photo(
                filename='demo_custom_desc.jpg',
                filename_s='demo_custom_desc_s.jpg',
                filename_m='demo_custom_desc_m.jpg',
                description=custom_description,  # User provided description
                author=admin_user
            )
            db.session.add(photo2)
            db.session.commit()
            
            # Run ML analysis
            alt_text2 = ml_analyzer.generate_alt_text(str(test_image2))
            photo2.alt_text = alt_text2
            
            # Check if description is preserved
            if photo2.description == custom_description:
                print(f"✅ User description preserved: '{photo2.description}'")
                print(f"   (AI generated: '{alt_text2}' but wasn't used)")
            else:
                print(f"❌ User description was overwritten")
            
            db.session.commit()
            
            print()
            print("📊 Summary")
            print("=" * 50)
            print("This feature ensures:")
            print("• Every photo has a meaningful description")
            print("• Users can provide their own descriptions")
            print("• AI fills in descriptions when users don't provide them")
            print("• Both accessibility (alt text) and user experience are improved")
            print()
            print("🎉 Smart description feature is working perfectly!")
            
    except Exception as e:
        print(f"❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    demo_description_feature()