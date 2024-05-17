class EventsController < ApplicationController
  skip_forgery_protection
  # TODO: Might want to rename this to index?
  def new
    respond_to do |format|
      format.html do
        gon.GOOGLE_MAPS_API_KEY = ENV['GOOGLE_MAPS_API_KEY']
        gon.S3_HTTPS = ENV['S3_HTTPS']
      end

      format.json do
        render json: {}
      end
    end
  end

  def external_create
    api_token = params.require(:api_token)
    profile = Profile.find_by(external_api_token: api_token)

    unless profile && profile.can_post_via_external_api
      status = :unprocessable_entity
    else
      status = :ok
    end

    user = profile.user

    if status == :ok
      readings = params["_json"].map do |j|
        json = JSON.parse(j.to_json)
        json['timestamp'] = Time.at(json['timestamp'].to_i / 1000)
        json
      end

      event = Event.create(
        author_id: user.id,
        status: 'draft',
        sensor_readings: readings
      )

      unless event
        # TODO: is there a better status to signify validation error or something?
        status = :unprocessable_entity
        url = ""
      else
        url = "#{request.host_with_port}/#/events/#{event.id}/update"
      end
    end

    respond_to do |format|
      # Add CO2 stuff here
      format.json do
        render json: {
          status: status,
          url: url
        }
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

  def approve
    if !current_user or !current_user.admin?
      status = :unprocessable_entity
    else
      if Event.find(params['id']).update(approved_by_id: current_user.id)
        status = 201
      else
        status = :unprocessable_entity
      end
    end

    respond_to do |format|
      format.json do
        render json: {
        }.to_json, status: status
      end
    end
  end

  def update
    status = :unprocessable_entity

    if !current_user || (current_user.id != event_data[:author_id] && !current_user.admin?)
      status = :unprocessable_entity
    else
      event = Event.find(params[:id])
      if event.update(event_data)
        status = 200
      end
    end

    respond_to do |format|
      format.json do
        render json: {
          event: event
        }.to_json, status: status
      end
    end
  end


  def create
    if !current_user
      status = :unprocessable_entity
    else
      event = Event.create(event_data)

      if event
        status = 201
      else
        status = :unprocessable_entity
      end
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
      :initial_co2,
      :status,
      sensor_readings: [
        :co2,
        :timestamp,
        :key,
        :identifier
      ],
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
