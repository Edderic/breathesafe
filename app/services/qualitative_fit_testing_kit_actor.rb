class QualitativeFitTestingKitActor
  def self.preset_diy_create(datetime: nil)
    ActiveRecord::Base.transaction do
      if datetime.nil?
        datetime = DateTime.now
      end

      kit_uuid = SecureRandom.uuid
      self.create(uuid: kit_uuid, datetime: datetime)

      nebulizer_uuid = SecureRandom.uuid
      NebulizerActor.preset_create(
        model: "Mayluck Portable Nebulizer",
        uuid: nebulizer_uuid,
        datetime: datetime + 1.second
      )

      hood_uuid = SecureRandom.uuid
      HoodActor.preset_create(
        uuid: hood_uuid,
        model: :DIY,
        datetime: datetime + 1.second
      )

      fit_test_solution_uuid = SecureRandom.uuid
      SolutionActor.preset_create(
        uuid: fit_test_solution_uuid,
        model: 'DIY',
        flavor_type: 'saccharin',
        concentration_type: 'fit_test',
        datetime: datetime + 1.second
      )

      sensitivity_solution_uuid = SecureRandom.uuid
      SolutionActor.preset_create(
        uuid: sensitivity_solution_uuid,
        model: 'DIY',
        flavor_type: 'saccharin',
        concentration_type: 'sensitivity',
        datetime: datetime + 1.second
      )


      solution_uuids = [fit_test_solution_uuid, sensitivity_solution_uuid]

      solution_uuids.each do |solution_uuid|
        self.add_solution(
          uuid: kit_uuid,
          solution_uuid: solution_uuid,
          datetime: datetime + 1.second
        )
      end

      # Associate those parts with the qualitative fit testing kit

      self.add_hood(
        uuid: kit_uuid,
        hood_uuid: hood_uuid,
        datetime: datetime + 1.second
      )

      self.add_nebulizer(
        uuid: kit_uuid,
        nebulizer_uuid: nebulizer_uuid,
        datetime: datetime + 1.second
      )

    end
  end

  def self.create(
    uuid:,
    datetime: nil
  )
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'QualitativeFitTestingKitAction',
      name: 'Create',
      datetime: datetime,
      metadata: {
        'uuid': uuid
      }
    )
  end

  def self.add_solution(uuid:, solution_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end
    Action.create(
      type: 'QualitativeFitTestingKitAction',
      name: 'AddSolution',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'solution_uuid': solution_uuid
      }
    )
  end

  def self.remove_solution(uuid:, solution_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'QualitativeFitTestingKitAction',
      name: 'RemoveSolution',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'solution_uuid': solution_uuid
      }
    )
  end


  def self.add_nebulizer(uuid:, nebulizer_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'QualitativeFitTestingKitAction',
      name: 'AddNebulizer',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'nebulizer_uuid': nebulizer_uuid
      }
    )
  end

  def self.remove_nebulizer(uuid:, nebulizer_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'QualitativeFitTestingKitAction',
      name: 'RemoveNebulizer',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'nebulizer_uuid': nebulizer_uuid
      }
    )
  end

  def self.add_hood(uuid:, hood_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'QualitativeFitTestingKitAction',
      name: 'AddHood',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'hood_uuid': hood_uuid
      }
    )
  end

  def self.remove_hood(uuid:, hood_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'QualitativeFitTestingKitAction',
      name: 'RemoveHood',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'hood_uuid': hood_uuid
      }
    )
  end

  def self.set_address(uuid:, address_uuid:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    Action.create(
      type: 'QualitativeFitTestingKitAction',
      name: 'SetAddress',
      datetime: datetime,
      metadata: {
        'uuid': uuid,
        'address_uuid': address_uuid
      }
    )
  end
end
