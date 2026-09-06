"""
WSGI entry point for Hostinger's "Setup Python App" feature (hPanel).

Hostinger's Python hosting runs on Phusion Passenger, which looks for a file
named exactly `passenger_wsgi.py` at the app's root with a WSGI-callable
named `application`. This file just exposes the existing Flask app under
that expected name — no other changes needed.

In hPanel, when you set up the Python App:
- Application root: the folder containing this file
- Application startup file: passenger_wsgi.py
- Application Entry point: application
"""
import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from file import app as application
