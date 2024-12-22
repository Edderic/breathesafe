class UserStatusBuilder
  def self.build()
    actions = UserAction.all.order(:datetime)

    actions.reduce({}) do |accum, action|
      puts(action.name)
      if action.name == 'CreateUser'
        accum[action.metadata['uuid']] = {
          'high_risk' => nil,
          'studies' => {
          },
          'address_uuid' => nil
        }
      elsif action.name == 'SetName'
        accum[action.metadata['uuid']]['first_name'] = action.metadata['first_name']
        accum[action.metadata['uuid']]['last_name'] = action.metadata['last_name']
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
