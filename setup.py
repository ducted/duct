from setuptools import setup, find_packages


setup(
    name="ducted",
    version='1.3',
    url='http://github.com/ducted/duct',
    license='MIT',
    description="A monitoring agent and event processor",
    author='Colin Alston',
    author_email='colin.alston@gmail.com',
    packages=find_packages() + [
        "twisted.plugins",
    ],
    package_data={
        'twisted.plugins': ['twisted/plugins/duct_plugin.py']
    },
    include_package_data=True,
    install_requires=[
        'zope.interface',
        'Twisted',
        'PyYaml',
        'pyOpenSSL',
        'protobuf',
        'construct<2.6',
        'pysnmp==4.2.5',
        'cryptography',
        'service_identity'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Monitoring',
    ],
)
