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
  # Add external api token
  unless p.external_api_token
    p.external_api_token = SecureRandom.uuid
  end

  p.can_post_via_external_api = true
  p.save
end

events = Event.all

# Refactor the data. Use more precise language
events.each do |e|
  puts "Going though event id: #{e.id}"
  sensor_readings = e.sensor_readings

  if sensor_readings
    # Assumption, data is sampled every second
    readings = sensor_readings.map.with_index do |s,i|

      if s.key?('value')
        s.merge({
          "co2": s["value"],
          "timestamp": (e.start_datetime + i.second).to_s
        })
      else
        s
      end
    end

    e.sensor_readings = readings
  end
  e.save
end
