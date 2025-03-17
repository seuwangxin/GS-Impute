from setuptools import setup, find_packages

setup(
    name='GS-Impute',  
    version='1.0.0',  
    description="",  
    long_description=open('README.md').read(),  
    include_package_data=True,  
    author='jzt',  
    author_email='',  
    maintainer='jzt',  
    maintainer_email='',  
    license='MIT License',  
    url='',  
    packages=find_packages(),  
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',  
    ],
    python_requires='>=3.9',  
    install_requires=[''],  
    entry_points={
        'console_scripts': [
            'gsi = pycut.pyTest:main'],
    },
)
