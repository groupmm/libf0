from setuptools import setup, find_packages


with open('README.md', 'r') as fdesc:
    long_description = fdesc.read()

setup(
    name='libf0',
    version='1.0.0',
    description='Python Package for F0-Estimation',
    author='Sebastian Rosenzweig and Meinard Müller',
    author_email='sebastian.rosenzweig@audiolabs-erlangen.de',
    url='',
    download_url='',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Programming Language :: Python :: 3",
    ],
    keywords=['audio', 'music', 'f0', 'pitch'],
    license='MIT',
    install_requires=['ipython >= 7.8.0, < 8.0.0',
                      'librosa >= 0.8.0, < 1.0.0',
                      'matplotlib >= 3.1.0, < 4.0.0',
                      'numba >= 0.51.0, < 1.0.0',
                      'numpy >= 1.17.0, < 2.0.0',
                      'pysoundfile >= 0.9.0, < 1.0.0',
                      'scipy >= 1.3.0, < 2.0.0'],
    python_requires='>=3.6',
    extras_require={
        'dev': ['jupyter == 1.0.*',
                'nbstripout == 0.4.*'],
        'tests': ['pytest == 6.2.*'],
        'docs': ['sphinx == 4.0.*',
                 'sphinx-rtd-theme == 0.5.*'],
    }
)
