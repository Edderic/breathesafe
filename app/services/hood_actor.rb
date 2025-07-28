# frozen_string_literal: true

class HoodActor
  MODELS = {
    'Allegro' => {
      'model' => 'Allegro',
      'how' => {
        'method' => 'purchase',
        'url' => 'https://www.industrialsafetyproducts.com/allegro-saccharin-fit-test-kit-2040/'
      },
      'weight' => {
        'amount' => 100,
        'measurement_unit' => 'g'
      },
      'cost' => {
        'material_cost' => 65,
        'labor_hours' => 0
      }
    },
    'DIY' => {
      'model' => 'DIY',
      'weight' => {
        'amount' => 20,
        'measurement_unit' => 'g'
      },
      'how' => {
        'method' => 'diy',
        'url' => '',
        'notes' => '2.5 gallon Ziploc bag with a hole port for the nebulizer, reinforced with cardboard and tape.'
      },
      'cost' => {
        'material_cost' => 0.5,
        'labor_hours' => 0.05
      }
    }
  }.freeze

  def self.preset_create(uuid:, model:, datetime: nil)
    metadata = JSON.parse(MODELS[model].to_json)

    datetime = DateTime.now if datetime.nil?

    metadata['uuid'] = uuid

    Action.create(
      type: 'HoodAction',
      name: 'CreateHood',
      datetime: datetime,
      metadata: metadata
    )
  end

  def self.create(
    model:, how:, cost:, weight: nil,
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
    datetime = DateTime.now if datetime.nil?

    Action.create(
      type: 'HoodAction',
      name: 'CreateHood',
      datetime: datetime,
      metadata: {
        'uuid' => SecureRandom.uuid,
        'model' => model,
        'how' => how,
        'weight' => weight,
        'cost' => cost
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
end
