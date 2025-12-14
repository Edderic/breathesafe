# frozen_string_literal: true

class EncryptFacialMeasurementFields < ActiveRecord::Migration[7.0]
  def up
    # Convert numeric columns to text to support encryption
    say_with_time 'Converting numeric columns to text' do
      # Integer columns
      %i[
        face_width
        jaw_width
        face_depth
        face_length
        bitragion_menton_arc
        bitragion_subnasale_arc
        nasal_root_breadth
        nose_protrusion
        nose_bridge_height
        lip_width
        head_circumference
        nose_breadth
      ].each do |column|
        add_column :facial_measurements, :"#{column}_temp", :text
        execute "UPDATE facial_measurements SET #{column}_temp = #{column}::text WHERE #{column} IS NOT NULL"
        remove_column :facial_measurements, column
        rename_column :facial_measurements, :"#{column}_temp", column
      end

      # Double precision column
      add_column :facial_measurements, :lower_face_length_temp, :text
      execute 'UPDATE facial_measurements SET lower_face_length_temp = lower_face_length::text WHERE lower_face_length IS NOT NULL'
      remove_column :facial_measurements, :lower_face_length
      rename_column :facial_measurements, :lower_face_length_temp, :lower_face_length
    end

    # Enable support for reading unencrypted data during migration
    ActiveRecord::Encryption.config.support_unencrypted_data = true

    say_with_time "Encrypting facial measurement fields for #{FacialMeasurement.count} records" do
      # Reload the FacialMeasurement model to pick up the new column types
      FacialMeasurement.reset_column_information

      # Get encryption types for each field
      field_types = {}
      %i[
        face_width
        jaw_width
        face_depth
        face_length
        lower_face_length
        bitragion_menton_arc
        bitragion_subnasale_arc
        cheek_fullness
        nasal_root_breadth
        nose_protrusion
        nose_bridge_height
        lip_width
        head_circumference
        nose_breadth
        arkit
      ].each do |field|
        field_types[field] = FacialMeasurement.type_for_attribute(field)
      end

      FacialMeasurement.find_each do |measurement|
        # Read unencrypted values
        values = {}
        field_types.each_key do |field|
          values[field] = measurement.send(field)
        end

        # Check if there's any data to encrypt
        has_data = values.values.any?(&:present?)

        next unless has_data

        # Manually encrypt each value using the type serializer
        encrypted_values = {}
        values.each do |field, value|
          encrypted_values[field] = value.present? ? field_types[field].serialize(value) : nil
        end

        # Build UPDATE SQL
        update_sql = []
        encrypted_values.each do |field, encrypted_value|
          update_sql << "#{field} = #{connection.quote(encrypted_value)}" if encrypted_value
        end

        if update_sql.any?
          connection.execute("UPDATE facial_measurements SET #{update_sql.join(', ')} WHERE id = #{measurement.id}")
        end
      end
    end

    # Disable support for unencrypted data - now all data should be encrypted
    ActiveRecord::Encryption.config.support_unencrypted_data = false
  end

  def down
    say 'Rollback: Remove encrypts declarations from FacialMeasurement model manually to read the data'
    say 'Then convert numeric columns back if needed'
  end
end
