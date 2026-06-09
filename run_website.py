# -*- coding: utf-8 -*-
"""
Run this file to start the LawPal website.
Then open: http://localhost:5000
"""
import sys, os

# Make sure we run from the web folder
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "web"))
sys.path.insert(0, ".")

print("=" * 45)
print("  LawPal Web Server Starting...")
print("  Open this in your browser:")
print("  http://localhost:5000")
print("=" * 45)

from app import app
app.run(debug=False, host="127.0.0.1", port=5000, use_reloader=False, threaded=True)
