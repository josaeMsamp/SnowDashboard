"""
Entry point for Streamlit application.
Streamlit Cloud uses this file to locate and run the app.
The actual app code is in Dashbord_repo/Dashboard-JS/app.py
"""
import sys
import os

# Add Dashboard-JS to path so imports work
dashboard_dir = os.path.join(os.path.dirname(__file__), 'Dashbord_repo', 'Dashboard-JS')
sys.path.insert(0, dashboard_dir)

# Now run the app - this needs to be in a conditional to avoid circular imports
if __name__ == "__main__":
    # Import and execute the dashboard app
    exec(open(os.path.join(dashboard_dir, 'app.py')).read())
