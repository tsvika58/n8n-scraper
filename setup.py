"""
n8n Workflow Scraper
Setup configuration for pip installation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme = Path(__file__).parent / "README.md"
long_description = readme.read_text(encoding="utf-8") if readme.exists() else ""

# Read requirements
requirements = Path(__file__).parent / "requirements.txt"
install_requires = []
if requirements.exists():
    with open(requirements) as f:
        install_requires = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#') and not line.startswith('-')
        ]

setup(
    name="n8n-scraper",
    version="1.0.0",
    author="Your Team",
    author_email="team@example.com",
    description="Comprehensive workflow scraper for n8n.io with multimodal content extraction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourteam/n8n-scraper",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11,<3.12",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "n8n-scraper=cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)




