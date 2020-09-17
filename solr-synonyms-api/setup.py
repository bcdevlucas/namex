from setuptools import setup

import os
## from synonyms.VERSION import __version__


def is_package(path):
    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py'))
        )


def find_packages(path, base="" ):
    """ Find all packages in path """
    packages = {}
    for item in os.listdir(path):
        dir = os.path.join(path, item)
        if is_package( dir ):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            packages[module_name] = dir
            packages.update(find_packages(dir, module_name))
    return packages


def read_requirements(filename):
    """
    Get application requirements from
    the requirements.txt file.
    :return: Python requirements
    :rtype: list
    """
    with open(filename, 'r') as req:
        requirements = req.readlines()
    install_requires = [r.strip() for r in requirements if r.find('git+') != 0]
    return install_requires


def read(filepath):
    """
    Read the contents from a file.
    :param str filepath: path to the file to be read
    :return: file contents
    :rtype: str
    """
    with open(filepath, 'r') as f:
        content = f.read()
    return content


packages = find_packages(".")
requirements = read_requirements('requirements/prod.txt')


setup(
    name='namex',
    version='0.1.1b',
    packages=packages.keys(),
    package_dir=packages,
    include_package_data=True,
    license=read('LICENSE'),
    long_description =read('README.md'),
    install_requires=[
        'Flask',
        'Flask-Migrate',
        'Flask-Script',
        'Flask-Moment',
        'Flask-SQLAlchemy',
        'Flask-RESTplus',
        'Flask-Marshmallow',
        'flask-jwt-oidc',
        'python-dotenv',
        'psycopg2-binary',
        'cx_Oracle',
        'marshmallow',
        'marshmallow-sqlalchemy',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-mock'
    ],
    classifiers=[
          'Development Status :: Beta',
          'Environment :: Console',
          'Environment :: Web API',
          'Intended Audience :: API Service Users',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache 2.0 License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Communications :: Email',
          'Topic :: Office/Business :: BC Government Registries',
          'Topic :: Software Development :: GitHub Issue Tracking',
    ],
)
