class HoodActor
  MODELS = {
    Allegro: {
      model: 'Allegro',
      how: {
        method: 'purchase',
        url: 'https://www.industrialsafetyproducts.com/allegro-saccharin-fit-test-kit-2040/'
      },
      weight: {
        'amount': 100,
        'measurement_unit': 'g',
      },
      cost: {
        'material_cost': 65,
        'labor_hours': 0
      }
    },
    DIY: {
      model: 'DIY',
      weight: {
        amount: 20,
        measurement_unit: 'g'
      },
      how: {
        'method' => 'diy',
        'url' => '',
        'notes' => "2.5 gallon Ziploc bag with a hole port for the nebulizer, reinforced with cardboard and tape."
      },
      cost: {
        'material_cost' => 0.5,
        'labor_hours' => 0.05
      }

    }
  }

  def self.preset_create(uuid:, model:, datetime: nil)
    metadata = JSON.parse(MODELS[model].to_json)

    if datetime.nil?
      datetime = DateTime.now
    end

    metadata['uuid'] = uuid

    Action.create(
      type: 'HoodAction',
      name: 'CreateHood',
      datetime: datetime,
      metadata: metadata
    )
  end

  def self.create(
    weight: nil,
    model: ,
    how:,
    cost: ,
    datetime: nil
  )
    # Parameters:
    #   model: 'Allegro Hood',
    #   weight: {
    #     amount: 1,
    #     measurement_unit: 'mg'
    #   },
    #   how: {
    #     method: 'buy' / 'diy',
    #     url: Allegro link / DIY link
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
      type: 'HoodAction',
      name: 'CreateHood',
      datetime: datetime,
      metadata: {
        'uuid' => SecureRandom.uuid,
        'model' => model,
        'how' => how,
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
      type: 'HoodAction',
      name: 'Sanitize',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'cost' => cost,
        'sanitize_notes' => sanitize_notes
      }
    )
  end

  def self.add_to_qlft_kit(uuid:, qlft_kit_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'HoodAction',
      name: 'AssociateWithQLFTKit',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'qlft_kit_id' => qlft_kit_uuid,
        'datetime' => datetime
      }
    )
  end

  def self.remove_from_qlft_kit(uuid:, qlft_kit_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'HoodAction',
      name: 'DissociateWithQLFTKit',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'qlft_kit_id' => qlft_kit_uuid,
        'datetime' => datetime
      }
    )
  end
end


