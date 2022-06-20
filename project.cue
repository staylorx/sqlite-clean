// project cuefile for Dagger CI and other development tooling related to this project.
package main

import (
	"dagger.io/dagger"
	"universe.dagger.io/docker"
)

// python build for linting, testing, building, etc.
#PythonBuild: {
	// client filesystem
	filesystem: dagger.#FS

	// python version to use for build
	python_ver: string | *"3.9"

	// poetry version to use for build
	poetry_ver: string | *"1.1.13"

	// container image
	output: _python_build.output

	// referential build for base python image
	_python_pre_build: docker.#Build & {
		steps: [
			docker.#Pull & {
				source: "python:" + python_ver
			},
			docker.#Run & {
				command: {
					name: "mkdir"
					args: ["/workdir"]
				}
			},
			docker.#Copy & {
				contents: filesystem
				source:   "./pyproject.toml"
				dest:     "/workdir/pyproject.toml"
			},
			docker.#Copy & {
				contents: filesystem
				source:   "./poetry.lock"
				dest:     "/workdir/poetry.lock"
			},
			docker.#Run & {
				workdir: "/workdir"
				command: {
					name: "pip"
					args: ["install", "--no-cache-dir", "poetry==" + poetry_ver]
				}
			},
			docker.#Set & {
				config: {
					env: ["POETRY_VIRTUALENVS_CREATE"]: "false"
				}
			},
			docker.#Run & {
				workdir: "/workdir"
				command: {
					name: "poetry"
					args: ["install", "--no-interaction", "--no-ansi"]
				}
			},
		]
	}
	// python build with likely changes
	_python_build: docker.#Build & {
		steps: [
			docker.#Copy & {
				input:    _python_pre_build.output
				contents: filesystem
				source:   "./"
				dest:     "/workdir"
			},
		]
	}
}

// Convenience cuelang build for formatting, etc.
#CueBuild: {
	// client filesystem
	filesystem: dagger.#FS

	// output from the build
	output: _cue_build.output

	// cuelang pre-build
	_cue_pre_build: docker.#Build & {
		steps: [
			docker.#Pull & {
				source: "golang:latest"
			},
			docker.#Run & {
				command: {
					name: "mkdir"
					args: ["/workdir"]
				}
			},
			docker.#Run & {
				command: {
					name: "go"
					args: ["install", "cuelang.org/go/cmd/cue@latest"]
				}
			},
		]
	}
	// cue build for actions in this plan
	_cue_build: docker.#Build & {
		steps: [
			docker.#Copy & {
				input:    _cue_pre_build.output
				contents: filesystem
				source:   "./project.cue"
				dest:     "/workdir/project.cue"
			},
		]
	}

}

dagger.#Plan & {

	client: {
		filesystem: {
			"./": read: contents:              dagger.#FS
			"./sqlite_clean": write: contents: actions.clean.black.export.directories."/workdir/sqlite_clean"
			"./tests": write: contents:        actions.clean.black.export.directories."/workdir/tests"
			"./project.cue": write: contents:  actions.clean.cue.export.files."/workdir/project.cue"
		}
	}
	python_version: string | *"3.9"
	poetry_version: string | *"1.1.13"

	actions: {

		python_build: #PythonBuild & {
			filesystem: client.filesystem."./".read.contents
			python_ver: python_version
			poetry_ver: poetry_version
		}

		cue_build: #CueBuild & {
			filesystem: client.filesystem."./".read.contents
		}

		// applied code and/or file formatting
		clean: {
			// sort python imports with isort
			isort: docker.#Run & {
				input:   python_build.output
				workdir: "/workdir"
				command: {
					name: "poetry"
					args: ["run", "isort", "--profile", "black", "sqlite_clean/", "tests/"]
				}
			}
			// code style formatting with black
			black: docker.#Run & {
				input:   isort.output
				workdir: "/workdir"
				command: {
					name: "poetry"
					args: ["run", "black", "sqlite_clean/", "tests/"]
				}
				export: {
					directories: {
						"/workdir/sqlite_clean": _
						"/workdir/tests":        _
					}
				}
			}
			// code formatting for cuelang
			cue: docker.#Run & {
				input:   cue_build.output
				workdir: "/workdir"
				command: {
					name: "cue"
					args: ["fmt", "/workdir/project.cue"]
				}
				export: {
					files: "/workdir/project.cue": _
				}
			}
		}

		// linting to check for formatting and best practices
		lint: {

			// python versions to reference for builds
			"3.9": _
			"3.8": _
			"3.7": _

			[compat_python_version=string]: {

				build: #PythonBuild & {
					filesystem: client.filesystem."./".read.contents
					python_ver: compat_python_version
					poetry_ver: poetry_version
				}

				// mypy static type check
				mypy: docker.#Run & {
					input:   build.output
					workdir: "/workdir"
					command: {
						name: "poetry"
						args: ["run", "mypy", "--ignore-missing-imports", "sqlite_clean/"]
					}
				}
				// isort (imports) formatting check
				isort: docker.#Run & {
					input:   mypy.output
					workdir: "/workdir"
					command: {
						name: "poetry"
						args: ["run", "isort", "--profile", "black", "--check", "--diff sqlite_clean/", "tests/"]
					}
				}
				// black formatting check
				black: docker.#Run & {
					input:   isort.output
					workdir: "/workdir"
					command: {
						name: "poetry"
						args: ["run", "black", "--check", "sqlite_clean/", "tests/"]
					}
				}
				// pylint checks
				pylint: docker.#Run & {
					input:   black.output
					workdir: "/workdir"
					command: {
						name: "poetry"
						args: ["run", "pylint", "sqlite_clean/", "tests/"]
					}
				}
				// bandit security vulnerabilities check
				bandit: docker.#Run & {
					input:   pylint.output
					workdir: "/workdir"
					command: {
						name: "poetry"
						args: ["run", "bandit", "-c", "pyproject.toml", "-r", "sqlite_clean/"]
					}
				}
			}
		}
		// test
		test: {
			// python versions to reference for builds
			"3.9": _
			"3.8": _
			"3.7": _

			[compat_python_version=string]: {

				build: #PythonBuild & {
					filesystem: client.filesystem."./".read.contents
					python_ver: compat_python_version
					poetry_ver: poetry_version
				}

				// mypy static type check
				pytest: docker.#Run & {
					input:   build.output
					workdir: "/workdir"
					command: {
						name: "poetry"
						args: ["run", "pytest"]
					}
				}
			}
		}
	}
}
