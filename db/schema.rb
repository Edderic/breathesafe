# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[7.0].define(version: 2024_07_22_173522) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_stat_statements"
  enable_extension "plpgsql"

  create_table "carbon_dioxide_monitors", force: :cascade do |t|
    t.string "name"
    t.string "model"
    t.string "serial"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["serial"], name: "index_carbon_dioxide_monitors_on_serial"
  end

  create_table "covid_states", force: :cascade do |t|
    t.date "date"
    t.string "state"
    t.integer "fips"
    t.integer "cases_cumulative"
    t.integer "deaths_cumulative"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "events", force: :cascade do |t|
    t.jsonb "portable_air_cleaners"
    t.float "room_width_meters"
    t.float "room_length_meters"
    t.float "room_height_meters"
    t.string "room_name"
    t.float "room_usable_volume_factor"
    t.jsonb "place_data"
    t.jsonb "activity_groups"
    t.float "ventilation_co2_ambient_ppm"
    t.string "ventilation_co2_measurement_device_name"
    t.string "ventilation_co2_measurement_device_model"
    t.string "ventilation_co2_measurement_device_serial"
    t.float "ventilation_co2_steady_state_ppm"
    t.text "ventilation_notes"
    t.datetime "start_datetime"
    t.string "duration"
    t.string "private"
    t.integer "author_id", null: false
    t.jsonb "occupancy"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.float "ventilation_ach"
    t.float "portable_ach"
    t.float "room_usable_volume_cubic_meters"
    t.float "total_ach"
    t.integer "maximum_occupancy"
    t.integer "approved_by_id"
    t.integer "initial_co2"
    t.jsonb "sensor_readings"
    t.string "status"
    t.boolean "sensor_data_from_external_api", default: false
    t.index ["author_id"], name: "index_events_on_author_id"
  end

  create_table "facial_measurements", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.string "source"
    t.integer "face_width"
    t.integer "jaw_width"
    t.integer "face_depth"
    t.integer "face_length"
    t.string "lower_face_length"
    t.integer "bitragion_menton_arc"
    t.integer "bitragion_subnasale_arc"
    t.string "cheek_fullness"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.integer "nasal_root_breadth"
    t.integer "nose_protrusion"
    t.integer "nose_bridge_height"
    t.integer "lip_width"
    t.index ["user_id"], name: "index_facial_measurements_on_user_id"
  end

  create_table "masks", force: :cascade do |t|
    t.string "unique_internal_model_code"
    t.json "modifications"
    t.string "filter_type"
    t.boolean "elastomeric"
    t.string "image_urls"
    t.string "author_ids"
    t.string "where_to_buy_urls"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "population_states", force: :cascade do |t|
    t.integer "population"
    t.string "name"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "profiles", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.string "measurement_system", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.integer "num_positive_cases_last_seven_days"
    t.integer "num_people_population"
    t.float "uncounted_cases_multiplier"
    t.string "mask_type"
    t.string "event_display_risk_time"
    t.string "first_name"
    t.string "last_name"
    t.float "height_meters"
    t.float "stride_length_meters"
    t.jsonb "socials"
    t.uuid "external_api_token"
    t.boolean "can_post_via_external_api", default: true
    t.json "demographics"
    t.string "race_ethnicity"
    t.string "gender_and_sex"
    t.string "other_gender"
    t.index ["user_id"], name: "index_profiles_on_user_id"
  end

  create_table "states", force: :cascade do |t|
    t.string "full_name"
    t.string "code"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "user_carbon_dioxide_monitors", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.string "serial", null: false
    t.string "model", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["user_id"], name: "index_user_carbon_dioxide_monitors_on_user_id"
  end

  create_table "users", force: :cascade do |t|
    t.string "email", default: "", null: false
    t.string "encrypted_password", default: "", null: false
    t.string "reset_password_token"
    t.datetime "reset_password_sent_at"
    t.datetime "remember_created_at"
    t.integer "sign_in_count", default: 0, null: false
    t.datetime "current_sign_in_at"
    t.datetime "last_sign_in_at"
    t.string "current_sign_in_ip"
    t.string "last_sign_in_ip"
    t.string "confirmation_token"
    t.datetime "confirmed_at"
    t.datetime "confirmation_sent_at"
    t.string "unconfirmed_email"
    t.integer "failed_attempts", default: 0, null: false
    t.string "unlock_token"
    t.datetime "locked_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.boolean "admin", default: false
    t.index ["confirmation_token"], name: "index_users_on_confirmation_token", unique: true
    t.index ["email"], name: "index_users_on_email", unique: true
    t.index ["reset_password_token"], name: "index_users_on_reset_password_token", unique: true
    t.index ["unlock_token"], name: "index_users_on_unlock_token", unique: true
  end

  add_foreign_key "facial_measurements", "users"
  add_foreign_key "profiles", "users"
  add_foreign_key "user_carbon_dioxide_monitors", "users"
end
