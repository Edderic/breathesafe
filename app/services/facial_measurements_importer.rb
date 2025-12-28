# frozen_string_literal: true

# Import facial measurements from CSV string
# Usage:
# csv_string = File.read('/path/to/file.csv')
# importer = FacialMeasurementsImporter.new(
#   csv_string: csv_string,
#   manager_email: 'manager@example.com',
#   source: 'wcft'
# )
# importer.import

require 'csv'
require 'date'

class FacialMeasurementsImporter
  attr_reader :manager, :csv_string, :source

  def initialize(csv_string:, manager_email:, source:)
    @csv_string = csv_string
    @source = source
    @manager = User.find_by(email: manager_email)
    @stats = {
      total_rows: 0,
      created: 0,
      updated: 0,
      skipped: 0,
      errors: []
    }
  end

  def import
    unless @manager
      Rails.logger.debug 'ERROR: Manager user not found'
      return
    end

    Rails.logger.debug 'Starting import...'
    Rails.logger.debug "Manager: #{@manager.email} (ID: #{@manager.id})"
    Rails.logger.debug "Source: #{@source}"
    Rails.logger.debug '-' * 80

    csv = CSV.parse(@csv_string, headers: true, header_converters: :symbol)

    # Debug: Show available columns
    if csv.first
      Rails.logger.debug "Available columns: #{csv.first.headers.inspect}"
      Rails.logger.debug '-' * 80
    end

    csv.each do |row|
      @stats[:total_rows] += 1
      process_row(row)
    end

    print_summary
  end

  private

  def process_row(row)
    anonymous_first_name = row[:anonymous_first_name]&.strip

    if anonymous_first_name.blank?
      @stats[:skipped] += 1
      @stats[:errors] << "Row #{@stats[:total_rows]}: Missing anonymous_first_name"
      return
    end

    # Skip example row
    if anonymous_first_name == 'EXAMPLE'
      @stats[:skipped] += 1
      Rails.logger.debug '⊘ Skipped example row'
      return
    end

    # Find the managed user by UUID (stored in first_name)
    managed_user = find_managed_user(anonymous_first_name)

    unless managed_user
      @stats[:skipped] += 1
      @stats[:errors] << "Row #{@stats[:total_rows]}: No managed user found with first_name '#{anonymous_first_name}'"
      return
    end

    # Parse the date (use current time if missing)
    date = parse_date(row[:date]) || Time.current

    # Prepare facial measurement data
    facial_data = {
      user_id: managed_user.managed_id,
      source: @source,
      face_width: row[:face_width_mm]&.to_f,
      face_length: row[:face_length_mm]&.to_f,
      nose_bridge_height: row[:nose_bridge_height_mm]&.to_f,
      nasal_root_breadth: row[:nasal_root_breadth_mm]&.to_f,
      nose_protrusion: row[:nose_protrusion_mm]&.to_f,
      bitragion_subnasale_arc: row[:bitragion_subnasale_arc_mm]&.to_f,
      created_at: date,
      updated_at: date
    }

    # Find existing facial measurement for this user
    existing_measurement = FacialMeasurement.where(user_id: managed_user.managed_id)
                                            .order(created_at: :desc)
                                            .first

    if existing_measurement
      # Update existing measurement
      if existing_measurement.update(facial_data)
        @stats[:updated] += 1
        Rails.logger.debug "✓ Updated facial measurement for user: #{anonymous_first_name} (ID: #{managed_user.managed_id})"
      else
        @stats[:errors] << "Row #{@stats[:total_rows]}: Failed to update - #{existing_measurement.errors.full_messages.join(', ')}"
        @stats[:skipped] += 1
      end
    else
      # Create new measurement
      facial_measurement = FacialMeasurement.new(facial_data)
      if facial_measurement.save
        @stats[:created] += 1
        Rails.logger.debug "✓ Created facial measurement for user: #{anonymous_first_name} (ID: #{managed_user.managed_id})"
      else
        @stats[:errors] << "Row #{@stats[:total_rows]}: Failed to create - #{facial_measurement.errors.full_messages.join(', ')}"
        @stats[:skipped] += 1
      end
    end
  rescue StandardError => e
    @stats[:skipped] += 1
    @stats[:errors] << "Row #{@stats[:total_rows]}: Exception - #{e.message}"
    Rails.logger.debug "✗ Error processing row #{@stats[:total_rows]}: #{e.message}"
  end

  def find_managed_user(anonymous_first_name)
    # Find managed user where the profile's first_name matches the UUID
    ManagedUser.joins(managed: :profile)
               .where(manager_id: @manager.id)
               .where(profiles: { first_name: anonymous_first_name })
               .first
  end

  def parse_date(date_string)
    return nil if date_string.blank?

    date_string = date_string.strip

    # Try format: 2025-04-18 (YYYY-MM-DD)
    begin
      return Date.parse(date_string)
    rescue ArgumentError
      # Continue to next format
    end

    # Try format: 09/14/25 (MM/DD/YY)
    begin
      return Date.strptime(date_string, '%m/%d/%y')
    rescue ArgumentError
      # Continue to next format
    end

    # Try format: 05/24/25 (MM/DD/YY)
    begin
      Date.strptime(date_string, '%m/%d/%y')
    rescue ArgumentError
      nil
    end
  end

  def print_summary
    Rails.logger.debug '-' * 80
    Rails.logger.debug 'Import Summary:'
    Rails.logger.debug "  Total rows processed: #{@stats[:total_rows]}"
    Rails.logger.debug "  Created: #{@stats[:created]}"
    Rails.logger.debug "  Updated: #{@stats[:updated]}"
    Rails.logger.debug "  Skipped: #{@stats[:skipped]}"
    Rails.logger.debug ''

    if @stats[:errors].any?
      Rails.logger.debug 'Errors:'
      @stats[:errors].each do |error|
        Rails.logger.debug "  - #{error}"
      end
    else
      Rails.logger.debug 'No errors!'
    end
    Rails.logger.debug '-' * 80
  end
end
