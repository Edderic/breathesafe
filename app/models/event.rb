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
        select events_with_state.*, num_cases_last_seven_days, population_states.population, num_cases_last_seven_days::float / population_states.population as naive_prevalence, profiles.user_id, profiles.first_name, profiles.last_name, authors.admin as authored_by_admin
        from (
          select events.*, array_to_string(regexp_matches(place_data->>'formatted_address', '[A-Z]{2}'), ';') as state_short_name
          from events
        ) as events_with_state

        left join states on (states.code = events_with_state.state_short_name)
        left join (
          select (curr_cum - prev_cum) as num_cases_last_seven_days, state from
            (
              select blah.date as curr_date, blah.state, blah.cases_cumulative as curr_cum, bleh.cases_cumulative as prev_cum, bleh.date as seven_days_ago_date from (
                select date, cases_cumulative, state
                from covid_states
                where date = '#{Date.today - 1.day}'
              ) as blah
              inner join (
                select date, to_date('#{Date.today - 1.day}', 'YYYY-MM-DD') as recent_date,  state, cases_cumulative from covid_states where date = '#{Date.today - 8.day}'
              ) as bleh on (
                blah.date = bleh.recent_date
                and blah.state = bleh.state
              )
           ) as cases
        ) as cases_2 on (cases_2.state = states.full_name)
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
      # Only show if the current user is the author OR
      # Event has been approved by an admin and the privacy setting is set to public
      # Or the author is an admin
      "where events_with_state.author_id = #{current_user.id} or (events_with_state.approved_by_id is not null or authors.admin = true) and events_with_state.private = 'public'"
    else
      # If not logged in
      # Show only those that have been approved by an admin and public
      # OR Show only those that have been authored by an admin and public
      "where (events_with_state.approved_by_id is not null or authors.admin = true) and events_with_state.private = 'public'"
    end
  end
end
