class TapeMeasureActor
  def self.create(
    uuid:,
    weight: {
        'amount' => 17.2,
        'measurement_unit' => 'g'
    },
    model: 'Perfect Measuring Tape',
    cost: {
      'material_cost' => 1.49,
      'labor_hours' => 0.0
    },
    purchase_link: 'https://www.amazon.com/gp/product/B085KGFL1G/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1',
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

    Action.create(
      type: 'TapeMeasureAction',
      name: 'CreateTapeMeasure',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
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

  def self.associate_with_facial_measurement_kit(
    uuid:,
    facial_measurement_kit_uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'TapeMeasureAction',
      name: 'AssociateWithFacialMeasurementKit',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'facial_measurement_kit_uuid' => facial_measurement_kit_uuid
      }
    )
  end

  def self.dissociate_from_facial_measurement_kit(uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'TapeMeasureAction',
      name: 'DissociateWithFacialMeasurementKit',
      datetime: datetime,
      metadata: {
        'uuid' => uuid
      }
    )
  end
end
