#!/usr/bin/env python3
"""
Start Flask app with simplified configuration to avoid session issues.
"""
import os
import sys
from pathlib import Path

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

def start_app():
    """Start Flask app with simplified configuration."""
    try:
        from moments import create_app
        
        # Create app with development config
        app = create_app('development')
        
        # Override some settings to avoid session issues
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DROPZONE_ENABLE_CSRF'] = False
        
        print("🚀 Starting Flask application with simplified configuration...")
        print("📍 The app will be available at: http://127.0.0.1:5000/")
        print("🔑 Login with: admin@helloflask.com / moments")
        print("📸 Upload photos and test the ML features!")
        print("⏹️  Press Ctrl+C to stop")
        print("\n" + "="*60)
        print("NOTE: CSRF protection is temporarily disabled for testing.")
        print("This allows uploads to work without session issues.")
        print("="*60 + "\n")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    start_app()