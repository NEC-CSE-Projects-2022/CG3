from setuptools import setup

# Minimal setup.py to avoid build issues
setup(
    name="water-quality-backend",
    version="0.1",
    py_modules=[],
    install_requires=[],
    python_requires='>=3.8',
)

# Note: We're using requirements.txt for dependencies instead of setup.py
# to avoid build issues with setuptools
