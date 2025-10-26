# frozen_string_literal: true

class FitTest < ApplicationRecord
  belongs_to :mask, optional: true
  belongs_to :facial_measurement, optional: true
  belongs_to :user
  belongs_to :quantitative_fit_testing_device, class_name: 'MeasurementDevice', optional: true

  def self.viewable(user)
    # Use ActiveRecord queries to ensure encryption/decryption works properly
    if user.admin?
      fit_tests = FitTest.includes(:user, :mask, :facial_measurement, user: :profile)
                         .order(updated_at: :desc)
    else
      managed_user_ids = ManagedUser.where(manager_id: user.id).pluck(:managed_id)
      fit_tests = FitTest.includes(:user, :mask, :facial_measurement, user: :profile)
                         .where(user_id: managed_user_ids)
                         .order(updated_at: :desc)
    end

    result = []

    fit_tests.each do |ft|
      profile = ft.user.profile
      mask = ft.mask
      facial_measurement = ft.facial_measurement

      # Build the result hash with decrypted values
      row = {
        # FitTest attributes
        'id' => ft.id,
        'user_id' => ft.user_id,
        'mask_id' => ft.mask_id,
        'facial_measurement_id' => ft.facial_measurement_id,
        'quantitative_fit_testing_device_id' => ft.quantitative_fit_testing_device_id,
        'facial_hair' => ft.facial_hair,
        'comfort' => ft.comfort,
        'results' => ft.results,
        'user_seal_check' => ft.user_seal_check,
        'created_at' => ft.created_at,
        'updated_at' => ft.updated_at,

        # Mask attributes
        'unique_internal_model_code' => mask&.unique_internal_model_code,
        'image_urls' => mask&.image_urls,
        'has_exhalation_valve' => mask&.has_exhalation_valve,
        'strap_type' => mask&.strap_type,
        'style' => mask&.style,
        'perimeter_mm' => mask&.perimeter_mm,
        'colors' => mask&.colors,

        # Profile attributes (these will be automatically decrypted)
        'first_name' => profile&.first_name,  # This will be decrypted
        'last_name' => profile&.last_name,    # This will be decrypted

        # Facial measurement attributes
        'fm_user_id' => facial_measurement&.user_id
      }

      # Add facial measurement presence data if available
      if facial_measurement
        FacialMeasurement::COLUMNS.each do |column|
          row["#{column}_present"] = facial_measurement.send(column).present? ? 1 : 0
        end

        # Calculate facial measurement presence status
        required_columns = %w[
          face_width jaw_width face_depth face_length lower_face_length
          bitragion_menton_arc bitragion_subnasale_arc cheek_fullness nasal_root_breadth
          nose_protrusion nose_bridge_height lip_width head_circumference nose_breadth
        ]
        missing_columns = required_columns.reject { |col| facial_measurement.send(col).blank? }

        row['facialMeasurementPresence'] = if missing_columns.empty?
                                             'Complete'
                                           else
                                             'Partially missing'
                                           end
      else
        FacialMeasurement::COLUMNS.each do |column|
          row["#{column}_present"] = 0
        end
        row['facialMeasurementPresence'] = 'Completely missing'
      end

      result << row
    end

    result
  end

  def self.find_by_id_with_user_id(id)
    # Use ActiveRecord queries to ensure encryption/decryption works properly
    fit_test = FitTest.includes(:user, :mask, :facial_measurement, user: :profile)
                      .find(id)

    profile = fit_test.user.profile
    mask = fit_test.mask
    facial_measurement = fit_test.facial_measurement

    # Build the result hash with decrypted values
    row = {
      # FitTest attributes
      'id' => fit_test.id,
      'user_id' => fit_test.user_id,
      'mask_id' => fit_test.mask_id,
      'facial_measurement_id' => fit_test.facial_measurement_id,
      'quantitative_fit_testing_device_id' => fit_test.quantitative_fit_testing_device_id,
      'facial_hair' => fit_test.facial_hair,
      'comfort' => fit_test.comfort,
      'results' => fit_test.results,
      'user_seal_check' => fit_test.user_seal_check,
      'created_at' => fit_test.created_at,
      'updated_at' => fit_test.updated_at,

      # Mask attributes
      'unique_internal_model_code' => mask&.unique_internal_model_code,
      'image_urls' => mask&.image_urls,
      'has_exhalation_valve' => mask&.has_exhalation_valve,

      # Profile attributes (these will be automatically decrypted)
      'first_name' => profile&.first_name,  # This will be decrypted
      'last_name' => profile&.last_name,    # This will be decrypted

      # Facial measurement attributes
      'fm_user_id' => facial_measurement&.user_id
    }

    # Add facial measurement presence data if available
    if facial_measurement
      FacialMeasurement::COLUMNS.each do |column|
        row["#{column}_present"] = facial_measurement.send(column).present? ? 1 : 0
      end

      # Calculate facial measurement presence status
      required_columns = %w[
        face_width jaw_width face_depth face_length lower_face_length bitragion_menton_arc
        bitragion_subnasale_arc cheek_fullness nasal_root_breadth nose_protrusion
        nose_bridge_height lip_width head_circumference nose_breadth]
      missing_columns = required_columns.reject { |col| facial_measurement.send(col).blank? }

      row['facialMeasurementPresence'] = if missing_columns.empty?
                                           'Complete'
                                         else
                                           'Partially missing'
                                         end
    else
      FacialMeasurement::COLUMNS.each do |column|
        row["#{column}_present"] = 0
      end
      row['facialMeasurementPresence'] = 'Completely missing'
    end

    # Apply json_parse logic for specific columns
    %w[facial_hair comfort results user_seal_check image_urls].each do |col|
      row[col] = if !row[col]
                   []
                 elsif col == 'image_urls'
                   [row['image_urls'].gsub('{', '').gsub('}', '').gsub('"', '')]
                 else
                   JSON.parse(row[col])
                 end
    end

    row
  end

  def self.json_parse(events, columns)
    events.map do |ev|
      columns.each do |col|
        ev[col] = if !ev[col]
                    []
                  elsif col == 'image_urls'
                    [ev['image_urls'].gsub('{', '').gsub('}', '').gsub('"', '')]
                  else
                    JSON.parse(ev[col])
                  end
      end

      ev
    end
  end

  def self.facial_measurement_presence
    <<-SQL
      CASE WHEN fm.face_width IS NOT NULL
          AND fm.jaw_width IS NOT NULL
          AND fm.face_depth IS NOT NULL
          AND fm.face_length IS NOT NULL
          AND fm.lower_face_length IS NOT NULL
          AND fm.bitragion_menton_arc IS NOT NULL
          AND fm.bitragion_subnasale_arc IS NOT NULL
          AND fm.cheek_fullness IS NOT NULL
          AND fm.nasal_root_breadth IS NOT NULL
          AND fm.nose_protrusion IS NOT NULL
          AND fm.nose_bridge_height IS NOT NULL
          AND fm.lip_width IS NOT NULL
        THEN 'Complete'
      WHEN fm.id IS NULL
        THEN 'Completely missing'
      ELSE 'Partially missing'
      END AS facial_measurement_presence
    SQL
  end
end
