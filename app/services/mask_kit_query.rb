# frozen_string_literal: true

class MaskKitQuery
  def self.managed_by(manager_id:)
    # TODO:
    # I should be able to view my untested and tested masks.
    # - Add Shipping Status, Shipping Status Joins, Mask Kit Status for myself,
    # and others I've tseted.
    #
    # Multiple
    #
    # Sent, Untested masks
    #   use manager_id joined with the shipping status
    #
    # Not sent, Untested masks
    #   for each mask, count the number of fit tests by an individual (managed_id)
    #
    # Admin usage:
    #   On behalf of a user, (sent & untested), make changes
    #   On behalf of a user, (not sent & untested), make changes
    #
    u = User.find(manager_id)

    where_clause = "    WHERE mu.manager_id = #{manager_id.to_i}"

    where_clause = '' if u.admin?

    results = JSON.parse(
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
        WITH fit_test_counts_per_mask_user AS (
          SELECT m.id as mask_id, user_id, CASE WHEN COUNT(ft.id) IS NOT NULL THEN COUNT(ft.id) ELSE 0 END AS num_fit_tests_per_mask_user
          FROM masks m
          LEFT JOIN fit_tests ft
          ON (ft.mask_id = m.id)
          GROUP BY m.id, user_id
        ),
        #{Mask.average_filtration_efficiencies_sql}

        SELECT
          masks.*,
          avg_sealed_ffs.*,
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
        LEFT JOIN avg_sealed_ffs
          ON masks.id = avg_sealed_ffs.mask_id
        LEFT JOIN mask_kit_statuses mks
          ON mks.mask_uuid = masks.id
        LEFT JOIN shipping_status_joins ssj
          ON ssj.shippable_uuid = mks.uuid
        LEFT JOIN shipping_statuses ss
          ON ss.uuid = ssj.shipping_uuid
        LEFT JOIN users
          ON users.email = ss.to_user_uuid
        LEFT JOIN managed_users mu
          ON mu.manager_id = users.id
        LEFT JOIN profiles ON profiles.user_id = mu.managed_id
        LEFT JOIN fit_test_counts_per_mask_user ftcpmu
          ON ftcpmu.mask_id = masks.id
          AND ftcpmu.user_id = mu.managed_id


        #{where_clause}
        SQL
      ).to_json
    )

    FitTest.json_parse(
      results,
      %w[
        image_urls
        breathability
        filtration_efficiencies
        payable_datetimes
      ]
    )
  end

  def self.find_shipped_mask_accessible_to_managed_user(managed_user_id:, mask_id:)
    JSON.parse(
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
        SELECT *, mks.uuid as mask_kit_uuid
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

        WHERE masks.id = #{mask_id}
          AND mu.managed_id = #{managed_user_id}
          AND users.admin = false
        SQL
      ).to_json
    )
  end
end
