# setup.py
from setuptools import setup, find_packages

setup(
    name="cloudops-buddy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Gemini (new SDK)
        "google-genai>=1.0.0",
        # Groq
        "groq>=0.9.0",
        # OpenAI (and compatible local endpoints)
        "openai>=1.0.0",
        # Configuration & CLI
        "python-dotenv>=1.0.0",
        "click>=8.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "rich>=13.0.0",
        # Testing (optional)
        "pytest>=7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cloudops-buddy = src.cli.main:main",
        ],
    },
)