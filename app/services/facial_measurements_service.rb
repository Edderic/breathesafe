# frozen_string_literal: true

# Aggregates the latest traditional and ARKit facial measurements per user.
class FacialMeasurementsService
  TRADITIONAL_FIELDS = %i[
    face_width
    face_length
    bitragion_subnasale_arc
    nose_protrusion
    nasal_root_breadth
    nose_bridge_height
  ].freeze

  EMPTY_AGGREGATED_VALUES = {
    nose_mm: nil,
    strap_mm: nil,
    top_cheek_mm: nil,
    mid_cheek_mm: nil,
    chin_mm: nil
  }.freeze

  def self.call
    new.call
  end

  def call
    traditional_measurements = latest_traditional_measurements
    arkit_measurements = latest_arkit_measurements

    user_ids = (traditional_measurements.keys + arkit_measurements.keys).uniq.sort

    user_ids.map do |user_id|
      traditional = traditional_measurements[user_id]
      arkit = arkit_measurements[user_id]
      aggregated = arkit&.aggregated_arkit_measurements || EMPTY_AGGREGATED_VALUES.dup

      {
        user_id: user_id,
        face_width: traditional&.face_width,
        face_length: traditional&.face_length,
        bitragion_subnasale_arc: traditional&.bitragion_subnasale_arc,
        nose_protrusion: traditional&.nose_protrusion,
        nasal_root_breadth: traditional&.nasal_root_breadth,
        nose_bridge_height: traditional&.nose_bridge_height,
        nose_mm: aggregated[:nose_mm],
        strap_mm: aggregated[:strap_mm],
        top_cheek_mm: aggregated[:top_cheek_mm],
        mid_cheek_mm: aggregated[:mid_cheek_mm],
        chin_mm: aggregated[:chin_mm]
      }
    end
  end

  private

  def latest_traditional_measurements
    scope = FacialMeasurement
            .select('DISTINCT ON (user_id) facial_measurements.*')
            .order('user_id, created_at DESC')

    TRADITIONAL_FIELDS.each do |field|
      scope = scope.where.not(field => nil)
    end

    scope.index_by(&:user_id)
  end

  def latest_arkit_measurements
    FacialMeasurement
      .select('DISTINCT ON (user_id) facial_measurements.*')
      .where.not(arkit: nil)
      .order('user_id, created_at DESC')
      .index_by(&:user_id)
  end
end
