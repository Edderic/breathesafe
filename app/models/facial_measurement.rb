# frozen_string_literal: true

class FacialMeasurement < ApplicationRecord
  RECOMMENDER_COLUMNS = %w[
    bitragion_subnasale_arc
    face_width
    face_length
    nose_protrusion
  ].freeze

  COLUMNS = [
    'face_width',
    'jaw_width',
    'face_depth',
    'face_length',
    'lower_face_length',
    'bitragion_menton_arc',
    'bitragion_subnasale_arc',
    # "cheek_fullness",
    'nasal_root_breadth',
    'nose_protrusion',
    'nose_bridge_height',
    'lip_width',
    'head_circumference',
    'nose_breadth'
  ].freeze

  # Encrypt sensitive facial measurement data
  encrypts :face_width, :jaw_width, :face_depth, :face_length, :lower_face_length,
           :bitragion_menton_arc, :bitragion_subnasale_arc, :cheek_fullness,
           :nasal_root_breadth, :nose_protrusion, :nose_bridge_height,
           :lip_width, :head_circumference, :nose_breadth, :arkit,
           deterministic: true

  belongs_to :user

  validate :validate_arkit_structure, if: -> { arkit.present? }

  # Aggregated ARKit measurements
  def aggregated_arkit_measurements
    if arkit.blank? || !arkit.is_a?(Hash)
      return {
        nose_mm: nil,
        strap_mm: nil,
        top_cheek_mm: nil,
        mid_cheek_mm: nil,
        chin_mm: nil
      }
    end

    average_measurements = arkit['average_measurements']
    unless average_measurements.is_a?(Hash)
      return {
        nose_mm: nil,
        strap_mm: nil,
        top_cheek_mm: nil,
        mid_cheek_mm: nil,
        chin_mm: nil
      }
    end

    # Define the measurement keys for each subsection
    nose_keys = %w[
      160-371 371-367 367-387 387-14
      609-802 802-798 798-14 14-818
    ]

    strap_keys = %w[
      967-464 464-456 456-451 451-455
      999-1027 1027-884 884-883 883-879
    ]

    top_cheek_keys = %w[
      879-600 600-756 756-862 862-753 753-594 594-582 582-609
      451-151 151-321 321-434 434-318 318-145 145-133 133-160
    ]

    mid_cheek_keys = %w[
      509-893 893-894 894-881 881-880 880-879
      60-478 478-479 479-453 453-452 452-451
    ]

    chin_keys = %w[
      1049-983 983-982 982-1050 1050-1051 1051-1052 1052-1053 1053-509
      1049-984 984-985 985-986 986-987 987-988 988-989 989-60
    ]

    {
      nose_mm: sum_keys(nose_keys, average_measurements),
      strap_mm: sum_keys(strap_keys, average_measurements),
      top_cheek_mm: sum_keys(top_cheek_keys, average_measurements),
      mid_cheek_mm: sum_keys(mid_cheek_keys, average_measurements),
      chin_mm: sum_keys(chin_keys, average_measurements)
    }
  end

  def percent_complete
    aggregated = aggregated_arkit_measurements

    # Count how many of the 5 aggregated measurements are not nil
    completed_count = [
      aggregated[:nose_mm],
      aggregated[:strap_mm],
      aggregated[:top_cheek_mm],
      aggregated[:mid_cheek_mm],
      aggregated[:chin_mm]
    ].count { |value| !value.nil? }

    # Return percentage as float (0.0 to 100.0)
    (completed_count / 5.0 * 100.0).round(2)
  end

  def as_json(options = {})
    super(options).merge(
      'aggregated' => aggregated_arkit_measurements,
      'percent_complete' => percent_complete
    )
  end

  def self.latest(user)
    facial_measurements = FacialMeasurement.where(user_id: user.id).order(:created_at)

    return facial_measurements.last if facial_measurements.size.positive?

    nil
  end

  def self.missing_ratio_sql
    <<-SQL
        latest_facial_measurement_missing AS (
          SELECT *,
            CASE WHEN bitragion_subnasale_arc = 0 OR bitragion_subnasale_arc IS NULL THEN 1 ELSE 0 END AS bitragion_subnasale_arc_missing,
            CASE WHEN bitragion_menton_arc = 0 OR bitragion_menton_arc IS NULL THEN 1 ELSE 0 END AS bitragion_menton_arc_missing,
            CASE WHEN face_width = 0 OR face_width IS NULL THEN 1 ELSE 0 END AS face_width_missing,
            CASE WHEN face_length = 0 OR face_length IS NULL THEN 1 ELSE 0 END AS face_length_missing,
            CASE WHEN lower_face_length = 0 OR lower_face_length IS NULL THEN 1 ELSE 0 END AS lower_face_length_missing,
            CASE WHEN lip_width = 0 OR lip_width IS NULL THEN 1 ELSE 0 END AS lip_width_missing,
            CASE WHEN jaw_width = 0 OR jaw_width IS NULL THEN 1 ELSE 0 END AS jaw_width_missing,
            CASE WHEN nose_breadth = 0 OR nose_breadth IS NULL THEN 1 ELSE 0 END AS nose_breadth_missing,
            CASE WHEN nose_bridge_height = 0 OR nose_bridge_height IS NULL THEN 1 ELSE 0 END AS nose_bridge_height_missing,
            CASE WHEN nasal_root_breadth = 0 OR nasal_root_breadth IS NULL THEN 1 ELSE 0 END AS nasal_root_breadth_missing,
            CASE WHEN nose_protrusion = 0 OR nose_protrusion IS NULL THEN 1 ELSE 0 END AS nose_protrusion_missing,
            CASE WHEN head_circumference = 0 OR head_circumference IS NULL THEN 1 ELSE 0 END AS head_circumference_missing
          FROM latest_facial_measurements_for_users
        ), latest_facial_measurement_missing_counts AS (
          SELECT id,
            bitragion_subnasale_arc_missing +
            bitragion_menton_arc_missing +
            face_width_missing +
            face_length_missing +
            lower_face_length_missing +
            lip_width_missing +
            jaw_width_missing +
            nose_breadth_missing +
            nose_bridge_height_missing +
            nasal_root_breadth_missing +
            nose_protrusion_missing +
            head_circumference_missing AS missing_count

          FROM latest_facial_measurement_missing
        ), facial_measurement_missing_ratio AS (
          SELECT *, round(missing_count::numeric / 12, 4) AS missing_ratio
          FROM latest_facial_measurement_missing_counts
        )
    SQL
  end

  def self.arkit_percent_complete_sql
    # Check if all required keys exist for each of the 5 aggregated sections
    # For each section, check that the key exists AND has a non-null 'value' field
    # Structure: arkit->'average_measurements'->'key' gives us {"value": 3.82, "description": "..."}

    <<-SQL
        arkit_percent_complete AS (
          SELECT
            id,
            user_id,
            CASE
              WHEN arkit IS NULL OR arkit->'average_measurements' IS NULL THEN 0.0
              ELSE (
                -- Check nose section (8 keys)
                CASE WHEN
                  (arkit->'average_measurements' ? '160-371' AND
                   arkit->'average_measurements' ? '371-367' AND
                   arkit->'average_measurements' ? '367-387' AND
                   arkit->'average_measurements' ? '387-14' AND
                   arkit->'average_measurements' ? '609-802' AND
                   arkit->'average_measurements' ? '802-798' AND
                   arkit->'average_measurements' ? '798-14' AND
                   arkit->'average_measurements' ? '14-818' AND
                   (arkit->'average_measurements'->'160-371'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'371-367'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'367-387'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'387-14'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'609-802'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'802-798'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'798-14'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'14-818'->>'value') IS NOT NULL) THEN 1 ELSE 0 END +
                -- Check strap section (8 keys)
                CASE WHEN
                  (arkit->'average_measurements' ? '967-464' AND
                   arkit->'average_measurements' ? '464-456' AND
                   arkit->'average_measurements' ? '456-451' AND
                   arkit->'average_measurements' ? '451-455' AND
                   arkit->'average_measurements' ? '999-1027' AND
                   arkit->'average_measurements' ? '1027-884' AND
                   arkit->'average_measurements' ? '884-883' AND
                   arkit->'average_measurements' ? '883-879' AND
                   (arkit->'average_measurements'->'967-464'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'464-456'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'456-451'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'451-455'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'999-1027'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'1027-884'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'884-883'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'883-879'->>'value') IS NOT NULL) THEN 1 ELSE 0 END +
                -- Check top cheek section (14 keys)
                CASE WHEN
                  (arkit->'average_measurements' ? '879-600' AND
                   arkit->'average_measurements' ? '600-756' AND
                   arkit->'average_measurements' ? '756-862' AND
                   arkit->'average_measurements' ? '862-753' AND
                   arkit->'average_measurements' ? '753-594' AND
                   arkit->'average_measurements' ? '594-582' AND
                   arkit->'average_measurements' ? '582-609' AND
                   arkit->'average_measurements' ? '451-151' AND
                   arkit->'average_measurements' ? '151-321' AND
                   arkit->'average_measurements' ? '321-434' AND
                   arkit->'average_measurements' ? '434-318' AND
                   arkit->'average_measurements' ? '318-145' AND
                   arkit->'average_measurements' ? '145-133' AND
                   arkit->'average_measurements' ? '133-160' AND
                   (arkit->'average_measurements'->'879-600'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'600-756'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'756-862'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'862-753'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'753-594'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'594-582'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'582-609'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'451-151'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'151-321'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'321-434'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'434-318'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'318-145'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'145-133'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'133-160'->>'value') IS NOT NULL) THEN 1 ELSE 0 END +
                -- Check mid cheek section (10 keys)
                CASE WHEN
                  (arkit->'average_measurements' ? '509-893' AND
                   arkit->'average_measurements' ? '893-894' AND
                   arkit->'average_measurements' ? '894-881' AND
                   arkit->'average_measurements' ? '881-880' AND
                   arkit->'average_measurements' ? '880-879' AND
                   arkit->'average_measurements' ? '60-478' AND
                   arkit->'average_measurements' ? '478-479' AND
                   arkit->'average_measurements' ? '479-453' AND
                   arkit->'average_measurements' ? '453-452' AND
                   arkit->'average_measurements' ? '452-451' AND
                   (arkit->'average_measurements'->'509-893'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'893-894'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'894-881'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'881-880'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'880-879'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'60-478'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'478-479'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'479-453'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'453-452'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'452-451'->>'value') IS NOT NULL) THEN 1 ELSE 0 END +
                -- Check chin section (14 keys)
                CASE WHEN
                  (arkit->'average_measurements' ? '1049-983' AND
                   arkit->'average_measurements' ? '983-982' AND
                   arkit->'average_measurements' ? '982-1050' AND
                   arkit->'average_measurements' ? '1050-1051' AND
                   arkit->'average_measurements' ? '1051-1052' AND
                   arkit->'average_measurements' ? '1052-1053' AND
                   arkit->'average_measurements' ? '1053-509' AND
                   arkit->'average_measurements' ? '1049-984' AND
                   arkit->'average_measurements' ? '984-985' AND
                   arkit->'average_measurements' ? '985-986' AND
                   arkit->'average_measurements' ? '986-987' AND
                   arkit->'average_measurements' ? '987-988' AND
                   arkit->'average_measurements' ? '988-989' AND
                   arkit->'average_measurements' ? '989-60' AND
                   (arkit->'average_measurements'->'1049-983'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'983-982'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'982-1050'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'1050-1051'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'1051-1052'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'1052-1053'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'1053-509'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'1049-984'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'984-985'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'985-986'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'986-987'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'987-988'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'988-989'->>'value') IS NOT NULL AND
                   (arkit->'average_measurements'->'989-60'->>'value') IS NOT NULL) THEN 1 ELSE 0 END
              ) * 20.0
            END AS percent_complete
          FROM latest_facial_measurements_for_users
        )
    SQL
  end

  private

  def sum_keys(keys, data)
    total = 0.0
    found_count = 0

    keys.each do |key|
      next unless data.key?(key)

      value = data[key]
      extracted_value = extract_value(value)

      if extracted_value
        total += extracted_value
        found_count += 1
      end
    end

    # Return null if no keys were found or if some keys are missing (incomplete)
    return nil if found_count.zero? || found_count < keys.length

    total
  end

  def extract_value(value)
    return nil unless value

    # Handle direct numeric value
    return value.to_f if value.is_a?(Numeric)

    # Handle hash format: {'value' => 3.82, 'description' => '...'}
    return value['value'].to_f if value.is_a?(Hash) && value.key?('value') && value['value'].is_a?(Numeric)

    nil
  end

  def validate_arkit_structure
    # arkit must be a hash
    unless arkit.is_a?(Hash)
      errors.add(:arkit, 'must be a hash')
      return
    end

    # Must have "average_measurements" key
    unless arkit.key?('average_measurements')
      errors.add(:arkit, 'must have an "average_measurements" key')
      return
    end

    average_measurements = arkit['average_measurements']

    # "average_measurements" must be a hash
    unless average_measurements.is_a?(Hash)
      errors.add(:arkit, '"average_measurements" must be a hash')
      return
    end

    # Validate each entry in average_measurements
    average_measurements.each do |key, value|
      # Key must match pattern: digits-dash-digits (e.g., "14-818")
      unless key.is_a?(String) && key.match?(/^\d+-\d+$/)
        errors.add(
          :arkit,
          "key in average_measurements must match pattern 'digits-dash-digits' (e.g., '14-818'), got: #{key.inspect}"
        )
        next
      end

      # Value must be a hash
      unless value.is_a?(Hash)
        errors.add(
          :arkit,
          "value for key '#{key}' in average_measurements must be a hash"
        )
        next
      end

      # Must have "value" key with positive float
      unless value.key?('value')
        errors.add(
          :arkit,
          "hash for key '#{key}' in average_measurements must have 'value' key"
        )
        next
      end

      value_float = value['value']
      unless value_float.is_a?(Numeric) && value_float.to_f.positive?
        errors.add(
          :arkit,
          "value for key '#{key}' in average_measurements must be a positive float, got: #{value_float.inspect}"
        )
      end

      # Must have "description" key with string value
      unless value.key?('description')
        errors.add(
          :arkit,
          "hash for key '#{key}' in average_measurements must have 'description' key"
        )
        next
      end

      next if value['description'].is_a?(String)

      errors.add(
        :arkit,
        "description for key '#{key}' in average_measurements must be a string, got: #{value['description'].class}"
      )
    end
  end
end
