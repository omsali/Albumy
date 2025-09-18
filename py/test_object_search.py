#!/usr/bin/env python3
"""
Test object search functionality.
"""
import os
import sys
from pathlib import Path
from io import BytesIO
from PIL import Image

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_object_search():
    """Test object search functionality."""
    try:
        from moments import create_app
        from moments.core.extensions import db
        from moments.models import User, Photo
        from flask import current_app
        
        app = create_app('development')
        with app.app_context():
            print("Testing object search functionality...")
            print("=" * 50)
            
            # Get admin user
            admin_user = db.session.scalar(db.select(User).filter_by(email='admin@helloflask.com'))
            if not admin_user:
                print("❌ Admin user not found. Please run create_admin.py first.")
                return
            
            print(f"✓ Using admin user: {admin_user.username}")
            
            # Test the search route
            with app.test_client() as client:
                # Test search by objects
                search_response = client.get('/search/objects?q=blue')
                print(f"Search for 'blue' status: {search_response.status_code}")
                
                if search_response.status_code == 200:
                    print("✅ Object search is working!")
                    page_content = search_response.data.decode()
                    if 'blue' in page_content.lower():
                        print("✅ Found 'blue' in search results")
                    else:
                        print("⚠️  'blue' not found in search results")
                else:
                    print(f"❌ Search failed: {search_response.status_code}")
                
                # Test search by alt text
                search_response2 = client.get('/search/objects?q=purple')
                print(f"Search for 'purple' status: {search_response2.status_code}")
                
                if search_response2.status_code == 200:
                    print("✅ Object search for 'purple' is working!")
                    page_content2 = search_response2.data.decode()
                    if 'purple' in page_content2.lower():
                        print("✅ Found 'purple' in search results")
                    else:
                        print("⚠️  'purple' not found in search results")
                else:
                    print(f"❌ Search for 'purple' failed: {search_response2.status_code}")
                
                # Test search by objects
                search_response3 = client.get('/search/objects?q=background')
                print(f"Search for 'background' status: {search_response3.status_code}")
                
                if search_response3.status_code == 200:
                    print("✅ Object search for 'background' is working!")
                    page_content3 = search_response3.data.decode()
                    if 'background' in page_content3.lower():
                        print("✅ Found 'background' in search results")
                    else:
                        print("⚠️  'background' not found in search results")
                else:
                    print(f"❌ Search for 'background' failed: {search_response3.status_code}")
                    
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_object_search()