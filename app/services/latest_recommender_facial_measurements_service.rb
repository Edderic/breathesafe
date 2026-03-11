# frozen_string_literal: true

class LatestRecommenderFacialMeasurementsService
  class Error < StandardError; end
  class ForbiddenError < Error; end
  class MissingMeasurementsError < Error; end

  EMPTY_MEASUREMENTS = FacialMeasurement::RECOMMENDER_COLUMNS.index_with { nil }.freeze

  def self.call(viewer:, recommender_user_id:)
    new(viewer:, recommender_user_id:).call
  end

  def initialize(viewer:, recommender_user_id:)
    @viewer = viewer
    @recommender_user_id = recommender_user_id
  end

  def call
    raise ForbiddenError, 'unauthorized' unless viewer

    user = User.find(recommender_user_id)
    raise ForbiddenError, 'forbidden' unless viewer.manages?(user)

    measurement = latest_usable_arkit_measurement_for(user)
    raise MissingMeasurementsError, 'No usable ARKit facial measurements found for user.' unless measurement

    normalized_recommender_measurements(measurement)
  end

  private

  attr_reader :viewer, :recommender_user_id

  def latest_usable_arkit_measurement_for(user)
    FacialMeasurement
      .where(user_id: user.id)
      .where.not(arkit: nil)
      .where.not(arkit: {})
      .order(created_at: :desc)
      .detect do |measurement|
        aggregated = normalized_recommender_measurements(measurement)
        aggregated.values.all?(&:present?)
      end
  end

  def normalized_recommender_measurements(measurement)
    return EMPTY_MEASUREMENTS.dup if measurement.nil?

    aggregated = stringify(measurement.aggregated_arkit_measurements)
    return aggregated if aggregated.values.any?(&:present?)

    arkit = measurement.arkit
    if arkit.is_a?(Hash) && arkit['averageMeasurements'].is_a?(Hash)
      normalized_arkit = arkit.deep_dup
      normalized_arkit['average_measurements'] ||= normalized_arkit['averageMeasurements']
      fallback = stringify(FacialMeasurement.new(arkit: normalized_arkit).aggregated_arkit_measurements)
      return fallback if fallback.values.any?(&:present?)
    end

    EMPTY_MEASUREMENTS.dup
  end

  def stringify(hash)
    (hash || {}).transform_keys(&:to_s)
  end
end
