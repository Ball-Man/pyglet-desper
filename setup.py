from setuptools import setup, find_packages

REQUIREMENTS = open('requirements.txt').read().splitlines()
README = open('README.md').read()

setup(name='pyglet-desper',
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python :: 3 :: Only',
                   'Topic :: Games/Entertainment'],
      version='0.9.0',
      description='Extension package for desper and pyglet '
                  'interoperation',
      install_requires=REQUIREMENTS,
      long_description=README,
      url='https://github.com/Ball-Man/pyglet-desper',
      author='Francesco Mistri',
      author_email='franc.mistri@gmail.com',
      license='MIT',
      packages=find_packages(),
      )
