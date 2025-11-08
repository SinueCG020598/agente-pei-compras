"""
Setup configuration for pei-compras-ai package.
Allows editable installation with: pip install -e .
"""
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pei-compras-ai",
    version="0.1.0",
    author="PEI Team",
    author_email="dev@pei.com",
    description="Sistema inteligente de automatización de compras con agentes AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pei/pei-compras-ai",
    packages=find_packages(include=["src", "src.*", "config", "config.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "openai>=1.10.0",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.5",
        "langgraph>=0.0.20",
        "sqlalchemy>=2.0.23",
        "alembic>=1.13.0",
        "requests>=2.31.0",
        "aiohttp>=3.9.1",
        "aiofiles>=23.2.1",
        "python-multipart>=0.0.6",
        "email-validator>=2.1.0",
        "streamlit>=1.29.0",
        "pillow>=10.1.0",
        "jinja2>=3.1.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.12.0",
            "ruff>=0.1.8",
            "mypy>=1.7.1",
            "pre-commit>=3.6.0",
            "httpx>=0.25.2",
        ]
    },
)
