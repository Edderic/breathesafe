class UserStatusBuilder
  def self.build()
    actions = UserAction.all.order(:datetime)

    actions.reduce({}) do |accum, action|
      puts(action.name)
      if action.name == 'CreateUser'
        accum[action.metadata['uuid']] = {
          'high_risk' => nil,
          'studies' => {
            "Mask Recommender Based on Facial Features" => {
              'interested_datetime' => nil,
              'accepted_datetime' => nil,
              'removal_from_study' => {
                'reason' => nil,
                'removal_datetime' => nil
              },
              'qualifications' => {
                'pod_type' => nil,
                'hard_to_fit_face' => nil,
                'country_of_residence' => nil,
              },
              'equipment' => {
                'masks' => {
                  'requested_at' => nil,
                  'received_at' => nil,
                },
                'facial_measurement_kit' => {
                  'requested_at' => nil,
                  'received_at' => nil
                },
                'qualitative_fit_testing_kit' => {
                  'requested_at' => nil,
                  'received_at' => nil
                },
              }
            }
          },
          'address' => {
            'state' => nil,
            'country' => nil,
            'zip_code' => nil,
            'town_city' => nil,
            'address_line_1' => nil,
            'address_line_2' => nil,
            'address_line_3' => nil,
          },
          'address_coordinate' => nil
        }
      elsif action.name == 'MarkInterestedInStudy'
        study_name = action.metadata['study']

        accum[action.metadata['uuid']]['studies'][study_name]['interested_datetime'] = action.datetime

      elsif action.name == 'AcceptIntoStudy'
        study_name = action.metadata['study']

        accum[action.metadata['uuid']]['studies'][study_name] = accum[action.metadata['uuid']]['studies'][study_name].merge(
          {
            'accepted_datetime' => action.datetime
          }
        )
      elsif action.name == 'MarkHighRisk'
        accum[action.metadata['uuid']]['health_status'] = {
          'is_high_risk' => true,
          'is_high_risk_datetime' => action.datetime
        }
      elsif action.name == 'RemoveFromStudy'
        study_name = action.metadata['study']

        accum[action.metadata['uuid']]['studies'][study_name]['removal_from_study'] = {
          'reason' => action.metadata['reason'],
          'removal_datetime' => action.datetime
        }
      elsif action.name == 'SetStudyQualifications'
        study_name = action.metadata['study']['study_name']

        accum[action.metadata['uuid']]['studies'][study_name]['qualifications'] = \
          accum[action.metadata['uuid']]['studies'][study_name]['qualifications'].merge(
            action.metadata['study']['qualifications']
          )
      elsif action.name == 'SetAddress'
        unless accum[action.metadata['uuid']].key?('address')
          accum[action.metadata['uuid']]['address'] = {}
        end

        accum[action.metadata['uuid']]['address'] = \
          accum[action.metadata['uuid']]['address'].merge(action.metadata['address'])
        accum[action.metadata['uuid']]['address_coordinate'] = action.metadata['address_coordinate']
      elsif action.name == 'RequestForEquipment'
        study_name = action.metadata['study']['study_name']
        equipment_request = action.metadata['study']['equipment_request']

        equipment_request.each do |k, v|
          if v == true
            accum[action.metadata['uuid']]['studies'][study_name]['equipment'][k]['requested_at'] = action.datetime
          end
        end
      end

      accum
    end
  end
end
