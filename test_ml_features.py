#!/usr/bin/env python3
"""
Test script to demonstrate ML features of the enhanced Moments app.
"""
import os
import sys
from pathlib import Path

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_ml_services():
    """Test the ML services with a sample image."""
    try:
        from moments.ml_services import ml_analyzer
        
        # Create a test image path (you would need an actual image file)
        test_image_path = "/workspace/test_image.jpg"
        
        if not os.path.exists(test_image_path):
            print("No test image found. Please place a test image at /workspace/test_image.jpg")
            print("You can download a sample image from the internet for testing.")
            return
        
        print("Testing ML Services...")
        print("=" * 50)
        
        # Test alternative text generation
        print("1. Testing Alternative Text Generation:")
        alt_text = ml_analyzer.generate_alt_text(test_image_path)
        print(f"   Generated alt text: {alt_text}")
        print()
        
        # Test object detection
        print("2. Testing Object Detection:")
        objects = ml_analyzer.detect_objects(test_image_path)
        print(f"   Detected {len(objects)} objects:")
        for obj in objects:
            print(f"   - {obj['label']} (confidence: {obj['confidence']:.2f})")
        print()
        
        # Test searchable keywords
        print("3. Testing Searchable Keywords:")
        keywords = ml_analyzer.get_searchable_keywords(test_image_path)
        print(f"   Keywords: {', '.join(keywords)}")
        print()
        
        print("ML Services test completed successfully!")
        
    except Exception as e:
        print(f"Error testing ML services: {e}")
        print("Make sure all dependencies are installed and models can be downloaded.")

def test_database_schema():
    """Test the database schema changes."""
    try:
        from moments import create_app
        from moments.core.extensions import db
        from moments.models import Photo
        
        app = create_app('development')
        with app.app_context():
            # Check if new columns exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('photo')]
            
            print("Database Schema Test:")
            print("=" * 50)
            print(f"Photo table columns: {columns}")
            
            if 'alt_text' in columns and 'detected_objects' in columns:
                print("✓ New ML columns found in database")
            else:
                print("✗ ML columns missing from database")
                
    except Exception as e:
        print(f"Error testing database: {e}")

if __name__ == '__main__':
    print("Moments ML Features Test")
    print("=" * 50)
    print()
    
    test_database_schema()
    print()
    test_ml_services()