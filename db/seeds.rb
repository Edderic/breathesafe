# This file should contain all the record creation needed to seed the database with its default values.
# The data can then be loaded with the bin/rails db:seed command (or created alongside the database with db:setup).
#
# Examples:
#
#   movies = Movie.create([{ name: "Star Wars" }, { name: "Lord of the Rings" }])
#   Character.create(name: "Luke", movie: movies.first)
#
require 'securerandom'

profiles = Profile.all
profiles.each do |p|
  unless p.external_api_token
    p.external_api_token = SecureRandom.uuid
    p.save
  end
end

events = Event.all

# Refactor the data. Use more precise language
events.each do |e|
  sensor_readings = e.sensor_readings
  if e.sensor_data_from_external_api.nil?
    e.sensor_data_from_external_api = false
  end

  if sensor_readings
    readings = sensor_readings.map do |s|

      if s.key?('value')
        return s.merge({
          "co2": s["value"],
          "timestamp": s["identifier"]
        })
      end

      s
    end

    e.sensor_readings = readings
  end

  e.save
end
