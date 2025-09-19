#!/usr/bin/env python3
"""
Test script to simulate the upload process and check ML integration.
"""
import os
import sys
from pathlib import Path

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_upload_simulation():
    """Simulate the upload process step by step."""
    try:
        from moments import create_app
        from moments.core.extensions import db
        from moments.models import Photo, User, Role
        from moments.ml_services import ml_analyzer
        from flask import current_app
        
        app = create_app('development')
        with app.app_context():
            print("Testing upload simulation...")
            print("=" * 50)
            
            # Check if upload directory exists
            upload_path = current_app.config['MOMENTS_UPLOAD_PATH']
            print(f"Upload path: {upload_path}")
            print(f"Upload path exists: {upload_path.exists()}")
            
            if not upload_path.exists():
                upload_path.mkdir(parents=True, exist_ok=True)
                print("Created upload directory")
            
            # Create a test image
            from PIL import Image
            test_image_path = upload_path / 'test_upload_simulation.jpg'
            img = Image.new('RGB', (300, 200), color='blue')
            img.save(test_image_path)
            print(f"Created test image: {test_image_path}")
            
            # Test ML processing directly
            print("\nTesting ML processing...")
            try:
                alt_text = ml_analyzer.generate_alt_text(str(test_image_path))
                print(f"✓ Alt text generated: {alt_text}")
                
                detected_objects = ml_analyzer.detect_objects(str(test_image_path))
                print(f"✓ Objects detected: {len(detected_objects)}")
                
                # Test the Photo model methods
                photo = Photo(
                    filename='test_upload_simulation.jpg',
                    filename_s='test_upload_simulation_s.jpg',
                    filename_m='test_upload_simulation_m.jpg',
                    author_id=1  # We'll use a dummy author_id
                )
                
                photo.alt_text = alt_text
                photo.set_detected_objects(detected_objects)
                
                print(f"✓ Photo alt_text set: {photo.alt_text}")
                print(f"✓ Photo detected_objects set: {photo.detected_objects}")
                
                # Test the helper methods
                keywords = photo.get_searchable_keywords()
                print(f"✓ Searchable keywords: {keywords}")
                
            except Exception as e:
                print(f"✗ ML processing failed: {e}")
                import traceback
                traceback.print_exc()
            
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_upload_simulation()