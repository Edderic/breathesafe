class Event < ApplicationRecord

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
        select distinct(events_with_state.id) as distinct_id, events_with_state.*, population_states.population, profiles.user_id, profiles.first_name, profiles.last_name, authors.admin as authored_by_admin
        from (
          select events.*, array_to_string(regexp_matches(place_data->>'formatted_address', '[A-Z]{2}'), ';') as state_short_name
          from events
        ) as events_with_state

        left join states on (states.code = events_with_state.state_short_name)
        left join population_states on (
          population_states.name = states.full_name
        )
        left join profiles on (
          events_with_state.author_id = profiles.user_id
        )
        left join users as authors on (
          events_with_state.author_id = authors.id
        )
        #{self.where_clause(user)}
      SQL
    )

    self.json_parse(events)
  end

  def self.json_parse(events)
    events.map do |ev|
      ["place_data", "activity_groups", "occupancy", "portable_air_cleaners"].each do |col|
        ev[col] = JSON.parse(ev[col])
      end

      ev
    end
  end

  def self.where_clause(current_user)
    if current_user && current_user.admin?
      ""
    elsif current_user && !current_user.admin?
      "where events_with_state.author_id = #{current_user.id} or events_with_state.private = 'public'"
    else
      # If not logged in
      # Show only those that have been authored by an admin and public
      "where events_with_state.private = 'public'"
    end
  end
end
