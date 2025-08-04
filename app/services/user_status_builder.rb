# frozen_string_literal: true

class UserStatusBuilder
  def self.build
    actions = UserAction.all.order(:datetime)

    actions.each_with_object({}) do |action, accum|
      Rails.logger.debug(action.name)
      case action.name
      when 'CreateUser'
        accum[action.metadata['uuid']] = {
          'high_risk' => nil,
          'studies' => {},
          'address_uuid' => nil
        }
      when 'SetName'
        accum[action.metadata['uuid']]['first_name'] = action.metadata['first_name']
        accum[action.metadata['uuid']]['last_name'] = action.metadata['last_name']
      when 'AcceptIntoStudy'
        study_name = action.metadata['study']

        accum[action.metadata['uuid']]['studies'][study_name] = accum[action.metadata['uuid']]['studies'][study_name].merge(
          {
            'accepted_datetime' => action.datetime
          }
        )
      when 'MarkHighRisk'
        accum[action.metadata['uuid']]['health_status'] = {
          'is_high_risk' => true,
          'is_high_risk_datetime' => action.datetime
        }
      when 'SetAddress'
        accum[action.metadata['uuid']]['address_uuid'] = action.metadata['address_uuid']
      when 'RequestForEquipment'
        study_name = action.metadata['study']['study_name']
        equipment_request = action.metadata['study']['equipment_request']

        equipment_request.each_key do |k|
          accum[action.metadata['uuid']]['studies'][study_name]['equipment'][k]['requested_at'] = action.datetime
        end
      end
    end
  end
end
