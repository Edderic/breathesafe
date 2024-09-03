class MeasurementDevice < ApplicationRecord
  belongs_to :owner, foreign_key: 'owner_id', class_name: 'User'

  def self.viewable(user, id=nil)
    if id
      where_clause = "WHERE measurement_devices.id = #{id}"
    end

    MeasurementDevice.connection.exec_query(
      <<-SQL
        WITH measurement_device_fit_test_counts AS (
          SELECT md.id, COUNT(ft.id) as num_fit_tests
          FROM measurement_devices md
          LEFT JOIN fit_tests ft
            ON (ft.quantitative_fit_testing_device_id = ft.id)
          WHERE owner_id = #{user.id}
          GROUP BY md.id
        )

        SELECT measurement_devices.*, num_fit_tests
        FROM measurement_device_fit_test_counts
        INNER JOIN measurement_devices
          ON (measurement_devices.id = measurement_device_fit_test_counts.id )
        #{where_clause}
      SQL
    )
  end
end
