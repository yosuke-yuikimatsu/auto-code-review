from setuptools import setup, find_packages

setup(
    name="auto-code-review",
    version="0.1.0",
    author="Your Name",
    description="Automatic code review library for GitHub PRs using OpenAI API",
    packages=find_packages(),
    install_requires=[
        "PyYAML",
        "requests",
        "openai",
    ],
    entry_points={
        "console_scripts": [
            "auto-code-review=auto_code_review.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)