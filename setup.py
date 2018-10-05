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
        'cryptography==2.3.1',
        'docutils==0.13.1',
        'Flask==1.0.2',
        'flask_oidc==1.4.0',
        'flask-restplus==0.12.1',
        'flask-swagger-ui',
        'flask_sqlalchemy==2.3.2',
        'ipaddress==1.0.18',
        'pygerrit>=1.0.1-dev1',
        'PyYAML==3.11',
        'SQLAlchemy-Utils==0.33.5'
    ],
    dependency_links=[
        'https://github.com/atengler/pygerrit/tarball/python3#egg=pygerrit-1.0.1-dev1'
    ],
    tests_require=[
        'flake8'
    ],
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
