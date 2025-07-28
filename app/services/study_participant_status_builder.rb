# frozen_string_literal: true

class StudyParticipantStatusBuilder
  def self.build(datetime: nil)
    DateTime.now if datetime.nil?

    actions = StudyParticipantAction.all.order(:datetime)
    actions.each_with_object({}) do |action, accum|
      metadata = action.metadata

      study_uuid = action.metadata['study_uuid']
      participant_uuid = action.metadata['participant_uuid']
      accum[study_uuid] = {} if accum[study_uuid].nil?

      case action.name
      when 'SetSnapshot'
        accum[study_uuid][participant_uuid] = metadata

      when 'Create'
        accum[study_uuid][participant_uuid] = {
          'interested_datetime' => nil,
          'accepted_datetime' => nil,
          'removal_from_study' => {
            'reason' => nil,
            'removal_datetime' => nil
          },
          'finished_study_datetime' => nil,
          'qualifications' => {
            'hard_to_fit_face' => nil,
            'country_of_residence' => nil
          },
          'equipment' => {
            'masks' => {
              'requested_at' => nil,
              'received_at' => nil
            },
            'facial_measurement_kit' => {
              'requested_at' => nil,
              'received_at' => nil
            },
            'qualitative_fit_testing_kit' => {
              'requested_at' => nil,
              'received_at' => nil
            },
            'money' => {
              'requested_at' => nil,
              'received_at' => nil
            }
          }
        }
      when 'MarkInterestedInStudy'
        accum[study_uuid][participant_uuid]['interested_datetime'] = action.datetime
      when 'AcceptIntoStudy'
        accum[study_uuid][participant_uuid]['accepted_datetime'] = action.datetime
      when 'RemoveFromStudy'
        accum[study_uuid][participant_uuid]['removal_from_study'] = {
          'reason' => action.metadata['reason'],
          'removal_datetime' => action.datetime
        }
      when 'FinishStudy'
        accum[study_uuid][participant_uuid]['finished_study_datetime'] = action.datetime
      when 'SetStudyQualifications'
        accum[study_uuid][participant_uuid]['qualifications'] = \
          accum[study_uuid][participant_uuid]['qualifications'].merge(metadata['qualifications'])
      when 'RequestForEquipment'
        accum[study_uuid][participant_uuid]['equipment'] =
          accum[study_uuid][participant_uuid]['equipment'].merge(action.metadata['equipment_request'])
      end
    end
  end
end
