"""Setup for model_manager package."""

from setuptools import setup

version = '1.0'

setup(
    install_requires=[
        'Flask==1.0.2',
        'flask-restplus==0.12.1',
        'flask-swagger-ui',
        'flask_sqlalchemy==2.3.2',
    ],
)
