import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-enum-choices",
    version="0.0.1",
    author="Vasil Slavov",
    author_email="v.slavov96@gmail.com",
    description="A custom Django field able to use subclasses of Python's internal `Enum` class as choices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/slavov-v/django-enum-choices",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
