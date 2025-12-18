# frozen_string_literal: true

# Visits
class EventsController < ApplicationController
  skip_forgery_protection
  # TODO: Might want to rename this to index?
  def new
    respond_to do |format|
      format.html do
        gon.S3_HTTPS = ENV['S3_HTTPS']
      end

      format.json do
        render json: {}
      end
    end
  end

  def external_create
    api_token = params.require(:api_token)
    name = params['name']

    if name == 'test'
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

    elsif name == 'share'
      profile = Profile.find_by(external_api_token: api_token)

      status = if profile&.can_post_via_external_api
                 :ok
               else
                 :unprocessable_entity
               end

      user = profile.user

      if status == :ok
        data = params['data']

        # Adds the CO2 stuff
        readings = data['points'].map do |j|
          json = JSON.parse(j.to_json)
          json['timestamp'] = Time.zone.at(json['timestamp'].to_i / 1000)
          json
        end

        bounds = data['bounds']

        place_data = {
          'center': {
            'lat': (bounds['ne'][1] + bounds['sw'][1]) / 2.0,
            'long': (bounds['ne'][0] + bounds['sw'][0]) / 2.0
          },
          'types': []
        }

        sensor_data_from_external_api = if data.key?('sensor_data_from_external_api')
                                          data['sensor_data_from_external_api']
                                        else
                                          true
                                        end

        event = Event.create(
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
          ventilation_co2_measurement_device_name: 'AirCoda - External API',
          ventilation_co2_measurement_device_model: '',
          ventilation_co2_measurement_device_serial: '',
          ventilation_ach: 0.1,
          portable_ach: 0.1,
          duration: '1 hour', # do we need this
          private: 'public',
          occupancy: { "parsed": {} },

          activity_groups: [
            {
              'id' => SecureRandom.uuid, # Do we really need this?
              'sex' => 'Female', # Let's just average this out?
              'ageGroup' => '30 to <40',
              'maskType' => 'None',
              'numberOfPeople' => '10',
              'rapidTestResult' => 'Unknown',
              'aerosolGenerationActivity' => 'Resting – Speaking',
              'carbonDioxideGenerationActivity' => 'Sitting tasks, light effort (e.g, office work)'
            }
          ]
        )

        if event
          url = "#{request.host_with_port}/#/events/#{event.id}/update"
        else
          # TODO: is there a better status to signify validation error or something?
          status = :unprocessable_entity
          url = ''
        end
      end

      respond_to do |format|
        # Add CO2 stuff here
        format.json do
          render json: {
            status: status,
            name: 'share-accepted',
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
    status = if !current_user || !current_user.admin?
               :unprocessable_entity
             elsif Event.find(params['id']).update(approved_by_id: current_user.id)
               201
             else
               :unprocessable_entity
             end

    respond_to do |format|
      format.json do
        render json: {}.to_json, status: status
      end
    end
  end

  def update
    status = :unprocessable_entity

    if !current_user || (current_user.id != event_data[:author_id] && !current_user.admin?)
      status = :unprocessable_entity
    else
      event = Event.find(params[:id])
      status = 200 if event.update(event_data)
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

      status = if event
                 201
               else
                 :unprocessable_entity
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
      activity_groups: %i[
        id
        aerosolGenerationActivity
        carbonDioxideGenerationActivity
        ageGroup
        maskType
        numberOfPeople
        rapidTestResult
        sex
      ],
      portable_air_cleaners: %i[
        id
        airDeliveryRateCubicMetersPerHour
        singlePassFiltrationEfficiency
        notes
      ],
      place_data: {},
      occupancy: {
        parsed: {}
      }
    )
  end
end
