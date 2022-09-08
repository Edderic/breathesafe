# README

This README would normally document whatever steps are necessary to get the
application up and running.

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
