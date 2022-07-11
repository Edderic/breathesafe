class Event < ApplicationRecord

  def self.can_be_accessed_by(user)
    Event.find_by_sql(
      <<-SQL
        select * from events where author_id = #{user.id} or private = 'public'
      SQL
    )
  end
end
