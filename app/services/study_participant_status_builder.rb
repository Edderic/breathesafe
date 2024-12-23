class StudyParticipantStatusBuilder
  def self.build(datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    actions = StudyParticipantAction.all.order(:datetime)
    actions.reduce({}) do |accum, action|
      metadata = action.metadata

      study_uuid = action.metadata['study_uuid']
      participant_uuid = action.metadata['participant_uuid']

      if action.name == 'Create'
        accum[study_uuid] = {}
        accum[study_uuid][participant_uuid] =
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


      elsif action.name == 'MarkInterestedInStudy'
        accum[study_uuid][participant_uuid]['interested_datetime'] = action.datetime
      elsif action.name == 'AcceptIntoStudy'
        accum[study_uuid][participant_uuid]['accepted_datetime'] = action.datetime
      elsif action.name == 'RemoveFromStudy'
        accum[study_uuid][participant_uuid]['removal_from_study'] = {
          'reason' => action.metadata['reason'],
          'removal_datetime' => action.datetime
        }
      elsif action.name == 'SetStudyQualifications'
        accum[study_uuid][participant_uuid]['qualifications'] = \
          accum[study_uuid][participant_uuid]['qualifications'].merge(metadata[qualifications])
      elsif action.name == 'RequestForEquipment'
        equipment_request = action.metadata['equipment_request']

        equipment_request.each do |k, v|
          accum[study_uuid][participant_uuid]['equipment'][k]['requested_at'] = action.datetime
        end
      end
    end
  end
end