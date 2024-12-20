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
          'address_uuid' => nil
        }
      elsif action.name == 'SetName'
        accum[action.metadata['uuid']]['first_name'] = action.metadata['first_name']
        accum[action.metadata['uuid']]['last_name'] = action.metadata['last_name']
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
        accum[action.metadata['uuid']]['address_uuid'] = action.metadata['address_uuid']
      elsif action.name == 'RequestForEquipment'
        study_name = action.metadata['study']['study_name']
        equipment_request = action.metadata['study']['equipment_request']

        equipment_request.each do |k, v|
          accum[action.metadata['uuid']]['studies'][study_name]['equipment'][k]['requested_at'] = action.datetime
        end
      end

      accum
    end
  end
end
