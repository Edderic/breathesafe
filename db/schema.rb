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

ActiveRecord::Schema[7.0].define(version: 2025_08_04_025902) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_stat_statements"
  enable_extension "plpgsql"
  enable_extension "postgis"

  create_table "actions", force: :cascade do |t|
    t.datetime "datetime"
    t.string "name"
    t.string "type"
    t.jsonb "metadata"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "address_statuses", force: :cascade do |t|
    t.uuid "uuid", null: false
    t.datetime "refresh_datetime", null: false
    t.string "address_line_1", null: false
    t.string "address_line_2"
    t.string "address_line_3"
    t.string "town_city", null: false
    t.string "country", null: false
    t.string "state", null: false
    t.string "zip_code", null: false
    t.geometry "address_coordinate", limit: {:srid=>0, :type=>"geometry"}
    t.string "stringified_address", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["uuid", "refresh_datetime"], name: "index_address_statuses_on_uuid_and_refresh_datetime", unique: true
  end

  create_table "addresses", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.string "start_datetime"
    t.string "address_line_1"
    t.string "address_line_2"
    t.string "address_line_3"
    t.string "town_city"
    t.string "state"
    t.string "country"
    t.string "zipcode"
    t.string "phone_number"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["user_id"], name: "index_addresses_on_user_id"
  end

  create_table "carbon_dioxide_monitors", force: :cascade do |t|
    t.string "name"
    t.string "model"
    t.string "serial"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["serial", "model"], name: "index_carbon_dioxide_monitors_on_serial_and_model", unique: true
    t.index ["serial"], name: "index_carbon_dioxide_monitors_on_serial"
  end

  create_table "digital_caliper_statuses", force: :cascade do |t|
    t.uuid "uuid", null: false
    t.uuid "facial_measurement_kit_uuid"
    t.datetime "refresh_datetime", null: false
    t.jsonb "how"
    t.jsonb "cost"
    t.string "model", null: false
    t.jsonb "weight"
    t.jsonb "power_supply"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["uuid", "refresh_datetime", "facial_measurement_kit_uuid"], name: "index_dig_cal_sta_on_uuid_refr_fm_kit_uuid", unique: true
  end

  create_table "facial_measurement_kit_statuses", force: :cascade do |t|
    t.uuid "uuid", null: false
    t.datetime "refresh_datetime", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["uuid", "refresh_datetime"], name: "index_fmks_on_uuid_refr_datetime__unique_true", unique: true
  end

  create_table "facial_measurements", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.string "source"
    t.integer "face_width"
    t.integer "jaw_width"
    t.integer "face_depth"
    t.integer "face_length"
    t.float "lower_face_length"
    t.integer "bitragion_menton_arc"
    t.integer "bitragion_subnasale_arc"
    t.string "cheek_fullness"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.integer "nasal_root_breadth"
    t.integer "nose_protrusion"
    t.integer "nose_bridge_height"
    t.integer "lip_width"
    t.integer "head_circumference"
    t.integer "nose_breadth"
    t.index ["user_id"], name: "index_facial_measurements_on_user_id"
  end

  create_table "fit_tests", force: :cascade do |t|
    t.bigint "mask_id"
    t.jsonb "user_seal_check"
    t.jsonb "comfort"
    t.jsonb "facial_hair"
    t.jsonb "results"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "facial_measurement_id"
    t.bigint "quantitative_fit_testing_device_id"
    t.bigint "user_id"
    t.index ["facial_measurement_id"], name: "index_fit_tests_on_facial_measurement_id"
    t.index ["mask_id"], name: "index_fit_tests_on_mask_id"
    t.index ["quantitative_fit_testing_device_id"], name: "index_fit_tests_on_quantitative_fit_testing_device_id"
    t.index ["user_id"], name: "index_fit_tests_on_user_id"
  end

  create_table "hood_statuses", force: :cascade do |t|
    t.uuid "uuid", null: false
    t.datetime "refresh_datetime", null: false
    t.jsonb "how"
    t.jsonb "cost"
    t.string "model", null: false
    t.jsonb "weight"
    t.jsonb "sanitization"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["uuid", "refresh_datetime"], name: "index_hood_statuses_on_uuid_and_refresh_datetime", unique: true
    t.index ["uuid"], name: "index_hood_statuses_on_uuid"
  end

  create_table "managed_users", force: :cascade do |t|
    t.bigint "manager_id", null: false
    t.bigint "managed_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["managed_id"], name: "index_managed_users_on_managed_id"
    t.index ["manager_id"], name: "index_managed_users_on_manager_id"
  end

  create_table "mask_kit_statuses", force: :cascade do |t|
    t.uuid "uuid", null: false
    t.integer "mask_uuid", null: false
    t.datetime "refresh_datetime", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["uuid", "mask_uuid", "refresh_datetime"], name: "index_uuid_mask_uuid_datetime_on_mkst", unique: true
  end

  create_table "masks", force: :cascade do |t|
    t.string "unique_internal_model_code"
    t.json "modifications"
    t.string "image_urls", default: [], array: true
    t.integer "author_ids", default: [], array: true
    t.string "where_to_buy_urls", default: [], array: true
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "strap_type"
    t.string "mass_grams"
    t.string "height_mm"
    t.string "width_mm"
    t.string "depth_mm"
    t.boolean "has_gasket"
    t.float "initial_cost_us_dollars"
    t.string "sources", default: [], array: true
    t.text "notes"
    t.string "filter_type"
    t.jsonb "filtration_efficiencies", default: []
    t.jsonb "breathability", default: []
    t.string "style"
    t.float "filter_change_cost_us_dollars"
    t.string "age_range"
    t.string "color"
    t.boolean "has_exhalation_valve"
    t.bigint "author_id", null: false
    t.float "perimeter_mm"
    t.json "payable_datetimes", default: []
    t.jsonb "colors", default: [], null: false
    t.index ["author_id"], name: "index_masks_on_author_id"
    t.index ["unique_internal_model_code"], name: "index_masks_on_unique_internal_model_code", unique: true
  end

  create_table "measurement_devices", force: :cascade do |t|
    t.string "manufacturer"
    t.string "measurement_device_type"
    t.string "model"
    t.string "serial"
    t.text "notes"
    t.bigint "owner_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.boolean "remove_from_service", default: false
    t.index ["owner_id"], name: "index_measurement_devices_on_owner_id"
  end

  create_table "nebulizer_statuses", force: :cascade do |t|
    t.uuid "uuid", null: false
    t.datetime "refresh_datetime", null: false
    t.jsonb "how"
    t.jsonb "cost"
    t.string "model", null: false
    t.jsonb "weight"
    t.jsonb "batteries"
    t.jsonb "power_supply"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["uuid", "refresh_datetime"], name: "index_nebulizer_statuses_on_uuid_and_refresh_datetime", unique: true
    t.index ["uuid"], name: "index_nebulizer_statuses_on_uuid"
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
    t.integer "year_of_birth"
    t.datetime "study_start_datetime"
    t.datetime "study_goal_end_datetime"
    t.index ["user_id"], name: "index_profiles_on_user_id"
  end

  create_table "qualitative_fit_testing_kit_joins", force: :cascade do |t|
    t.uuid "qlft_kit_uuid", null: false
    t.uuid "part_uuid", null: false
    t.string "part_type", null: false
    t.datetime "refresh_datetime", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["qlft_kit_uuid", "part_uuid", "refresh_datetime"], name: "index_qlft_kit_join_on_qlft_kit_uuid_part_uuid_refresh_datetime", unique: true
  end

  create_table "qualitative_fit_testing_kit_statuses", force: :cascade do |t|
    t.uuid "uuid"
    t.datetime "refresh_datetime"
    t.string "type"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["uuid", "refresh_datetime", "type"], name: "index_qlft_kit_on_uuid_refresh_datetime_type_unique_true", unique: true
  end

  create_table "shipping_status_joins", force: :cascade do |t|
    t.datetime "refresh_datetime", null: false
    t.string "shippable_type", null: false
    t.uuid "shipping_uuid", null: false
    t.uuid "shippable_uuid", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["shipping_uuid", "shippable_uuid", "refresh_datetime"], name: "index_ssj_on_ship_uuid_shippable_uuid_refresh_datetime"
  end

  create_table "shipping_statuses", force: :cascade do |t|
    t.uuid "uuid"
    t.datetime "refresh_datetime", null: false
    t.string "to_user_uuid"
    t.string "from_user_uuid"
    t.jsonb "received"
    t.jsonb "delivered"
    t.uuid "from_address_uuid"
    t.uuid "to_address_uuid"
    t.jsonb "purchase_label"
    t.jsonb "send_to_courier"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["uuid", "refresh_datetime"], name: "index_shipping_statuses_on_uuid_and_refresh_datetime", unique: true
  end

  create_table "solution_statuses", force: :cascade do |t|
    t.uuid "uuid", null: false
    t.datetime "refresh_datetime", null: false
    t.string "model", null: false
    t.jsonb "flavor_type", null: false
    t.jsonb "how"
    t.jsonb "cost"
    t.jsonb "volume"
    t.string "concentration_type"
    t.float "volume_level_proportion"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["uuid", "refresh_datetime"], name: "index_solution_statuses_on_uuid_and_refresh_datetime", unique: true
    t.index ["uuid"], name: "index_solution_statuses_on_uuid"
  end

  create_table "states", force: :cascade do |t|
    t.string "full_name"
    t.string "code"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "study_participant_statuses", force: :cascade do |t|
    t.uuid "study_uuid", null: false
    t.string "participant_uuid", null: false
    t.datetime "refresh_datetime"
    t.datetime "interested_datetime"
    t.datetime "accepted_datetime"
    t.jsonb "removal_from_study", default: {}
    t.jsonb "qualifications", default: {}
    t.jsonb "equipment", default: {}
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.datetime "finished_study_datetime"
    t.index ["study_uuid", "participant_uuid", "refresh_datetime"], name: "index_stu_par_sta_on_study_uuid_participant_uuid_refr_dt", unique: true
  end

  create_table "study_statuses", force: :cascade do |t|
    t.uuid "uuid", null: false
    t.string "name", null: false
    t.datetime "refresh_datetime", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["uuid", "name", "refresh_datetime"], name: "index_study_statuses_on_uuid_and_name_and_refresh_datetime", unique: true
  end

  create_table "tape_measure_statuses", force: :cascade do |t|
    t.uuid "uuid", null: false
    t.uuid "facial_measurement_kit_uuid"
    t.jsonb "cost"
    t.string "model", null: false
    t.jsonb "weight"
    t.datetime "refresh_datetime", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["uuid", "refresh_datetime", "facial_measurement_kit_uuid"], name: "index_tape_mea_sta_on_uuid_refr_fm_kit_uuid", unique: true
  end

  create_table "user_carbon_dioxide_monitors", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.string "serial", null: false
    t.string "model", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["user_id"], name: "index_user_carbon_dioxide_monitors_on_user_id"
  end

  create_table "user_statuses", force: :cascade do |t|
    t.string "uuid", null: false
    t.string "first_name"
    t.string "last_name"
    t.boolean "high_risk"
    t.uuid "address_uuid"
    t.datetime "refresh_datetime"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
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

  create_table "ventilation_records", force: :cascade do |t|
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
    t.index ["author_id"], name: "index_ventilation_records_on_author_id"
  end

  add_foreign_key "addresses", "users"
  add_foreign_key "facial_measurements", "users"
  add_foreign_key "fit_tests", "facial_measurements"
  add_foreign_key "fit_tests", "masks"
  add_foreign_key "fit_tests", "measurement_devices", column: "quantitative_fit_testing_device_id"
  add_foreign_key "fit_tests", "users"
  add_foreign_key "managed_users", "users", column: "managed_id"
  add_foreign_key "managed_users", "users", column: "manager_id"
  add_foreign_key "masks", "users", column: "author_id"
  add_foreign_key "measurement_devices", "users", column: "owner_id"
  add_foreign_key "profiles", "users"
  add_foreign_key "user_carbon_dioxide_monitors", "users"
end
