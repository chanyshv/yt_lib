import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yt_lib",
    version="0.0.1",
    author="hairygeek",
    author_email="hairygeek@yandex.com",
    description="Young YouTube library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hairygeek/yt_lib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
