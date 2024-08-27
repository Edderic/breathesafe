class ManagedUser < ApplicationRecord
  belongs_to :manager, foreign_key: 'manager_id', class_name: 'User'
  belongs_to :managed, foreign_key: 'managed_id', class_name: 'User'

  def self.for_manager_id(args)

    JSON.parse(
      ManagedUser.connection.exec_query(
        <<-SQL
          WITH latest_facial_measurements AS (
            SELECT user_id, MAX(created_at) latest_created_at
            FROM facial_measurements
            GROUP BY user_id
          )

          SELECT
            mu.*,
            p.*,
            p.id AS profile_id,
            fm.id AS facial_measurement_id,
            lfm.*
          FROM managed_users mu
          INNER JOIN profiles p on (p.user_id = mu.managed_id)
          LEFT JOIN facial_measurements fm on (fm.user_id = mu.managed_id)
          LEFT JOIN latest_facial_measurements lfm on (lfm.user_id = mu.managed_id AND lfm.latest_created_at = fm.created_at)
          WHERE mu.manager_id = '#{args[:manager_id]}'
        SQL
      ).to_json
    )
  end

  def self.for_manager_and_managed(args)
    JSON.parse(
      ManagedUser.connection.exec_query(
        <<-SQL
          WITH latest_facial_measurements AS (
            SELECT user_id, MAX(created_at) latest_created_at
            FROM facial_measurements
            GROUP BY user_id
          )

          SELECT
            mu.*,
            p.*,
            p.id AS profile_id,
            lfm.id AS facial_measurement_id,
            lfm.*

          FROM managed_users mu
          INNER JOIN profiles p on (p.user_id = mu.managed_id)
          LEFT JOIN facial_measurements fm on (fm.user_id = mu.managed_id)
          LEFT JOIN latest_facial_measurements lfm on (lfm.user_id = mu.managed_id AND lfm.latest_created_at = fm.created_at)
          WHERE mu.manager_id = '#{args[:manager_id]}'
            AND mu.managed_id = '#{args[:managed_id]}'
        SQL
      ).to_json
    )
  end
end
