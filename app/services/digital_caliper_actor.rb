# frozen_string_literal: true

class DigitalCaliperActor
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
    #   model: 'iGaging 8-inch',
    #   power_supply: {
    #     'batteries': 2AA / not-applicable,
    #     'batteries_present': true / false,
    #   }
    #   weight: {
    #     amount: 1,
    #     measurement_unit: 'mg'
    #   },
    #   how: {
    #     method: 'buy',
    #     url: Allegro link / DIY link
    #   },
    #   cost: {
    #     'material_cost':
    #     'time_cost':
    #   }
    #
    datetime = DateTime.now if datetime.nil?

    uuid = SecureRandom.uuid if uuid.nil?

    if weight.nil?
      weight = {
        'amount' => 284,
        'measurement_unit' => 'g'
      }
    end

    model = 'iGaging 8-inch Digital Caliper' if model.nil?

    if cost.nil?
      cost = {
        'material_cost' => 38,
        'time_cost' => 0
      }
    end

    if power_supply.nil?
      # default settings for the Mesh DigitalCaliper
      power_supply = {
        'batteries': '1 CR2016',
        'batteries_present': true
      }
    end

    if how.nil?
      how = {
        'method': 'buy',
        'url': ''
      }

    end

    Action.create(
      type: 'DigitalCaliperAction',
      name: 'CreateDigitalCaliper',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'model' => model,
        'how' => how,
        'weight' => weight,
        'cost' => cost,
        'power_supply' => power_supply
      }
    )
  end

  def self.replace_battery(
    uuid:,
    datetime: nil
  )
    # Parameters:
    #   uuid: uuid
    #   batteries: {
    #     'batteries': 2AA / not-applicable,
    #   }
    datetime = DateTime.now if datetime.nil?

    if cost.nil?
      cost = {
        'material_cost' => 5,
        'labor_hours' => 0.02
      }
    end

    Action.create(
      type: 'DigitalCaliperAction',
      name: 'ReplaceBattery',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'cost' => cost
      }
    )
  end

  def self.mark_as_needing_battery_replacement(
    uuid:,
    datetime: nil
  )
    # Parameters:
    #   uuid: uuid
    #   batteries: {
    #     'batteries': 2AA / not-applicable,
    #   }
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'DigitalCaliperAction',
      name: 'MarkAsNeedingBatteryReplacement',
      datetime: datetime,
      metadata: {
        'uuid' => uuid
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
    #   }
    datetime = DateTime.now if datetime.nil?

    if cost.nil?
      cost = {
        'material_cost' => 2,
        'time_cost' => 0
      }
    end

    Action.create(
      type: 'DigitalCaliperAction',
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
    #   }
    datetime = DateTime.now if datetime.nil?

    if cost.nil?
      cost = {
        'material_cost' => 0,
        'time_cost' => 0
      }
    end

    Action.create(
      type: 'DigitalCaliperAction',
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
        'time_cost' => 0
      }
    end

    sanitize_notes = 'Wiped with 99.9% isopropyl alcohol' if sanitize_notes.nil?

    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'DigitalCaliperAction',
      name: 'Sanitize',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'cost' => cost,
        'sanitize_notes' => sanitize_notes
      }
    )
  end

  def self.associate_with_facial_measurement_kit(uuid:, facial_measurement_kit_uuid:, datetime: nil)
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'DigitalCaliperAction',
      name: 'AssociateWithFacialMeasurementKit',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'facial_measurement_kit_uuid' => facial_measurement_kit_uuid,
        'datetime' => datetime
      }
    )
  end

  def self.dissociate_from_facial_measurement_kit(uuid:, datetime: nil)
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'DigitalCaliperAction',
      name: 'DissociateFromFacialMeasurementKit',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'datetime' => datetime
      }
    )
  end
end
