from jinja2 import Template
from os import path
import os
import pathlib
from typing import List
import re
import json


def getTemplate(contributors: List[dict]) -> str:
    if path.exists(".github/contributor_list_template.md"):
        file_path = pathlib.Path(".github/contributor_list_template.md").absolute()
    else:
        file_path = (
            pathlib.Path(__file__).parent.absolute().joinpath("default_template.md")
        )

    with open(file_path) as template_file:
        template = Template(template_file.read())

    header_level = "##"
    header_level_var = os.getenv("INPUT_HEADER_LEVEL")
    if header_level_var is not None:
        try:
            level_count = int(header_level_var)
            level = ""
            for i in range(level_count):
                level += "#"
        except ValueError:
            print(
                f"Failed to convert {header_level_var} to int. Falling back on {level}."
            )

    return template.render({"contributors": contributors, "header_level": header_level})


def writeToReadme(rendered: str) -> None:
    with open("README.md") as _readme:
        readme = _readme.read()

    if not "<!-- DO NOT REMOVE - contributor_list:start -->" in readme:
        print("Contributor list not found - creating it now! 🎉")
        with open("README.md", "a") as readme:
            readme.write(
                "\n<!-- prettier-ignore-start -->\n<!-- DO NOT REMOVE - contributor_list:start -->\n"
                + rendered
                + "\n<!-- DO NOT REMOVE - contributor_list:end -->\n<!-- prettier-ignore-end -->"
            )
    else:
        readme = re.sub(
            "(?<=<!-- DO NOT REMOVE - contributor_list:start -->\n).+?(?=\n<!-- DO NOT REMOVE - contributor_list:end -->)",
            rendered,
            readme,
            flags=re.DOTALL,
        )
        with open("README.md", "w") as _readme:
            _readme.write(readme)


def commit(commit_name: str) -> None:
    os.system('git config --global user.email "action@github.com"')
    os.system('git config --global user.name "Publishing Bot"')
    os.system("git add .")
    os.system(f'git commit -m "{commit_name}"')
    os.system("git push")


def getStoredContributors() -> list:
    with open("README.md") as _readme:
        readme = _readme.read()
    match = re.search(
        "<!-- DO NOT REMOVE - contributor_list:data:start:(.+):end -->", readme
    )
    if match is None:
        return None
    parsed = json.loads(match.group(1))

    return parsed


def setStoredContributors(contributors):
    with open("README.md") as _readme:
        readme = _readme.read()
    match = re.search(
        "<!-- DO NOT REMOVE - contributor_list:data:start:(.+):end -->", readme
    )
    if match is None:
        readme = f"<!-- DO NOT REMOVE - contributor_list:data:start:{json.dumps(contributors)}:end -->\n{readme}"
    else:
        readme = re.sub(
            "(?<=<!-- DO NOT REMOVE - contributor_list:data:start:).+(?=:end -->)",
            json.dumps(contributors),
            readme,
        )

    with open("README.md", "w") as _readme:
        _readme.write(readme)
