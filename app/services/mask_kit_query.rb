class MaskKitQuery
  def self.managed_by(manager_id:)
    results = JSON.parse(
      ActiveRecord::Base.connection.exec_query(
        <<-SQL

        WITH fit_test_counts_per_mask_user AS (
          SELECT m.id as mask_id, user_id, CASE WHEN COUNT(ft.id) IS NOT NULL THEN COUNT(ft.id) ELSE 0 END AS num_fit_tests_per_mask_user
          FROM masks m
          LEFT JOIN fit_tests ft
          ON (ft.mask_id = m.id)
          GROUP BY m.id, user_id
        )
        SELECT masks.*,
          users.email,
          profiles.first_name,
          profiles.last_name,
          mks.uuid as mask_kit_uuid,
          managed_id,
          CASE WHEN num_fit_tests_per_mask_user IS NOT NULL THEN
            num_fit_tests_per_mask_user
          ELSE
            0
          END AS num_fit_tests_per_mask_user
        FROM masks
        INNER JOIN mask_kit_statuses mks
          ON mks.mask_uuid = masks.id
        INNER JOIN shipping_status_joins ssj
          ON ssj.shippable_uuid = mks.uuid
        INNER JOIN shipping_statuses ss
          ON ss.uuid = ssj.shipping_uuid
        INNER JOIN users
          ON users.email = ss.to_user_uuid
        INNER JOIN managed_users mu
          ON mu.manager_id = users.id
        LEFT JOIN profiles ON profiles.user_id = mu.managed_id
        LEFT JOIN fit_test_counts_per_mask_user ftcpmu
          ON ftcpmu.mask_id = masks.id
          AND ftcpmu.user_id = mu.managed_id

        WHERE mu.manager_id = #{manager_id.to_i}
        SQL
      ).to_json
    )

    FitTest.json_parse(
      results,
      [
        "image_urls",
        "breathability",
        "filtration_efficiencies",
        "payable_datetimes"
      ]
    )
  end
end