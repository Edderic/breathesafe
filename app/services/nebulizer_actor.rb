class NebulizerActor
  def self.create(
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

    if weight.nil?
      weight = {
        'amount' => 0.25,
        'measuring_unit' => 'lb'
      }
    end

    if model.nil?
      model = 'Mayluck Portable Nebulizer'
    end

    if cost.nil?
      cost = {
        'material_cost' => 38,
        'time_cost' => 0
      }
    end

    if power_supply.nil?
      # default settings for the Mesh Nebulizer
      power_supply = {
        'batteries': '2 AA',
        'batteries_present': false,
        'can_be_usb_powered': true
      }
    end

    if how.nil?
      how = {
        'method': 'buy',
        'url': 'https://www.amazon.com/dp/B0D5YR5QWZ'
      }

    end

    Action.create(
      type: 'NebulizerAction',
      name: 'CreateNebulizer',
      datetime: datetime,
      metadata: {
        'uuid' => SecureRandom.uuid,
        'model' => model,
        'how' => how,
        'weight' => weight,
        'cost' => cost,
        'power_supply' => power_supply
      }
    )
  end

  def self.add_batteries(
    uuid:,
    cost:,
    batteries: nil,
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

    Action.create(
      type: 'NebulizerAction',
      name: 'AddBatteries',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'weight' => weight,
        'cost' => cost,
        'power_supply' => {
          'batteries' => batteries
        }
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

