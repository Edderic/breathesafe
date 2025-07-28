# frozen_string_literal: true

class UserStatusQuery
  def self.find_by_name(name:)
    JSON.parse(
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
        WITH latest_datetimes AS (
          SELECT MAX(refresh_datetime) AS latest_datetime
          FROM user_statuses
        )

        SELECT * FROM latest_datetimes
        INNER JOIN user_statuses ON user_statuses.refresh_datetime = latest_datetimes.latest_datetime
        WHERE user_statuses.first_name || ' ' || user_statuses.last_name = '#{name}'
        SQL
      ).to_json
    )
  end
end
