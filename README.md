# README

This README would normally document whatever steps are necessary to get the
application up and running.

# Ask Edderic for your AWS credentials
AWS credentials will help us programmatically dump databases and import them.

# Environment Variables
```zsh
export BREATHESAFE_PROD_S3="s3://breathesafe"
export BREATHESAFE_DEV="<working directory to your breathesafe app>"
```

## Install RVM
- [RVM](https://rvm.io/)

## Install Ruby
`rvm install 3.1.2`

## Install Postgresql
`brew services start postgresql`

### On Mac

`brew install postgresql`

## Install Gems
`bundle install`

## Install Node
https://nodejs.org/en/

## Install NPM
`sudo npm install -g npm`

## Install Yarn
`npm install --global yarn`


## Run postgresql service
`brew services start postgresql`

# Creating a server on Heroku
```
heroku buildpacks:set heroku/ruby
```

## Also add nodejs so that npm can be used
`heroku buildpacks:add --index 1 heroku/nodejs`

# Dumping data from local to Production
[Heroku](https://devcenter.heroku.com/articles/heroku-postgres-import-export)
[Stackoverflow](https://stackoverflow.com/questions/59670645/heroku-importing-from-s3-failing/65797543#65797543)

## Dump Development database
`pg_dump -Fc --no-acl --no-owner -h localhost breathesafe_development > $BREATHESAFE_DEV/data/dumps/mydb.dump`

## Sync
`aws s3 sync $BREATHESAFE_DEV/data $BREATHESAFE_PROD_S3/data`
[Upload here](https://s3.console.aws.amazon.com/s3/buckets/breathesafe?prefix=database/&region=us-east-2)

## Sign the URL
`aws s3 presign s3://breathesafe/data/dumps/mydb.dump`

## Push to heroku
`heroku pg:backups:restore '<SIGNED URL>' DATABASE_URL --app example-app`

e.g.

`heroku pg:backups:restore 'https://breathesafe.s3.us-east-1.amazonaws.com/data/dumps/mydb.dump\?X-Amz-Algorithm\=AWS4-HMAC-SHA256\&X-Amz-Credential\=AKIAYQOGK2G6J2YHH7OC%2F20220909%2Fus-east-1%2Fs3%2Faws4_request\&X-Amz-Date\=20220909T112256' DATABASE_URL --app breathesafe`


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
