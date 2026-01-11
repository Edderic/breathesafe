# frozen_string_literal: true

# Mask model
class Mask < ApplicationRecord
  # Privacy threshold for demographic counts
  DEMOGRAPHIC_PRIVACY_THRESHOLD = 5

  belongs_to :author, class_name: 'User'
  belongs_to :brand, optional: true
  belongs_to :bulk_fit_tests_import, optional: true
  belongs_to :duplicate_of_mask, class_name: 'Mask', foreign_key: 'duplicate_of',
                                 optional: true, inverse_of: :duplicate_masks
  has_many :duplicate_masks, class_name: 'Mask', foreign_key: 'duplicate_of',
                             dependent: :nullify, inverse_of: :duplicate_of_mask
  has_many :mask_pairs_as_a, class_name: 'MaskPair', foreign_key: 'mask_a_id',
                             dependent: :restrict_with_exception, inverse_of: :mask_a
  has_many :mask_pairs_as_b, class_name: 'MaskPair', foreign_key: 'mask_b_id',
                             dependent: :restrict_with_exception, inverse_of: :mask_b
  has_many :mask_states, dependent: :destroy
  has_many :mask_events, dependent: :destroy

  validates :unique_internal_model_code, presence: true
  validates :unique_internal_model_code, uniqueness: true
  validate :cannot_be_duplicate_of_self
  validate :cannot_create_circular_reference

  # Create initial mask state snapshot after creation
  after_create :create_initial_state

  # Regenerate mask state from events
  def regenerate
    computed_state = MaskStatusBuilder.build_and_serialize(mask_id: id)
    update!(current_state: computed_state)
  end

  def self.find_targeted_but_untested_masks(manager_id)
    results = Mask.connection.exec_query(
      <<-SQL
      WITH scoped_to_manager AS (
        SELECT * FROM managed_users WHERE manager_id = #{manager_id}
      ), targeted_masks AS (
        SELECT * FROM masks
        WHERE JSON_ARRAY_LENGTH(payable_datetimes) > 0
      ), fit_tests_grouped_by_managed_id_and_mask_id AS (
        SELECT user_id, mask_id FROM fit_tests
        INNER JOIN scoped_to_manager
        ON (scoped_to_manager.managed_id = fit_tests.user_id)
        GROUP BY 1,2
      ), user_mask_cross_join AS (
        SELECT scoped_to_manager.managed_id, targeted_masks.id as mask_id, fit_tests.id as fit_test_id
        FROM scoped_to_manager
          CROSS JOIN targeted_masks
          LEFT JOIN fit_tests
            ON scoped_to_manager.managed_id = fit_tests.user_id
            AND targeted_masks.id = fit_tests.mask_id
      ), cross_join AS (
        SELECT managed_id, mask_id, COUNT(DISTINCT fit_test_id)
        FROM user_mask_cross_join

        GROUP BY 1,2
      )

      SELECT cross_join.*, masks.* FROM cross_join
      INNER JOIN masks ON masks.id = cross_join.mask_id
      SQL
    )

    json_parsed = JSON.parse(results.to_json)
    FitTest.json_parse(json_parsed, ['image_urls'])
  end

  def self.find_payable_on(date)
    masks = Mask.all

    masks.select do |m|
      m.payable_datetimes.any? do |dts|
        if dts['end_datetime']
          dts['start_datetime'].to_datetime < date && dts['end_datetime'].to_datetime >= date
        else
          dts['start_datetime'].to_datetime < date
        end
      end
    end
  end

  def self.average_filtration_efficiencies_sql
    <<-SQL
        #{N99ModeToN95ModeConverterService.avg_sealed_ffs_sql('')}
    SQL
  end

  def self.with_aggregations(mask_ids = nil)
    if mask_ids
      Mask.sanitize_sql_array(['WHERE m.id IN (?)', mask_ids])
    else
      ''
    end

    result = Mask.connection.exec_query(
      <<-SQL
        WITH fit_test_counts_per_mask AS (
          SELECT m.id as mask_id, COUNT(ft.id) AS fit_test_count
          FROM masks m
          LEFT JOIN fit_tests ft
          ON (ft.mask_id = m.id)
          GROUP BY m.id
        ),

        #{average_filtration_efficiencies_sql},

        breathability_measurements AS (
            SELECT m.id, b ->> 'breathability_pascals' as breathability_pascals,
                b ->> 'breathability_pascals_notes' as breathability_pascals_notes
            FROM masks m, jsonb_array_elements(
                  CASE
                    WHEN jsonb_typeof(breathability) = 'array' THEN breathability
                    ELSE jsonb_build_array(breathability)
                  END
            ) AS b
        ),         breathability_aggregates AS (
            SELECT id,
              COUNT(*) AS count_breathability,
              AVG(CASE#{' '}
                WHEN breathability_pascals ~ '^[0-9]+\.?[0-9]*$'#{' '}
                THEN breathability_pascals::numeric#{' '}
                ELSE NULL#{' '}
              END) AS avg_breathability_pa
            FROM breathability_measurements
            GROUP BY 1
        ),

        unique_fit_tester_counts_per_mask AS (
          SELECT m.id AS mask_id, COUNT(DISTINCT fm.user_id) AS unique_fit_testers_count
          FROM masks m
          LEFT JOIN fit_tests ft
          ON (ft.mask_id = m.id)
          LEFT JOIN facial_measurements fm
          ON (fm.id = ft.facial_measurement_id)
          GROUP BY m.id
        ), unique_fit_testers_per_mask AS (
          SELECT m.id AS mask_id,
            fm.user_id,
            MIN(ft.created_at) AS created_at
          FROM masks m
          LEFT JOIN fit_tests ft
            ON (ft.mask_id = m.id)
          LEFT JOIN facial_measurements fm
            ON (fm.id = ft.facial_measurement_id)
          GROUP BY 1, 2
        )

        SELECT masks.id,
          masks.*,
          CASE WHEN fit_test_count IS NULL THEN 0 ELSE fit_test_count END AS fit_test_count,
          unique_fit_tester_counts_per_mask.*,
          avg_sealed_ffs.avg_sealed_ff AS avg_sealed_fit_factor,
          avg_sealed_ffs.count_sealed_fit_factor,
          breathability_aggregates.avg_breathability_pa,
          count_breathability
        FROM
          masks
          LEFT JOIN fit_test_counts_per_mask ON (fit_test_counts_per_mask.mask_id = masks.id)
          LEFT JOIN unique_fit_tester_counts_per_mask
            ON (unique_fit_tester_counts_per_mask.mask_id = masks.id)
          LEFT JOIN avg_sealed_ffs
            ON masks.id = avg_sealed_ffs.mask_id
          LEFT JOIN breathability_aggregates
            ON masks.id = breathability_aggregates.id

      SQL
    ).to_a

    result.each do |x|
      x['image_urls'] = if x['image_urls']
                          [x['image_urls'].gsub(/{|}/, '').gsub(/"/, '')]
                        else
                          ['']
                        end

      x['breathability'] = JSON.parse(x['breathability']) if x['breathability']

      x['filtration_efficiencies'] = JSON.parse(x['filtration_efficiencies']) if x['filtration_efficiencies']

      x['where_to_buy_urls'] = if x['where_to_buy_urls']
                                 [x['where_to_buy_urls'].gsub(/{|}/, '')]
                               else
                                 ['']
                               end

      x['payable_datetimes'] = JSON.parse(x['payable_datetimes'])
      x['colors'] = JSON.parse(x['colors'])
    end

    result
  end

  def self.with_admin_aggregations(mask_ids = nil)
    aggregations = with_aggregations(mask_ids)

    masks = if mask_ids
              Mask.where(id: mask_ids)
            else
              Mask.all
            end

    # Calculate demographics without privacy thresholds for admin
    masks.each { |m| m.calculate_demographics!(apply_privacy_threshold: false) }

    aggregation_lookup = aggregations.index_by { |mask| mask['id'] || mask[:id] }

    masks.map do |m|
      admin_data = JSON.parse(m.to_json)
      aggregated_data = aggregation_lookup[m.id] || {}
      admin_data.merge(aggregated_data)
    end
  end

  def self.with_privacy_aggregations(mask_ids = nil)
    aggregations = with_aggregations(mask_ids)
    race_ethnicity_options = %w[
      american_indian_or_alaskan_native_count
      asian_pacific_islander_count
      black_african_american_count
      hispanic_count
      white_caucasian_count
      multiple_ethnicity_other_count
    ]

    gender_sex_options = %w[
      cisgender_male_count
      cisgender_female_count
      mtf_transgender_count
      ftm_transgender_count
      intersex_count
      other_gender_sex_count
    ]

    age_options = %w[
      age_between_2_and_4
      age_between_4_and_6
      age_between_6_and_8
      age_between_8_and_10
      age_between_10_and_12
      age_between_12_and_14
      age_between_14_and_18
      age_adult
    ]

    threshold = 5
    hash = {}

    aggregations.each do |r|
      r['prefer_not_to_disclose_race_ethnicity_count'] ||= 0
      r['prefer_not_to_disclose_gender_sex_count'] ||= 0
      r['prefer_not_to_disclose_age_count'] ||= 0

      race_ethnicity_options.each do |re|
        r[re] ||= 0
        if r[re] < threshold
          r['prefer_not_to_disclose_race_ethnicity_count'] += r[re]
          r[re] = 0
        end
      end

      gender_sex_options.each do |gs|
        r[gs] ||= 0

        if r[gs] < threshold
          r['prefer_not_to_disclose_gender_sex_count'] += r[gs]
          r[gs] = 0
        end
      end

      age_options.each do |a|
        r[a] ||= 0

        if r[a] < threshold
          r['prefer_not_to_disclose_age_count'] += r[a]
          r[a] = 0
        end
      end

      hash[r['id']] = r
    end

    masks = if mask_ids
              Mask.where(id: mask_ids)
            else
              Mask.all
            end

    # Calculate demographics for each mask before converting to JSON
    # Apply privacy thresholds for non-admin view
    masks.each { |m| m.calculate_demographics!(apply_privacy_threshold: true) }

    masks.map do |m|
      m_data = JSON.parse(m.to_json)

      # Apply privacy threshold adjustments
      # Note: hash[m.id] may not have demographic data anymore since we removed SQL aggregations
      # The demographic counts are now in m_data from calculate_demographics!
      # We only merge non-demographic fields from hash if they exist
      if hash[m.id]
        # Don't overwrite the demographic counts we just calculated
        hash_data = hash[m.id].except(
          'american_indian_or_alaskan_native_count',
          'asian_pacific_islander_count',
          'black_african_american_count',
          'hispanic_count',
          'white_caucasian_count',
          'multiple_ethnicity_other_count',
          'prefer_not_to_disclose_race_ethnicity_count',
          'cisgender_male_count',
          'cisgender_female_count',
          'mtf_transgender_count',
          'ftm_transgender_count',
          'intersex_count',
          'prefer_not_to_disclose_gender_sex_count',
          'other_gender_sex_count',
          'age_between_2_and_4',
          'age_between_4_and_6',
          'age_between_6_and_8',
          'age_between_8_and_10',
          'age_between_10_and_12',
          'age_between_12_and_14',
          'age_between_14_and_18',
          'age_adult',
          'prefer_not_to_disclose_age_count'
        )
        m_data.merge(hash_data)
      else
        m_data
      end
    end
  end

  # Override as_json to include virtual attributes
  def as_json(options = {})
    super(options).merge(
      'american_indian_or_alaskan_native_count' => american_indian_or_alaskan_native_count,
      'asian_pacific_islander_count' => asian_pacific_islander_count,
      'black_african_american_count' => black_african_american_count,
      'hispanic_count' => hispanic_count,
      'white_caucasian_count' => white_caucasian_count,
      'multiple_ethnicity_other_count' => multiple_ethnicity_other_count,
      'prefer_not_to_disclose_race_ethnicity_count' => prefer_not_to_disclose_race_ethnicity_count,
      'cisgender_male_count' => cisgender_male_count,
      'cisgender_female_count' => cisgender_female_count,
      'mtf_transgender_count' => mtf_transgender_count,
      'ftm_transgender_count' => ftm_transgender_count,
      'intersex_count' => intersex_count,
      'prefer_not_to_disclose_gender_sex_count' => prefer_not_to_disclose_gender_sex_count,
      'other_gender_sex_count' => other_gender_sex_count,
      'age_between_2_and_4' => age_between_2_and_4,
      'age_between_4_and_6' => age_between_4_and_6,
      'age_between_6_and_8' => age_between_6_and_8,
      'age_between_8_and_10' => age_between_8_and_10,
      'age_between_10_and_12' => age_between_10_and_12,
      'age_between_12_and_14' => age_between_12_and_14,
      'age_between_14_and_18' => age_between_14_and_18,
      'age_adult' => age_adult,
      'prefer_not_to_disclose_age_count' => prefer_not_to_disclose_age_count
    )
  end

  # Calculate demographics from fit tests
  def calculate_demographics!(apply_privacy_threshold: false)
    # Get unique fit testers for this mask
    unique_testers = FitTest.joins(:facial_measurement)
                            .where(mask_id: id)
                            .select('DISTINCT facial_measurements.user_id, fit_tests.created_at')
                            .group_by(&:user_id)
                            .map { |user_id, fts| { user_id: user_id, created_at: fts.first.created_at } }

    # Load profiles through ActiveRecord to get decrypted values
    user_ids = unique_testers.map { |t| t[:user_id] }.compact
    profiles = Profile.where(user_id: user_ids).index_by(&:user_id)

    # Initialize all counts to 0
    self.american_indian_or_alaskan_native_count = 0
    self.asian_pacific_islander_count = 0
    self.black_african_american_count = 0
    self.hispanic_count = 0
    self.white_caucasian_count = 0
    self.multiple_ethnicity_other_count = 0
    self.prefer_not_to_disclose_race_ethnicity_count = 0
    self.cisgender_male_count = 0
    self.cisgender_female_count = 0
    self.mtf_transgender_count = 0
    self.ftm_transgender_count = 0
    self.intersex_count = 0
    self.prefer_not_to_disclose_gender_sex_count = 0
    self.other_gender_sex_count = 0
    self.age_between_2_and_4 = 0
    self.age_between_4_and_6 = 0
    self.age_between_6_and_8 = 0
    self.age_between_8_and_10 = 0
    self.age_between_10_and_12 = 0
    self.age_between_12_and_14 = 0
    self.age_between_14_and_18 = 0
    self.age_adult = 0
    self.prefer_not_to_disclose_age_count = 0

    # Count demographics
    unique_testers.each do |tester|
      profile = profiles[tester[:user_id]]
      next unless profile

      # Count race/ethnicity
      case profile.race_ethnicity
      when 'American Indian or Alaskan Native'
        self.american_indian_or_alaskan_native_count += 1
      when 'Asian / Pacific Islander'
        self.asian_pacific_islander_count += 1
      when 'Black or African American'
        self.black_african_american_count += 1
      when 'Hispanic'
        self.hispanic_count += 1
      when 'White / Caucasian'
        self.white_caucasian_count += 1
      when 'Multiple ethnicity / Other'
        self.multiple_ethnicity_other_count += 1
      when 'Prefer not to disclose'
        self.prefer_not_to_disclose_race_ethnicity_count += 1
      end

      # Count gender/sex
      case profile.gender_and_sex
      when 'Cisgender male'
        self.cisgender_male_count += 1
      when 'Cisgender female'
        self.cisgender_female_count += 1
      when 'MTF transgender'
        self.mtf_transgender_count += 1
      when 'FTM transgender'
        self.ftm_transgender_count += 1
      when 'Intersex'
        self.intersex_count += 1
      when 'Prefer not to disclose'
        self.prefer_not_to_disclose_gender_sex_count += 1
      when 'Other'
        self.other_gender_sex_count += 1
      end

      # Count age ranges
      if profile.year_of_birth
        begin
          year_of_birth = profile.year_of_birth.to_i
          age = tester[:created_at].year - year_of_birth

          case age
          when 2...4
            self.age_between_2_and_4 += 1
          when 4...6
            self.age_between_4_and_6 += 1
          when 6...8
            self.age_between_6_and_8 += 1
          when 8...10
            self.age_between_8_and_10 += 1
          when 10...12
            self.age_between_10_and_12 += 1
          when 12...14
            self.age_between_12_and_14 += 1
          when 14...18
            self.age_between_14_and_18 += 1
          when 18..Float::INFINITY
            self.age_adult += 1
          end
        rescue StandardError
          # If year_of_birth can't be converted, skip age calculation
        end
      elsif profile.user_id
        self.prefer_not_to_disclose_age_count += 1
      end
    end

    # Apply privacy thresholds if requested
    apply_privacy_thresholds! if apply_privacy_threshold

    self
  end

  # Apply privacy thresholds to demographic counts
  def apply_privacy_thresholds!
    threshold = DEMOGRAPHIC_PRIVACY_THRESHOLD

    # Race/ethnicity groups
    race_ethnicity_fields = %i[
      american_indian_or_alaskan_native_count
      asian_pacific_islander_count
      black_african_american_count
      hispanic_count
      white_caucasian_count
      multiple_ethnicity_other_count
    ]

    race_ethnicity_fields.each do |field|
      count = send(field) || 0
      if count.positive? && count < threshold
        self.prefer_not_to_disclose_race_ethnicity_count += count
        send("#{field}=", 0)
      end
    end

    # Gender/sex groups
    gender_sex_fields = %i[
      cisgender_male_count
      cisgender_female_count
      mtf_transgender_count
      ftm_transgender_count
      intersex_count
      other_gender_sex_count
    ]

    gender_sex_fields.each do |field|
      count = send(field) || 0
      if count.positive? && count < threshold
        self.prefer_not_to_disclose_gender_sex_count += count
        send("#{field}=", 0)
      end
    end

    # Age groups
    age_fields = %i[
      age_between_2_and_4
      age_between_4_and_6
      age_between_6_and_8
      age_between_8_and_10
      age_between_10_and_12
      age_between_12_and_14
      age_between_14_and_18
      age_adult
    ]

    age_fields.each do |field|
      count = send(field) || 0
      if count.positive? && count < threshold
        self.prefer_not_to_disclose_age_count += count
        send("#{field}=", 0)
      end
    end

    self
  end

  private

  def create_initial_state
    # Create a snapshot of the mask's initial state
    mask_states.create!(
      unique_internal_model_code: unique_internal_model_code,
      modifications: modifications,
      image_urls: image_urls,
      author_ids: author_ids,
      where_to_buy_urls: where_to_buy_urls,
      strap_type: strap_type,
      mass_grams: mass_grams,
      height_mm: height_mm,
      width_mm: width_mm,
      depth_mm: depth_mm,
      has_gasket: has_gasket,
      initial_cost_us_dollars: initial_cost_us_dollars,
      sources: sources,
      notes: notes,
      filter_type: filter_type,
      filtration_efficiencies: filtration_efficiencies,
      breathability: breathability,
      style: style,
      filter_change_cost_us_dollars: filter_change_cost_us_dollars,
      age_range: age_range,
      color: color,
      has_exhalation_valve: has_exhalation_valve,
      author_id: author_id,
      perimeter_mm: perimeter_mm,
      payable_datetimes: payable_datetimes,
      colors: colors,
      duplicate_of: duplicate_of,
      brand_id: brand_id,
      bulk_fit_tests_import_id: bulk_fit_tests_import_id
    )
  rescue StandardError => e
    Rails.logger.error("Failed to create initial state for mask #{id}: #{e.message}")
  end

  def cannot_be_duplicate_of_self
    return if duplicate_of.blank?

    return unless duplicate_of == id

    errors.add(:duplicate_of, 'cannot reference itself')
  end

  def cannot_create_circular_reference
    return if duplicate_of.blank?
    return if duplicate_of == id # Already handled by cannot_be_duplicate_of_self

    # Traverse up the chain to check for circular references
    visited = Set.new([id])
    current_mask_id = duplicate_of

    while current_mask_id.present?
      # If we've seen this mask before, we have a cycle
      if visited.include?(current_mask_id)
        errors.add(:duplicate_of, 'would create a circular reference')
        break
      end

      visited.add(current_mask_id)

      # Get the next mask in the chain
      next_mask = Mask.find_by(id: current_mask_id)
      break unless next_mask

      current_mask_id = next_mask.duplicate_of
    end
  end

  # Virtual attributes for demographic counts
  attr_accessor :american_indian_or_alaskan_native_count,
                :asian_pacific_islander_count,
                :black_african_american_count,
                :hispanic_count,
                :white_caucasian_count,
                :multiple_ethnicity_other_count,
                :prefer_not_to_disclose_race_ethnicity_count,
                :cisgender_male_count,
                :cisgender_female_count,
                :mtf_transgender_count,
                :ftm_transgender_count,
                :intersex_count,
                :prefer_not_to_disclose_gender_sex_count,
                :other_gender_sex_count,
                :age_between_2_and_4,
                :age_between_4_and_6,
                :age_between_6_and_8,
                :age_between_8_and_10,
                :age_between_10_and_12,
                :age_between_12_and_14,
                :age_between_14_and_18,
                :age_adult,
                :prefer_not_to_disclose_age_count
end
