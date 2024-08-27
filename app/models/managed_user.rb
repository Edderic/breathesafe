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
          ), latest_facial_measurements_for_users AS (
            SELECT fm.*
            FROM latest_facial_measurements lfm
            INNER JOIN facial_measurements fm
            ON (fm.user_id = lfm.user_id)
          )


          SELECT
            mu.*,
            p.*,
            p.id AS profile_id,
            lfmu.id AS facial_measurement_id,
            lfmu.*
          FROM managed_users mu
          INNER JOIN profiles p on (p.user_id = mu.managed_id)
          LEFT JOIN latest_facial_measurements_for_users lfmu on (lfmu.user_id = mu.managed_id)
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
          ), latest_facial_measurements_for_users AS (
            SELECT fm.* FROM latest_facial_measurements lfm
            INNER JOIN facial_measurements fm
            ON (fm.user_id = lfm.user_id)
          )


          SELECT
            mu.*,
            p.*,
            p.id AS profile_id,
            lfmu.id AS facial_measurement_id,
            lfmu.*
          FROM managed_users mu
          INNER JOIN profiles p on (p.user_id = mu.managed_id)
          LEFT JOIN latest_facial_measurements_for_users lfmu on (lfmu.user_id = mu.managed_id)
          WHERE mu.manager_id = '#{args[:manager_id]}'
            AND mu.managed_id = '#{args[:managed_id]}'
        SQL
      ).to_json
    )
  end
end
