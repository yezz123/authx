import setuptools

__version__ = "0.0.7"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AuthX",
    version=__version__,
    author="Yasser Tahiri",
    author_email="yasserth19@gmail.com",
    description="Ready to use and customizable Authentications and Oauth2 management for FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Documentation": "https://yezz123.github.io/AuthX/",
        "Source Code": "https://github.com/yezz123/AuthX",
        "Bug Tracker": "https://github.com/yezz123/AuthX/issues",
    },
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP :: Session",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    python_requires=">=3.7",
    install_requires=[
        "fastapi==0.70.0",
        "PyJWT==1.7.1",
        "cryptography==35.0.0",
        "httpx==0.20.0",
        "aioredis==1.3.1",
        "passlib==1.7.4",
        "itsdangerous==1.1.0",
        "bcrypt==3.2.0",
        "email-validator==1.1.1",
        "motor==2.3.0",
        "aiosmtplib==1.1.4",
        "pydantic==1.8.2",
    ],
    extras_require={"dev": ["requests == 2.25.1", "uvicorn"]},
)
