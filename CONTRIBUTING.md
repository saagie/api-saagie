## Contributing

All contributions are made with the pull-request system. In order to contribute, please follow the following steps:

- Create an issue with the correct label (i.e. Documentation/Bug/Feature)
- Create a new branch starting with the issue type : `feat/...`, `fix/...` or `doc/...`. GitHub Action (CI) will be
  triggered on each push on your branch. Warning, after the first push on your branch, an automatic commit/push will be
  made by the CI in order to increment the version. Thus, remember to update your repository after your first commit.
- Implement your change
- Open a Pull Request (don't forget to link the PR to the issue)
- PR will be reviewed by the Professional Service Team and merged if all the checks are successful

### Code conventions

We're using different tools to ensure good code quality and consistency.

- [Black](https://black.readthedocs.io/en/stable/): linter for Python. We're using a 120 character max line length (
  configured in `pyproject.toml`).
- [isort](https://pycqa.github.io/isort/): optimize import orders  (configured in `pyproject.toml`).
- [pylint](https://pylint.pycqa.org/en/latest/) for code quality checks. Our CI will reject any errors
  or code with an overall score under 8.  (configured in `pyproject.toml`).

If you want to automaticly run the linters and the code quality checks, you can use the following command to add this
ckecks as a pre-commit hook:

```
poetry run pre-commit install
```

### Commits Guidelines

We're using the [Python Semantic Release library](https://python-semantic-release.readthedocs.io/en/latest/) to manage
our versioning.

In order to work properly, you need to follow
the  [Emoji Parser commit style](https://python-semantic-release.readthedocs.io/en/latest/configuration.html#major-emoji)
when squashing the commits during the merge of the PR to master.

- Messages with :ambulance:, :lock:, :bug:, :zap:, :goal_net:, :alien:, :wheelchair:, :speech_balloon:, :mag:, :apple:
  , :penguin:, :checkered_flag:, :robot:, :green_apple: emojis in the commit will make the release process to bump the
  patch version
- Messages with :sparkles:, :children_crossing:, :lipstick:, :iphone:, :egg:, :chart_with_upwards_trend: emojis in the
  commit will make the release process to bump the minor version
- Messages with a :boom: emoji in the commit will make the release process to bump the major version
