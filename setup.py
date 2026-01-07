from setuptools import setup, find_packages


with open('README.md', 'r') as fdesc:
    long_description = fdesc.read()

setup(
    name='libf0',
    version='1.0.3',
    description='A Python Library for Fundamental Frequency Estimation in Music Recordings',
    author='Sebastian Rosenzweig, Simon Schwär, and Meinard Müller',
    author_email='meinard.mueller@audiolabs-erlangen.de',
    url='https://github.com/groupmm/libf0',
    download_url='https://github.com/groupmm/libf0',
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
    keywords=['audio', 'music', 'f0', 'pitch', 'yin', 'pyin', 'melodia', 'swipe'],
    license='MIT',
    install_requires=["numpy>=2.2",
                      "numba>=0.63",
                      "scipy>=1.15",
                      "librosa>=0.11"],
    python_requires='>=3.10',
    extras_require={
        'dev': ["jupyter>=1.1",
                "matplotlib>=3.10",
                "pysoundfile>=0.9",
                "nbstripout>=0.8"],
        'tests': ["pytest>=9.0",
                  "flake8>=7.3"],
        'docs': ["sphinx>=8.0",
                 "sphinx-rtd-theme>=3.0"],
    }
)
