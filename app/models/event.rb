class Event < ApplicationRecord
  belongs_to :author, class_name: 'User'

  def self.can_be_accessed_by(user)
    # unless user
      # return Event.find_by_sql(
        # <<-SQL
          # select * from events where private = 'public'
        # SQL
      # )
#
    # end
    events = Event.connection.exec_query(
      <<-SQL
        select distinct(events.id) as distinct_id, events.*, profiles.user_id, profiles.first_name, profiles.last_name, authors.admin as authored_by_admin
        from events

        left join profiles on (
          events.author_id = profiles.user_id
        )
        left join users as authors on (
          events.author_id = authors.id
        )
        #{self.where_clause(user)}
      SQL
    )

    self.json_parse(events)
  end

  def self.json_parse(events)
    events.map do |ev|
      ["co2_readings", "place_data", "activity_groups", "occupancy", "portable_air_cleaners"].each do |col|
        unless ev[col]
          ev[col] = []
        else
          ev[col] = JSON.parse(ev[col])
        end
      end

      ev
    end
  end

  def self.where_clause(current_user)
    if current_user && current_user.admin?
      ""
    elsif current_user && !current_user.admin?
      "where events.author_id = #{current_user.id} or events.private = 'public'"
    else
      # If not logged in
      # Show only those that have been authored by an admin and public
      "where events.private = 'public'"
    end
  end
end
