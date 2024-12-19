class QualitativeFitTestingKitActor
  def self.create(
    uuid:
    datetime: nil,
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


  def self.add_nebulizer(uuid:, nebulizer_uuid:,, datetime: nil)
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

  def self.add_hood(uuid:, nebulizer_uuid:,, datetime: nil)
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
