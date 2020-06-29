set -eu

repo_uri="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
remote_name="origin"
main_branch="master"
app_name="${HEROKU_APP_NAME}"

git config user.name "$GITHUB_ACTOR"
git config user.email "${GITHUB_ACTOR}@bots.github.com"

echo "start of task"

git add .
set +e  # Grep succeeds with nonzero exit codes to show results.
git status | grep 'new file\|modified'
if [ $? -eq 0 ]
then
    set -e
    git commit -am "data updated on - $(date)"
    git remote set-url "$remote_name" "$repo_uri"
    git push -u "$remote_name" "$main_branch"
    echo "Pushed to Github"

    heroku auth:token
    heroku git:remote -a "$app_name"
    git push heroku "$main_branch"
    echo "Pushed to Heroku"
else
    set -e
    echo "No changes since last run"
fi

echo "end of task"
