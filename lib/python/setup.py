import setuptools

setuptools.setup(
    name="aw2-api-backend",
    version="0.0.1",
    author="Ethan Hollins",
    author_email="ethanjohol@gmail.com",
    description="Shared Python library for Lambdas.",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "attrs",
        "cattrs",
        "jsonschema",
        "pytest",
        "requests",
        "Werkzeug",
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)
