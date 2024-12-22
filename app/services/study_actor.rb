class StudyActor
  def self.create(uuid:, name:, datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    StudyAction.create(
      name: 'Create',
      datetime: datetime,
      metadata: {
        uuid: uuid,
        name: name
      }
    )
  end
end
