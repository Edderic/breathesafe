# README

This README would normally document whatever steps are necessary to get the
application up and running on Mac OS.

# Ask Edderic for your AWS credentials
AWS credentials will help us programmatically dump databases and import them.

# Environment Variables

## .zshrc
Put these in your `~/.zshrc` file.

```zsh
export BREATHESAFE_STAG_S3="s3://breathesafe-staging"
export BREATHESAFE_PROD_S3="s3://breathesafe"
export BREATHESAFE_DEV="<working directory to your breathesafe app>"
export BREATHESAFE_DEV_S3="s3://breathesafe-development"
```

Afterwards, run `source ~/.zshrc` in your terminal.

## .env
This is the place used by the `dotenv` gem of our app to pick up environment
variables for development. Note that `.env` is git-ignored. Here are the
variables that should be in there.

```
GOOGLE_MAPS_API_KEY=abcdefg
NODE_ENV=development
S3_HTTPS='https://breathesafe-development.s3.us-east-2.amazonaws.com'
```

Note that S3 is what is being used by `app/javascript/map_events.vue` to
host the SVG images for Google Maps custom markers.

After making changes to `.env`, you'll want to find the process that is running
the rails server (i.e. the process that is currently running `rails s`). In
other words, terminate the process that is running `rails s`, run `source
~/.zshrc` for changing to take effect for said process, and then run `rails s`
again.

# Installation

