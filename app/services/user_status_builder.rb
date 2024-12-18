class UserStatusBuilder
  def self.build()
    actions = UserAction.all.order(:datetime)

    actions.reduce({}) do |accum, action|
      puts(action.name)
      if action.name == 'CreateUser'
        accum[action.metadata['uuid']] = {
          'high_risk' => nil,
          'studies' => {}
        }
      elsif action.name == 'MarkInterestedInStudy'
        study_name = action.metadata['study']

        studies = {
          study_name => {
            'interested_datetime' => action.datetime
          }
        }

        accum[action.metadata['uuid']]['studies'] = studies

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
        unless accum[action.metadata['uuid']]['studies'][study_name].key?('qualifications')
          accum[action.metadata['uuid']]['studies'][study_name]['qualifications'] = {}
        end

        accum[action.metadata['uuid']]['studies'][study_name]['qualifications'] = \
          accum[action.metadata['uuid']]['studies'][study_name]['qualifications'].merge(
            action.metadata['study']['qualifications']
          )
      end

      accum
    end
  end
end
