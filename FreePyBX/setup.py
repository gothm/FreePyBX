try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='FreePyBX',
    version='0.1',
    description='A Complete PBX configurator for FreeSWITCH',
    author='Noel Morgan',
    author_email='noel@vwci.com',
    url='http://www.freepybx.org',
    install_requires=[
        "Pylons>=1.0",
        "SQLAlchemy>=0.5",
        "Genshi>=0.4",
	    "Psycopg2",
        "beautifulsoup",
        "zope.sqlalchemy",
        "pyamf"
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'freepybx': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'freepybx': [
    #        ('**.py', 'python', None),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = freepybx.config.middleware:make_app
    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
