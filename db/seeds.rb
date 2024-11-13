# This file should contain all the record creation needed to seed the database with its default values.
# The data can then be loaded with the bin/rails db:seed command (or created alongside the database with db:setup).
#
# Examples:
#
#   movies = Movie.create([{ name: "Star Wars" }, { name: "Lord of the Rings" }])
#   Character.create(name: "Luke", movie: movies.first)
#
require 'csv'
require 'securerandom'


def set_can_post_via_external_api
  profiles = Profile.all
  profiles.each do |p|
    # Add external api token
    unless p.external_api_token
      p.external_api_token = SecureRandom.uuid
    end

    p.can_post_via_external_api = true
    p.save
  end
end

def ensure_co2_timestamp_exists
  events = Event.all

  # Refactor the data. Use more precise language
  events.each do |e|
    puts "Going though event id: #{e.id}"
    sensor_readings = e.sensor_readings

    if sensor_readings
      # Assumption, data is sampled every minute
      readings = sensor_readings.map.with_index do |s,i|

        if s.key?('value')
          s.merge({
            "co2": s["value"],
            "timestamp": (e.start_datetime + i.minute).to_s
          })
        else
          s
        end
      end

    else
      readings = (0..120).map.with_index do |i|
        {
          'co2': e.ventilation_co2_steady_state_ppm,
          "timestamp": (e.start_datetime + i.minute).to_s
        }
      end
    end

    # Handle missing sensor_data_from_external_api
    if e.sensor_data_from_external_api.nil?
      e.sensor_data_from_external_api = false
    end

    e.sensor_readings = readings
    e.save
  end
end


# set_can_post_via_external_api
# ensure_co2_timestamp_exists
# Import data

def import_mask_data
  masks = CSV.read('./data/amanda_armbrust_masknerd_pmm_for_kids_with_where_to_buy_url.csv')

  headers = []
  u = User.find_by(email: 'edderic@gmail.com')
  masks.each.with_index do |mask, j|
    if j == 0
      headers = masks[j]
      next
    end

    mask_data = {}
    filtration_efficiency = {}
    breathability = {}
    image_urls = []
    where_to_buy_urls = []

    headers.each.with_index do |header, index|
      if header == 'uimc_lower'
        next
      elsif ['where_to_buy_url_1', 'where_to_buy_url_2', 'where_to_buy_url_3'].include?(header) && mask[index].blank?
        next
      elsif ['filtration_efficiency_percent', 'filtration_efficiency_source', 'filtration_efficiency_notes'].include?(header)
        filtration_efficiency[header] = mask[index]
      elsif ['breathability_pascals', 'breathability_pascals_source', 'breathability_pascals_notes'].include?(header)
        breathability[header] = mask[index]
      elsif ['where_to_buy_url_1', 'where_to_buy_url_2', 'where_to_buy_url_3'].include?(header) && mask[index].present?
        where_to_buy_urls << mask[index]
      elsif header == 'image_url'
        mask_data["#{header}s"] = [mask[index]]
      elsif header == 'has_exhalation_valve'
        mask_data[header] = ActiveModel::Type::Boolean.new.cast(mask[index].downcase)
      else
        mask_data[header] = mask[index]
      end
    end

    mask_data['filtration_efficiencies'] = [filtration_efficiency]
    mask_data['breathability'] = [breathability]
    mask_data['where_to_buy_urls'] = where_to_buy_urls
    mask_data['author_id'] = u.id

    Mask.create!(**mask_data)
  end
end

# import_mask_data
#
def assign_user_id_when_facial
  fit_tests = FitTest.all

  fit_tests.each do |f|
    if f.facial_measurement && f.facial_measurement.user_id
      f.update(user_id: f.facial_measurement.user_id)
    end
  end
end

# assign_user_id_when_facial
#
#
#
def add_filtration_efficiency_seal_check_exercise_to_qnft
  fts = FitTest.all
  fts.each do |ft|
    results =  ft.results
    if results['quantitative'] && results['quantitative']['aerosol'] && results['quantitative']['aerosol']['initial_count_per_cm3'].present?
      quantitative = results['quantitative']
      exercises = quantitative['exercises']

      if exercises.any? {|e| e['name'].match("SEALED") }
        next
      else
        exercises << {
          'name' => 'Normal breathing (SEALED)',
          'fit_factor' => nil
        }

        quantitative['exercises'] = exercises

        results['quantitative'] = quantitative

        ft.update(results: results)
      end
    end
  end
end

add_filtration_efficiency_seal_check_exercise_to_qnft
