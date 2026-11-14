# frozen_string_literal: true

# Descriptive rates for the same canonical, labeled records used by the dashboard.
# Keep calculations unrounded until the final presentation values.
class DashboardPassRatesService
  def self.call(rows)
    new(rows).call
  end

  def initialize(rows)
    @tests = rows.reject { |row| row['qlft_pass'].nil? }
  end

  def call
    pairs = pair_units
    {
      overall: test_summary(@tests),
      by_mask: test_groups('mask_id', 'unique_internal_model_code'),
      by_strap_type: test_groups('strap_type', 'strap_type'),
      by_style: test_groups('style', 'style'),
      equal_person_mask: {
        overall: pair_summary(pairs),
        by_mask: pair_groups(pairs, 'mask_id', 'unique_internal_model_code'),
        by_strap_type: pair_groups(pairs, 'strap_type', 'strap_type'),
        by_style: pair_groups(pairs, 'style', 'style')
      },
      equal_family_by_style: family_style_rates(pairs),
      weighting: {
        pair_outcome: 'Mean of the observed pass/fail outcomes within each person–mask pair.',
        style_family_mean: 'Average pair rates within person–family; average people within family; ' \
                           'average families within style.',
        missing_family: 'Missing family IDs use a separate family per canonical mask; they are not pooled together.',
        excluded_pair_records: @tests.size - pairs.sum { |pair| pair[:test_count] }
      }
    }
  end

  private

  def passed?(row)
    [true, 't'].include?(row['qlft_pass'])
  end

  def test_summary(tests)
    passed = tests.count { |row| passed?(row) }
    { total: tests.size, passed: passed, pass_rate: tests.empty? ? 0 : (100.0 * passed / tests.size).round(2) }
  end

  def test_groups(key, display_key)
    result = @tests.group_by { |row| row[key] }.filter_map do |value, tests|
      next if value.nil?

      test_summary(tests).merge(name: tests.first[display_key] || value.to_s)
    end
    result.sort_by { |row| [-row[:pass_rate], row[:name]] }
  end

  def identifier(value)
    value.to_s.strip unless value.nil? || value.to_s.strip.empty?
  end

  def pair_units
    eligible = @tests.select do |row|
      identifier(row['user_id']) && identifier(row['mask_id']) && [true, false, 't', 'f'].include?(row['qlft_pass'])
    end
    eligible.group_by { |row| [identifier(row['user_id']), identifier(row['mask_id'])] }.map do |(user, mask), tests|
      first = tests.first
      family = identifier(first['fit_family_id'])
      {
        user: user, mask: mask, family: family ? "family:#{family}" : "mask:#{mask}",
        metadata: first, rate: tests.count { |row| passed?(row) }.fdiv(tests.size),
        test_count: tests.size
      }
    end
  end

  def mean(values)
    values.sum.fdiv(values.size) unless values.empty?
  end

  def pair_summary(pairs)
    {
      pair_count: pairs.size,
      test_count: pairs.sum { |pair| pair[:test_count] },
      unique_users: pairs.map { |pair| pair[:user] }.uniq.size,
      mask_count: pairs.map { |pair| pair[:mask] }.uniq.size,
      mixed_pairs: pairs.count { |pair| pair[:rate].positive? && pair[:rate] < 1 },
      pass_rate: mean(pairs.map { |pair| pair[:rate] })&.*(100)&.round(2)
    }
  end

  def pair_groups(pairs, key, display_key)
    result = pairs.group_by { |pair| pair[:metadata][key] }.map do |value, group|
      pair_summary(group).merge(
        name: group.first[:metadata][display_key] || value&.to_s || 'Unknown',
        key => value
      )
    end
    result.sort_by { |row| [-row[:pass_rate], row[:name]] }
  end

  def family_style_rates(pairs)
    result = pairs.group_by { |pair| pair[:metadata]['style'] || 'Unknown' }.map do |style, style_pairs|
      families = style_pairs.group_by { |pair| pair[:family] }.map do |key, family_pairs|
        people = family_pairs.group_by { |pair| pair[:user] }
        person_rates = people.values.map { |person_pairs| mean(person_pairs.map { |pair| pair[:rate] }) }
        { family_key: key, rate: mean(person_rates), unique_users: people.size,
          mask_count: family_pairs.map { |pair| pair[:mask] }.uniq.size,
          pair_count: family_pairs.size, test_count: family_pairs.sum { |pair| pair[:test_count] } }
      end
      { name: style, family_count: families.size,
        unique_users: style_pairs.map { |pair| pair[:user] }.uniq.size,
        pair_count: style_pairs.size, test_count: style_pairs.sum { |pair| pair[:test_count] },
        person_family_count: families.sum { |family| family[:unique_users] },
        pass_rate: (100 * mean(families.map { |family| family[:rate] })).round(2),
        families: families.map { |family| family.except(:rate).merge(pass_rate: (100 * family[:rate]).round(2)) } }
    end
    result.sort_by { |row| [-row[:pass_rate], row[:name]] }
  end
end
