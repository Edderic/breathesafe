class TapeMeasureActor
  def self.create(
    weight: nil,
    model: nil,
    cost: nil,
    datetime: nil
  )
    # Parameters:
    #   model: 'Allegro TapeMeasure',
    #   weight: {
    #     amount: 1,
    #     measurement_unit: 'mg'
    #   },
    #   how: {
    #     method: 'buy',
    #     url: 'https://amazon.com'
    #   },
    #   cost: {
    #     'material_cost':
    #     'time_cost':
    #   }
    #
    if datetime.nil?
      datetime = DateTime.now
    end

    if weight.nil?
      weight = {
        'amount' => 0.01,
        'measuring_unit' => 'lb'
      }
    end

    if model.nil?
      model = 'DIY'
    end

    if cost.nil?
      cost = {
        'material_cost' => 0.5,
        'labor_hours' => 0.0
      }
    end

    Action.create(
      type: 'TapeMeasureAction',
      name: 'CreateTapeMeasure',
      datetime: datetime,
      metadata: {
        'uuid' => SecureRandom.uuid,
        'model' => model,
        'weight' => weight,
        'cost' => cost,
      }
    )
  end


  def self.sanitize(
    uuid:,
    sanitize_notes: nil,
    cost: nil,
    datetime: nil
  )
    # Parameters:
    #   uuid: uuid
    #   cost: {
    #     'material_cost': 0,
    #     'time_cost': 0
    #   }
    #   volume: {
    #     amount: 1,
    #     measurement_unit: 'mL'
    #   },
    if cost.nil?
      cost = {
        'material_cost' => 0,
        'time_cost' => 0,
      }
    end

    if sanitize_notes.nil?
      sanitize_notes = "Wiped with 99.9% isopropyl alcohol"
    end

    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'TapeMeasureAction',
      name: 'Sanitize',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'cost' => cost,
        'sanitize_notes' => sanitize_notes
      }
    )
  end

  def self.add_to_facial_measurement_kit(uuid:, facial_measurement_kit_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'TapeMeasureAction',
      name: 'AssociateWithFacialMeasurementKit',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'facial_measurement_kit_id' => facial_measurement_kit_uuid,
        'datetime' => datetime
      }
    )
  end

  def self.remove_from_facial_measurement_kit(uuid:, facial_measurement_kit_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'TapeMeasureAction',
      name: 'DissociateWithFacialMeasurementKit',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'facial_measurement_kit_id' => facial_measurement_kit_uuid,
        'datetime' => datetime
      }
    )
  end
end
