from setuptools import setup, find_packages

setup(
    name="uefi_development",               # Name des Pakets
    version="0.1.3",                      # Version
    author="hexzhen3x7",
    author_email="hexzhen3x7@blackzspace.de",
    description="This module is for easily creating a uefi sdk development enviroment!",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/alientools-org/uefi-development",  # Optional: GitHub URL
    packages=find_packages(where="."),   # Alle Pakete im aktuellen Verzeichnis
    python_requires=">=3.6",
    install_requires=[                    # Abhängigkeiten, z.B. ["requests>=2.0"]
        "requests",
        "tqdm"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",      # Lizenz anpassen
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
             "uefi_development=uefi_development.main:main",  # Falls CLI-Tool
        ],
    },
)
