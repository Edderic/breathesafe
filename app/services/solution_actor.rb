#
# 1 gallon = 3785.41 mL
# 100 mL
#
# Cost of distilled water: $1.50 / 1 gallon
#
# $1.50 / gallon * 1 gallon / 3785.41 mL * 100 mL = $0.039
# So the cost of water to generate sensitivity solution is about 4 cents
#
class SolutionActor
  def self.create_default_sensitivity_solution(
    uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    self.create_default_solution(
        uuid: uuid,
        concentration_type: 'sensitivity',
        cost: {
          'material_cost': 0.04,
          'time_cost': {
                'amount': 1,
                'measurement_unit': 'minute'
           }
        },
        datetime: datetime
    )
  end

  def self.create_default_fit_test_solution(
    uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    self.create_default_solution(
        uuid: uuid,
        concentration_type: 'fit test',
        cost: {
          'material_cost': 4,
          'time_cost': {
                'amount': 2,
                'measurement_unit': 'minutes'
           }
        },
        datetime: datetime
    )
  end

  def self.create_default_solution(
    uuid:,
    concentration_type:,
    cost:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    self.create(
        uuid: uuid,
        concentration_type: concentration_type,
        volume_level_proportion: 1,
        volume: {
            amount: 100,
            measurement_units: 'mL'
        },
        how: {
            method: 'DIY',
            url: 'https://ph.health.mil/PHC%20Resource%20Library/cv19-do-it-yourself-respiratory-fit-testing.pdf'
        },
        cost: cost,
        flavor_type: 'saccharin',
        datetime: datetime
    )
  end

  def self.create_allegro_fit_test_solution(
    uuid:,
    datetime: nil,
    how: nil,
    flavor_type: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    if flavor_type.nil?
      flavor_type = 'saccharin'
    end

    if how.nil?
      how = {
            method: 'purchase',
            url: 'https://www.industrialsafetyproducts.com/allegro-2040-12k-sweet-saccharin-test-solution-only-6-box/'
        }

    end

    self.create(
        uuid: uuid,
        concentration_type: 'fit test',
        volume_level_proportion: 1,
        volume: {
            amount: 15,
            measurement_units: 'mL'
        },
        how: how,
        cost: {
          'material_cost': 20.99,
          'time_cost': {
                'amount': 0,
                'measurement_unit': 'minutes'
           }
        },
        flavor_type: flavor_type,
        datetime: datetime
    )
  end

  def self.create_allegro_sensitivity_solution(
    uuid:,
    datetime: nil,
    flavor_type: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    if flavor_type.nil?
      flavor_type = 'saccharin'
    end

    self.create(
        uuid: uuid,
        concentration_type: 'sensitivity',
        volume_level_proportion: 1,
        volume: {
            amount: 15,
            measurement_units: 'mL'
        },
        how: {
            method: 'purchase',
            url: 'https://www.industrialsafetyproducts.com/allegro-2040-saccharin-fit-test-kit/'
        },
        cost: {
          'material_cost': 22.29,
          'time_cost': {
                'amount': 0,
                'measurement_unit': 'minutes'
           }
        },
        flavor_type: flavor_type,
        datetime: datetime
    )
  end

  def self.create(
    uuid: ,
    concentration_type:,
    volume:,
    how:,
    flavor_type:,
    cost:,
    volume_level_proportion:nil,
    datetime: nil
  )
    # Parameters:
    #   concentration_type: 'fit_test' or 'sensitivity'
    #   volume: {
    #     amount: 1,
    #     measurement: 'mL'
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
      type: 'SolutionAction',
      name: 'CreateSolution',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'flavor_type' => flavor_type,
        'concentration_type' => concentration_type,
        'volume' => volume,
        'volume_level_proportion' => volume_level_proportion,
        'how' => how,
        'cost' => cost
      }
    )
  end

  def self.estimate_volume(volume_level_proportion:, uuid:, datetime: nil)
    # Parameters:
    #   volume_level_proportion: {
    #     amount: 1,
    #     measurement_unit: 'mL'
    #   },
    #   uuid: uuid
    #   datetime: Defaults to nil
    #     if nil, gets DateTime.now
    if cost.nil?
      cost = 0
    end

    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'SolutionAction',
      name: 'EstimateVolume',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'volume_level_proportion' => volume_level_proportion,
      }
    )
  end

  # TODO: Use the one in QualitativeFitTestingKitActor
  def self.add_to_qlft_kit(uuid:, qlft_kit_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'SolutionAction',
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
