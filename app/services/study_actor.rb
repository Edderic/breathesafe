# frozen_string_literal: true

class StudyActor
  def self.create(uuid:, name:, datetime: nil)
    datetime = DateTime.now if datetime.nil?

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
