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
        select events_with_state.*, num_cases_last_seven_days, population_states.population, num_cases_last_seven_days::float / population_states.population as naive_prevalence from (
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
        #{self.query_for_user(user)}
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

  def self.query_for_user(user)
    if user
      "where events_with_state.author_id = #{user.id} or private = 'public'"
    else
      "where events_with_state.private = 'public'"
    end
  end
end
