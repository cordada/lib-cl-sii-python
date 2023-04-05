# Contributing Guidelines

Our development workflow.


## Submitting Changes

### Development

- Check out the **main VCS branch**:

  ```sh
  git checkout develop
  ```

- Create a **new branch**:

  ```sh
  git checkout -b task/example-change
  ```

- Perform any desired changes.
- Check your changes:

  ```sh
  make lint
  ```

- Test your changes:

  ```sh
  make test
  ```

- **Commit** your changes:

  ```sh
  git commit
  ```


### Pull Request

- Push the branch to `origin`:

  ```sh
  git push origin HEAD
  ```

- Create a **pull request**:
  - *Base reference*: `develop`
  - *Head reference*: `task/example-change`
- **Assign** the pull request to the appropriate developer (usually yourself).
- Wait until the CI checks have finished and fix any failures.
- Request pull request **reviews**.
- The pull request assignee will **merge** the branch into the main branch.
- After the pull request is **merged**, verify that the CI/CD system **successfully** builds the
  base branch.


## Creating a Release

### Synchronize Local and Remote VCS Repositories

(Local workstation)

- Make sure that the main branches are synchronized with the local ones, and tests pass:

  ```sh
  make clean
  test -z "$(git status --porcelain)" && echo 'CLEAN' || echo 'DIRTY'

  git checkout master
  git pull --ff-only --rebase=false -v
  git push -v

  git checkout develop
  git pull --ff-only --rebase=false -v
  git push -v
  ```

Then wait for the CI tests (`develop` branch) to finish and verify they were successful.


### Increase Version

(Local workstation)

- Choose a new version `X.Y.Z`, where `X` is the major, `Y` is the minor, and `Z` is
  the patch version [^semver].
- Check out the **main VCS branch**:

  ```sh
  git checkout develop
  ```

- Create a **new branch**:

  ```sh
  git checkout -b release/vX.Y.Z
  ```

- Generate a summary of changes [^git-alias-github-pr-summary]:

  ```sh
  git lg-github-pr-summary master..release/vX.Y.Z
  ```

- Add the summary to a new changelog entry:

  ```sh
  nano 'HISTORY.md'
  git add 'HISTORY.md'
  git commit -m "chore: Update history for new version"
  ```

- Bump the package version. Use either of the following alternatives:

  ```sh
  bumpversion major|minor|patch

  bumpversion --new-version 'X.Y.Z' part  # 'part' is a dummy argument.
  ```


### Pull Request for Release

- Push the branch to `origin`:

  ```sh
  git push origin HEAD
  ```

- Create a **pull request**:
  - *Base reference*: `develop`
  - *Head reference*: `release/vX.Y.Z`
  - *Title*: `Release vX.Y.Z`
  - *Description*:

    ```markdown
    ## Changes

    (Insert here summary of changes from the changelog.)
    ```

  - *Labels*:
    - `task`
    - `kind: release`
- **Assign** the pull request to the appropriate developer (usually yourself).
- Wait until the CI checks have finished.
- Request pull request **reviews**.
- The pull request assignee will **merge** the branch into the main branch.
- After the pull request is **merged**, verify that the CI/CD system **successfully** builds the
  base branch.


### Pull Request for Deployment

- Check out the **main VCS branch**:

  ```sh
  git checkout develop
  ```

- Update local VCS repository:

  ```sh
  git pull --ff-only --rebase=false -v
  ```

- Verify that the **main branch** points to the merge commit of the **release pull request**. If
  that is not the case (which can happen if other pull requests were merged after the release pull
  request), check out the correct merge commit.
- Create a **new branch**:

  ```sh
  git checkout -b deploy/vX.Y.Z
  ```

- Push the branch to `origin`:

  ```sh
  git push origin HEAD
  ```

- Create a **pull request**:
  - *Base reference*: `master`
  - *Head reference*: `deploy/vX.Y.Z`
  - *Title*: `Deploy release vX.Y.Z`
  - *Description*:

    ```markdown
    Ref: (Insert here URL of release pull request.)
    ```

  - *Labels*:
    - `task`
    - `kind: deploy`
- **Assign** the pull request to the appropriate developer (usually yourself).
- Wait until the CI checks have finished.
- Request pull request **reviews**.
- The pull request assignee will **merge** the branch into the main branch.
- After the pull request is **merged**, verify that the CI/CD system **successfully** builds the
  base branch.


### GitHub Release

- **After** the pull request is merged, the CI/CD system will create a **Git tag** and a
  **GitHub release** from the merge commit, and **deploy** it to the **production environment**
  (by “deploy” it is meant: publish to the package registry).
- Go to the [repository's releases section](https://github.com/fyntex/lib-cl-sii-python/releases).
- **Edit** the release that was automatically created by the CI/CD workflow for the new version.
- Replace the release description with:

  ```markdown
  ## Changes

  (Insert here summary of changes from the changelog.)
  ```

- Click *Update release*.


### Publish to Package Registry

This is done by the CI/CD system.


[^semver]: [Semantic Versioning](https://semver.org/)
[^git-alias-github-pr-summary]: Add a Git alias that generates a summary of changes from GitHub pull
  requests:
  `git config --global alias.lg-github-pr-summary
    '!f() { git log --date=short --reverse --merges --grep "^Merge pull request #[[:digit:]]* from" --pretty="tformat:- (%C(auto,red)<S>%s</S>%C(reset), %C(auto,green)%ad%C(reset)) %b" "$@" | sed -E "s|<S>Merge pull request (#[0-9]+) from .+</S>|PR \1|"; }; f'` <!-- markdownlint-disable-line MD013 -->
