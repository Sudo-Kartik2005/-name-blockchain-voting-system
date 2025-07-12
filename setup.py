#!/usr/bin/env python3
"""
Setup script for Blockchain Voting System
This script helps set up the environment and install dependencies
"""

from setuptools import setup, find_packages

setup(
    name="blockchain-voting-system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Flask==3.1.1",
        "Flask-Login==0.6.3",
        "Flask-SQLAlchemy==3.1.1",
        "Flask-WTF==1.2.2",
        "gunicorn==21.2.0",
        "cryptography==45.0.5",
        "Werkzeug==3.1.3",
        "WTForms==3.2.1",
    ],
    python_requires=">=3.8",
) 