## Install RVM
- [RVM](https://rvm.io/)

## Install Ruby

`rvm install 3.1.2`

RVM suggests running the following:
`source /Users/richhu/.rvm/scripts/rvm`

## Install Postgresql

`brew install postgresql`

## Run postgresql service

`brew services start postgresql`

## Stop postgresql service (not necessary)

`brew services stop postgresql`

## Install Gems

`gem install bundler`
`bundle install`

## Install Node
https://nodejs.org/en/

## Install NPM (optional)

`sudo npm install -g npm`

## Install [Yarn](https://engineering.fb.com/2016/10/11/web/yarn-a-new-package-manager-for-javascript/)

`npm install --global yarn`

## Install Yarn without NPM:

`cd ~ && brew install yarn`

Go to your local cloned breathsafe directory and type:

`yarn install`

## Start Rails
`rails s`

## Create DB

`rails db:create`

## Run DB migration files (breathsafe separates DDL and DML so this is just DDL)

`rails db:migrate`

## Access postgres db via psql

`psql -d breathesafe_development`

# Creating a server on Heroku

```
heroku buildpacks:set heroku/ruby
```

## Also add nodejs so that npm can be used

`heroku buildpacks:add --index 1 heroku/nodejs`

# Dumping data from local to Production
[Heroku](https://devcenter.heroku.com/articles/heroku-postgres-import-export)
[Stackoverflow](https://stackoverflow.com/questions/59670645/heroku-importing-from-s3-failing/65797543#65797543)

## Dump Development database so that it can be copied
`pg_dump -Fc --no-acl --no-owner -h localhost breathesafe_development > $BREATHESAFE_DEV/data/dumps/mydb.dump`

## Restore database dump

```bash
heroku pg:backups:capture --app breathesafe
heroku pg:backups:download --app breathesafe

pg_restore --verbose --clean --no-acl --no-owner -h localhost -d breathesafe_development latest.dump
```

## Sign the URL
`aws s3 presign s3://breathesafe/data/dumps/mydb.dump`

## Push to heroku
`heroku pg:backups:restore '<SIGNED URL>' DATABASE_URL --app example-app`

e.g.

`heroku pg:backups:restore 'https://breathesafe.s3.us-east-1.amazonaws.com/data/dumps/mydb.dump\?X-Amz-Algorithm\=AWS4-HMAC-SHA256\&X-Amz-Credential\=AKIAYQOGK2G6J2YHH7OC%2F20220909%2Fus-east-1%2Fs3%2Faws4_request\&X-Amz-Date\=20220909T112256' DATABASE_URL --app breathesafe`

# How to use multiple AWS accounts from the command line

This [link](https://stackoverflow.com/questions/593334/how-to-use-multiple-aws-accounts-from-the-command-line#:~:text=You%20can%20work%20with%20two,region%2C%20so%20have%20them%20ready.&text=You%20can%20then%20switch%20between,the%20profile%20on%20the%20command.) talks about how to set a profile so that you could let AWS know which profile you want to use, e.g. `--profile some-profile` when running a command.

# Updating icons

Below will produce new images under `$BREATHESAFE_DEV/app/assets/images/generated`:
`python python/generate_place_grades_icons.py`

## Pushing icons to S3 Production

Note that we're using `--profile` here. See the "How to use multiple AWS
accounts from the command line" section above to understand what it is doing.

After making sure that `$BREATHESAFE_DEV/app/assets/images/generated` has SVGs,
in the earlier step, we can sync to S3:

`aws s3 sync $BREATHESAFE_DEV/app/assets/images/generated $BREATHESAFE_PROD_S3/images/generated --profile breathesafe-edderic`
# Sync

Right now, we host a bunch of Google Maps custom markers in S3. So when we make
changes to those SVGs, they should be pushed to staging and production.

### Copy local data folder to production S3
`aws s3 sync $BREATHESAFE_DEV/data $BREATHESAFE_PROD_S3/data`
[Upload here](https://s3.console.aws.amazon.com/s3/buckets/breathesafe?prefix=database/&region=us-east-2)

### Copy local data folder to staging S3
`aws s3 sync $BREATHESAFE_DEV/data $BREATHESAFE_STAG_S3/data`
[Upload here](https://s3.console.aws.amazon.com/s3/buckets/breathesafe-staging?prefix=database/&region=us-east-2)

### Copy local data folder to development S3
`aws s3 sync $BREATHESAFE_DEV/data $BREATHESAFE_DEV_S3/data`
[Upload here](https://s3.console.aws.amazon.com/s3/buckets/breathesafe-staging?prefix=database/&region=us-east-2)

# Add remote heroku repos

Add Heroku staging repo so we can push or fetch to it:

```
git remote add breathesafe-stag https://git.heroku.com/breathesafe-staging.git`
```

Add Heroku production repo so we can push or fetch to it:

```
git remote add breathesafe-prod https://git.heroku.com/breathesafe-staging.git`
```

# Development-to-Production Process

## Making changes to a branch, then merging it to the development branch
- Make a branch.
- Make changes and commit them to that branch
- Create a pull request. Specify that the base branch be `development`.
- Wait for someone else to review your code.
- Reviewer makes suggestions.
- Assuming the reviewer accepts the pull request, you can then hit `Rebase and merge`.

- `git fetch`
- `git checkout staging`

## Pushing to the staging branch
- Make the staging branch have the commits of `origin/development`:
  ```
  git rebase origin/development
  ```

- Push staging to github (implicitly):
  ```
  git push
  ```

- Push to the Heroku staging repository, `git push breathesafe-stag staging:main` so that one's local `staging` branch is pushed to the `main` branch.

- Visit the staging site and see if the changes made didn't break anything.

## Push to the production branch

Assuming nothing broke, and everything looks expected:
```
git push breathesafe-prod staging:main
```

Edderic: It looks like we could use the "Promote to Production" in the Heroku Pipelines section. Not sure yet, since I haven't used it directly.

## Pushing icons to S3 Development
`aws s3 sync $BREATHESAFE_DEV/app/assets/images/generated $BREATHESAFE_DEV_S3/images/generated --profile breathesafe-edderic`

## Pushing icons to S3 Staging
`aws s3 sync $BREATHESAFE_DEV/app/assets/images/generated $BREATHESAFE_STAG_S3/images/generated --profile breathesafe-edderic`

Things you may want to cover:

* Ruby version

* System dependencies

* Configuration

* Database creation

* Database initialization

* How to run the test suite

* Services (job queues, cache servers, search engines, etc.)

* Deployment instructions

* ...
