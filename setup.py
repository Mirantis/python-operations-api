"""Setup for model_manager package."""

from setuptools import setup

version = '1.0'

test_require = [
    'faker',
    'flake8',
    'pytest',
    'pytest-cov',
    'pytest-env',
    'pytest-flask==0.11.0',
]

setup(
    install_requires=[
        'Flask==1.0.2',
        'flask-restplus==0.12.1',
        'flask-swagger-ui',
        'flask_sqlalchemy==2.3.2',
    ],
    tests_require=[
        'flake8'],
    extras_require={
        'test': test_require,
        'dev': test_require
    },

    entry_points={
        'console_scripts': [
            'operations_api = operations_api.app:run',
        ],
    }
)
