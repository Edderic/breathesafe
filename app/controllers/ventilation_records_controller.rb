class VentilationRecordsController < ApplicationController
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
    name = params["name"]

    if name == "test"
      respond_to do |format|
        # Add CO2 stuff here
        format.json do
          render json: {
            status: :ok,
            name: 'test_success',
            data: nil
          }
        end
      end

    elsif name == "share"
      profile = Profile.find_by(external_api_token: api_token)

      unless profile && profile.can_post_via_external_api
        status = :unprocessable_entity
      else
        status = :ok
      end

      user = profile.user

      if status == :ok
        data = params['data']

        # Adds the CO2 stuff
        readings = data["points"].map do |j|
          json = JSON.parse(j.to_json)
          json['timestamp'] = Time.at(json['timestamp'].to_i / 1000)
          json
        end

        bounds = data['bounds']

        place_data = {
          'center': {
            'lat': (bounds['ne'][1] + bounds['sw'][1]) / 2.0,
            'long': (bounds['ne'][0] + bounds['sw'][0]) / 2.0,
          },
          'types': []
        }

        if data.key?('sensor_data_from_external_api')
          sensor_data_from_external_api = data['sensor_data_from_external_api']
        else
          sensor_data_from_external_api = true
        end

        event = VentilationRecord.create(
          status: 'draft',
          sensor_data_from_external_api: sensor_data_from_external_api,
          author_id: user.id,
          maximum_occupancy: 20,
          sensor_readings: readings,
          place_data: place_data,
          room_height_meters: 2.43, # 8 ft
          room_length_meters: 8,
          room_width_meters: 5,
          room_usable_volume_factor: 0.8,
          room_usable_volume_cubic_meters: 2.43 * 8 * 5,
          ventilation_co2_ambient_ppm: 420,
          ventilation_co2_measurement_device_name: "AirCoda - External API",
          ventilation_co2_measurement_device_model: "",
          ventilation_co2_measurement_device_serial: "",
          ventilation_ach: 0.1,
          portable_ach: 0.1,
          duration: "1 hour", # do we need this
          private: "public",
          occupancy: {"parsed": {}},

          activity_groups: [
            {
              "id"=>SecureRandom.uuid, # Do we really need this?
              "sex"=>"Female", # Let's just average this out?
              "ageGroup"=>"30 to <40",
              "maskType"=>"None",
              "numberOfPeople"=>"10",
              "rapidTestResult"=>"Unknown",
              "aerosolGenerationActivity"=>"Resting – Speaking",
              "carbonDioxideGenerationActivity"=>"Sitting tasks, light effort (e.g, office work)",
            }
          ],
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
            name: "share-accepted",
            data: {
              url: url,
              event: event
            }
          }
        end
      end
    end
  end

  def index
    # TODO: if current user is nil, only show events that are public
    events = VentilationRecord.can_be_accessed_by(current_user)
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
      if VentilationRecord.find(params['id']).update(approved_by_id: current_user.id)
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
      event = VentilationRecord.find(params[:id])
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
      event = VentilationRecord.create(event_data)

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
        :identifier,
        :voc, # AirCoda
        :isOther, # AirCoda
        :latitude, # AirCoda
        :longitude, # AirCoda
        :readingAge, # AirCoda
        :sessionTag, # AirCoda
        :locationAge # AirCoda
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
