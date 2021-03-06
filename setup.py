from setuptools import setup

setup(name='olm',
    version='0.0.35',
    description='Static site generator',
    url='https://github.com/rhyst/olm',
    author='Rhys Tyers',
    author_email='',
    license='MIT',
    packages=['olm'],
    zip_safe=False,
    entry_points = {
        'console_scripts': ['olm=olm:main'],
    },
    install_requires=[
        'astroid==1.6.1',
        'blinker==1.4',
        'chardet==3.0.4',
        'coloredlogs==9.0',
        'humanfriendly==4.8',
        'isort==4.2.15',
        'Jinja2==2.10',
        'jsmin==2.2.2',
        'lazy-object-proxy==1.3.1',
        'libsass==0.13.7',
        'MarkupSafe==1.0',
        'mccabe==0.6.1',
        'mistune==0.8.3',
        'pylint==1.8.2',
        'six==1.11.0',
        'verboselogs==1.7',
        'wrapt==1.10.11'
    ]

)
