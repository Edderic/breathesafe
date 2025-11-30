# frozen_string_literal: true

class MaskKitQuery
  def self.managed_by(manager_id:)
    start_time = Time.current
    # TODO: I should be able to view my untested and tested masks.
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
    user_find_start = Time.current
    u = User.find(manager_id)
    Rails.logger.debug "MaskKitQuery: User.find took: #{(Time.current - user_find_start) * 1000}ms"

    where_clause = "    WHERE mu.manager_id = #{manager_id.to_i}"

    where_clause = '' if u.admin?

    sql_start = Time.current
    sql_results_raw = ActiveRecord::Base.connection.exec_query(
      <<-SQL
        -- TODO: deduplicate masks before counting

        WITH fit_test_counts_per_mask_user AS (
          SELECT m.id as mask_id, user_id, CASE WHEN COUNT(ft.id) IS NOT NULL THEN COUNT(ft.id) ELSE 0 END AS num_fit_tests_per_mask_user
          FROM masks m
          LEFT JOIN fit_tests ft
          ON (ft.mask_id = m.id)
          GROUP BY m.id, user_id
        ),
        #{Mask.average_filtration_efficiencies_sql}

        SELECT
          users.email,
          profiles.first_name,
          profiles.last_name,
          managed_id
        FROM users
        LEFT JOIN managed_users mu
          ON mu.managed_id = users.id
        LEFT JOIN profiles ON profiles.user_id = mu.managed_id


        #{where_clause}
      SQL
    )
    Rails.logger.debug "MaskKitQuery: SQL query took: #{(Time.current - sql_start) * 1000}ms"

    # Convert ActiveRecord::Result to array of hashes directly (much faster than to_json + parse)
    convert_start = Time.current
    results = sql_results_raw.to_a
    Rails.logger.debug "MaskKitQuery: SQL results conversion took: #{(Time.current - convert_start) * 1000}ms, converted #{results.length} rows"

    # Decrypt the profile data for each result
    # Collect all managed_ids that need decryption
    decrypt_start = Time.current
    managed_ids_needing_decryption = results.select do |result|
      result['managed_id'] && result['first_name'].is_a?(String) && result['first_name'].start_with?('{"p":')
    end.map { |result| result['managed_id'] }.uniq
    Rails.logger.debug "MaskKitQuery: Collecting managed_ids for decryption took: #{(Time.current - decrypt_start) * 1000}ms, found #{managed_ids_needing_decryption.length} IDs"

    # Preload all profiles in a single query
    profile_load_start = Time.current
    profiles_by_user_id = Profile.where(user_id: managed_ids_needing_decryption).index_by(&:user_id)
    Rails.logger.debug "MaskKitQuery: Profile preload took: #{(Time.current - profile_load_start) * 1000}ms, loaded #{profiles_by_user_id.length} profiles"

    # Update results using preloaded profiles
    profile_update_start = Time.current
    results.each do |result|
      unless result['managed_id'] && result['first_name'].is_a?(String) && result['first_name'].start_with?('{"p":')
        next
      end

      begin
        profile = profiles_by_user_id[result['managed_id']]
        if profile
          result['first_name'] = profile.first_name
          result['last_name'] = profile.last_name
        end
      rescue StandardError => e
        Rails.logger.warn "Failed to decrypt profile data for user #{result['managed_id']}: #{e.message}"
      end
    end
    Rails.logger.debug "MaskKitQuery: Profile decryption loop took: #{(Time.current - profile_update_start) * 1000}ms, processed #{results.length} results"

    json_parse_start = Time.current
    parsed_results = FitTest.json_parse(
      results,
      %w[
        image_urls
        breathability
        filtration_efficiencies
        payable_datetimes
      ]
    )
    Rails.logger.debug "MaskKitQuery: FitTest.json_parse took: #{(Time.current - json_parse_start) * 1000}ms"
    Rails.logger.debug "MaskKitQuery.managed_by total time: #{(Time.current - start_time) * 1000}ms"

    parsed_results
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
