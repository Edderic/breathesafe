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

ActiveRecord::Schema[7.0].define(version: 2022_07_11_021908) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "carbon_dioxide_monitors", force: :cascade do |t|
    t.string "name"
    t.string "model"
    t.string "serial"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["serial"], name: "index_carbon_dioxide_monitors_on_serial"
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
    t.index ["author_id"], name: "index_events_on_author_id"
  end

  create_table "profiles", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.string "measurement_system", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["user_id"], name: "index_profiles_on_user_id"
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
    t.index ["confirmation_token"], name: "index_users_on_confirmation_token", unique: true
    t.index ["email"], name: "index_users_on_email", unique: true
    t.index ["reset_password_token"], name: "index_users_on_reset_password_token", unique: true
    t.index ["unlock_token"], name: "index_users_on_unlock_token", unique: true
  end

  add_foreign_key "profiles", "users"
  add_foreign_key "user_carbon_dioxide_monitors", "users"
end
