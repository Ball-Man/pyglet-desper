from setuptools import setup, find_packages

REQUIREMENTS = """
desper >= 1.1.1
pyglet >= 2.0.0, < 2.1
""".strip().splitlines()
README = open('README.md').read()

setup(name='pyglet-desper',
      classifiers=['Intended Audience :: Developers',
                   'Programming Language :: Python :: 3 :: Only',
                   'Topic :: Games/Entertainment'],
      python_requires='>=3.9',
      version='0.10.0',
      description='Extension package for desper and pyglet '
                  'interoperation',
      install_requires=REQUIREMENTS,
      long_description=README,
      long_description_content_type='text/markdown',
      url='https://github.com/Ball-Man/pyglet-desper',
      author='Francesco Mistri',
      author_email='franc.mistri@gmail.com',
      license='MIT',
      packages=find_packages(),
      )
