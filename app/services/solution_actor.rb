class SolutionActor
  def self.create(
    concentration_type:,
    volume:,
    how:,
    flavor_type:,
    cost:,
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
        'uuid' => SecureRandom.uuid,
        'flavor_type' => flavor_type,
        'concentration_type' => concentration_type,
        'volume' => volume,
        'how' => how,
        'cost' => cost
      }
    )
  end

  def self.set_solution_volume(volume:, uuid:, cost:nil, datetime: nil)
    # Parameters:
    #   volume: {
    #     amount: 1,
    #     measurement_unit: 'mL'
    #   },
    if cost.nil?
      cost = 0
    end

    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'SolutionAction',
      name: 'SetSolutionVolume',
      datetime: datetime,
      metadata: {
        'uuid' => uuid,
        'volume' => new_volume,
        'cost' => cost
      }
    )
  end

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
