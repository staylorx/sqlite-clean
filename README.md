# SQLite Clean

A SQLite data validation and cleanup tool.

SQLite is an incredibly flexible tool that has great utility in many circumstances. This flexibility sometimes comes at the cost of later data performance or surprise challenges which can sometimes otherwise be avoided or fixed with checks. `sqlite-clean` is intended to be used for these checks and enable cleanup steps where possible.

Database changes from this tool are intended to be the choice and responsibility of the user. To this effect, `sqlite-clean` provides both "linting" (detection and alerts of possible issues) and "fixes" (actual changes to the database) as separate utilities within the same tool. By default, "linting" actions are taken unless otherwise specifying flags associated with "fixes".

## Example Usecases

- Checking that database column affinity type matches data type.
- Checking for null-like strings in nullable columns ("null" vs NULL)
- ... and more!

## Installation

Use pip to install this package along with optional version tags as desired.

```shell
pip install sqlite-clean
```

## Development

Installation: Please use Python [`poetry`](https://python-poetry.org/) to run and install this tool for development.

Development is assisted by procedures using [Dagger](https://dagger.io) via the `project.cue` file within this repo. These are also related to checks which are performed related to CI/CD. See the following page for more information on installing Dagger: <https://docs.dagger.io/install>

Afterwards, use the following commands within the project directory to perform various checks. Warnings or errors should show the related file and relevant text from the related tool which may need to be addressed.

```shell
# clean various files using formatting standards
dagger do clean
# lint the files for formatting or other issues
dagger do lint
# perform testing on the files
dagger do test
...
```

## Special Thanks

Special thanks goes to the [Way Lab](https://www.waysciencelab.com/) and [Cytomining](https://github.com/cytomining) development community, which helped inspire the work found within this repo.
