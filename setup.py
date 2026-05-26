from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-cocoscreator",
    version="1.0.0",
    description="CLI-Anything harness for Cocos Creator 3.8.8 editor automation",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    install_requires=["click>=8.0"],
    entry_points={
        "console_scripts": [
            "cli-anything-cocoscreator=cli_anything.cocoscreator.cocoscreator_cli:cli",
        ],
    },
    package_data={"cli_anything.cocoscreator": ["skills/*.md"]},
)
