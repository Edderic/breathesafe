class Event < ApplicationRecord

  def self.can_be_accessed_by(user)
    unless user
      return Event.find_by_sql(
        <<-SQL
          select * from events where private = 'public'
        SQL
      )

    end

    Event.find_by_sql(
      <<-SQL
        select * from events where author_id = #{user.id} or private = 'public'
      SQL
    )
  end
end
