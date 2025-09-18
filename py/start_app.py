#!/usr/bin/env python3
"""
Start the Flask application with proper initialization.
"""
import os
import sys
from pathlib import Path

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

def start_app():
    """Start the Flask application."""
    from moments import create_app
    from moments.core.extensions import db
    from moments.models import Role, User
    from werkzeug.security import generate_password_hash
    
    app = create_app('development')
    
    with app.app_context():
        # Initialize roles
        Role.init_role()
        print("✓ Roles initialized")
        
        # Create admin user manually to avoid the __init__ issue
        admin_user = db.session.scalar(db.select(User).filter_by(email='admin@helloflask.com'))
        if not admin_user:
            # Create user without calling __init__
            admin_user = User.__new__(User)
            admin_user.username = 'admin'
            admin_user.email = 'admin@helloflask.com'
            admin_user.name = 'Admin User'
            admin_user.password_hash = generate_password_hash('moments')
            admin_user.website = None
            admin_user.bio = None
            admin_user.location = None
            admin_user.confirmed = True
            admin_user.locked = False
            admin_user.active = True
            admin_user.public_collections = True
            admin_user.receive_comment_notification = True
            admin_user.receive_follow_notification = True
            admin_user.receive_collect_notification = True
            
            db.session.add(admin_user)
            db.session.commit()
            
            # Now set the role and generate avatar
            admin_user.set_role()
            admin_user.generate_avatar()
            db.session.commit()
            
            print("✓ Admin user created")
        else:
            print("✓ Admin user already exists")
    
    print("\nStarting Flask application...")
    print("=" * 50)
    print("The app will be available at: http://127.0.0.1:5000/")
    print("Login with: admin@helloflask.com / moments")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    start_app()