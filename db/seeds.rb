# This file should contain all the record creation needed to seed the database with its default values.
# The data can then be loaded with the bin/rails db:seed command (or created alongside the database with db:setup).
#
# Examples:
#
#   movies = Movie.create([{ name: "Star Wars" }, { name: "Lord of the Rings" }])
#   Character.create(name: "Luke", movie: movies.first)
#
require 'securerandom'

users = User.all
users.each do |u|
  unless u.external_api_token
    u.external_api_token = SecureRandom.uuid
    u.save
  end
end
