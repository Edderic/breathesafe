class NebulizerActor
  MODELS = {
    "Mayluck Portable Nebulizer" => {
      'model' => "Mayluck Portable Nebulizer",
      'weight' => {
        'amount' => 286,
        'measurement_unit' => 'g'
      },
      'cost' => {
        'material_cost' => 38,
        'time_cost' => 0
      },

      'power_supply' => {
        'batteries' => '2 AA',
        'batteries_present' => false,
        'can_be_usb_powered' => true
      },
      'batteries' => [],
      'how' => {
        'method' => 'buy',
        'url' => 'https://www.amazon.com/dp/B0D5YR5QWZ'
      }
    },
    "Allegro" => {
      'model' => "Allegro",
      'weight' => {
        'amount' => 74,
        'measurement_unit' => 'g'
      },
      'cost' => {
        'material_cost' => 43, # 170 - 40 (cost of fit test + sensitivity)
        'time_cost' => 0
      },
      'batteries' => [],

      'power_supply' => {
        'batteries' => 'N/A',
        'batteries_present' => false,
        'can_be_usb_powered' => true
      },
      'how' => {
        'method' => 'buy',
        'url' => 'https://www.amazon.com/dp/B0D5YR5QWZ'
      }

    }
  }
  def self.preset_create(
    uuid:,
    model:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    metadata = JSON.parse(MODELS[model].to_json)
    metadata['uuid'] = uuid

    Action.create(
      type: 'NebulizerAction',
      name: 'CreateNebulizer',
      datetime: datetime,
      metadata: metadata
    )
  end

  def self.create(
    uuid: nil,
    weight: nil,
    model: nil,
    how: nil,
    power_supply: nil,
    cost: nil,
    datetime: nil
  )
    # Parameters:
    #   model: 'Mayluck Portable Nebulizer',
    #   power_supply: {
    #     'batteries': 2AA / not-applicable,
    #     'batteries_present': true / false,
    #     'can_be_usb_powered': true / false
    #   }
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

    if uuid.nil?
      uuid = SecureRandom.UUID
    end

    Action.create(
      type: 'NebulizerAction',
      name: 'CreateNebulizer',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'model' => model,
        'how' => how,
        'weight' => weight,
        'cost' => cost,
        'power_supply' => power_supply,
        'batteries' => [],
        'sanitization' => []
      }
    )
  end

  def self.add_batteries(
    uuid:,
    cost: nil,
    weight: nil,
    amount: nil,
    datetime: nil
  )
    # Parameters:
    #   uuid: uuid
    #   batteries: {
    #     'batteries': 2AA / not-applicable,
    #     'batteries_present': true / false,
    #     'can_be_usb_powered': true / false
    #   }
    if datetime.nil?
      datetime = DateTime.now
    end

    if cost.nil?
      cost = {
        'material_cost' => 2,
        'time_cost' => 0
      }
    end

    if amount.nil?
      amount = {
        'quantity' => 2,
        'type' => 'AA',
      }

    end

    Action.create(
      type: 'NebulizerAction',
      name: 'AddBatteries',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'weight' => weight,
        'amount' => amount,
        'cost' => cost,
      }
    )
  end

  def self.remove_batteries(
    uuid:,
    cost:,
    batteries: nil,
    datetime: nil
  )
    # Parameters:
    #   uuid: uuid
    #   cost: {
    #     'material_cost': 0,
    #     'time_cost': 0
    #   }
    #   batteries: {
    #     'batteries': 2AA / not-applicable,
    #     'batteries_present': true / false,
    #     'can_be_usb_powered': true / false
    #   }
    if datetime.nil?
      datetime = DateTime.now
    end

    if cost.nil?
      cost = {
        'material_cost' => 0,
        'time_cost' => 0
      }
    end

    Action.create(
      type: 'NebulizerAction',
      name: 'RemoveBatteries',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'weight' => weight,
        'cost' => cost,
        'power_supply' => {
          'batteries' => {
            'batteries_present' => false
          }
        }
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
      type: 'NebulizerAction',
      name: 'Sanitize',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'cost' => cost,
        'sanitize_notes' => sanitize_notes
      }
    )
  end

  # TODO: replace because similar functionality exists
  def self.add_to_qlft_kit(uuid:, qlft_kit_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'NebulizerAction',
      name: 'AssociateWithQLFTKit',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'qlft_kit_id' => qlft_kit_uuid,
        'datetime' => datetime
      }
    )
  end

  # TODO: replace because similar functionality exists
  def self.remove_from_qlft_kit(uuid:, qlft_kit_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'NebulizerAction',
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

