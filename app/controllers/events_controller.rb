class EventsController < ApplicationController
  # TODO: Might want to rename this to index?
  def new
    respond_to do |format|
      format.html do
        gon.GOOGLE_MAPS_API_KEY = ENV['GOOGLE_MAPS_API_KEY']
      end

      format.json do
        render json: {
          projects: projects
        }.to_json
      end
    end
  end

  def index
    # TODO: if current user is nil, only show events that are public
    events = Event.can_be_accessed_by(current_user)

    respond_to do |format|
      format.json do
        render json: {
          events: events
        }.to_json, status: status
      end
    end
  end

  def create
    event = Event.create(event_data)

    if event
      status = 201
    else
      status = :unprocessable_entity
    end

    respond_to do |format|
      format.json do
        render json: {
          event: event
        }.to_json, status: status
      end
    end
  end

  def event_data
    params.require(:event).permit(
      :author_id,
      :room_width_meters,
      :room_height_meters,
      :room_length_meters,
      :room_usable_volume_factor,
      :room_usable_volume_cubic_meters,
      :room_name,
      :ventilation_ach,
      :portable_ach,
      :total_ach,
      :ventilation_co2_steady_state_ppm,
      :ventilation_co2_ambient_ppm,
      :ventilation_co2_measurement_device_name,
      :ventilation_co2_measurement_device_model,
      :ventilation_co2_measurement_device_serial,
      :ventilation_notes,
      :start_datetime,
      :duration,
      :private,
      :maximum_occupancy,
      activity_groups: [
        :id,
        :aerosolGenerationActivity,
        :carbonDioxideGenerationActivity,
        :ageGroup,
        :maskType,
        :numberOfPeople,
        :rapidTestResult,
        :sex
      ],
      portable_air_cleaners: [
        :id,
        :airDeliveryRateCubicMetersPerHour,
        :singlePassFiltrationEfficiency,
        :notes
      ],
      place_data: {},
      occupancy: {
        parsed: {},
      },
    )
  end
end
