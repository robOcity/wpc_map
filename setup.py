from distutils.core import setup


setup(
    name='wx_map',
    version='0.5',
    packages=['wx_map'],
    url='https://github.com/robOcity/wx_map',
    license='MIT',
    author='Robert Osterburg',
    author_email='robert.osterburg@gmail.com',
    description=('Downloads archived weather maps from the',
                 'Weather Prediction Center (WPC).'),
    keywords=['weather', 'map', 'surface'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering :: Atmospheric Science'],
    long_description="""\
Downloads archived weather maps from the Weather Prediction Center (WPC).

Surface weather maps for North America and the Continental United States are
available from May 1, 2005 onward.  Eight different kinds of maps are available at eight different times each day.
This program will allow you to download one type of map for a range of dates, and store the maps in a folder. 
"""
)
