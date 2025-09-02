# frozen_string_literal: true

require 'csv'
begin
  require 'aws-sdk-s3'
rescue LoadError
  # Allow running locally without aws-sdk-s3; will raise if S3 is actually used
end

# BulkDataImporter ingests/validates external fit testing CSVs.
#
# Usage:
#   BulkDataImporter.call(
#     style: 'Crash2.5',
#     read_path: 'input.csv',
#     write_path: 'output.csv',
#     environment: 'staging',
#     user_id: 123,
#     mode: 'validate', # or 'save'
#     testing_mode: 'N95' # 'N99' | 'N95' | 'qualitative'
#   )
#
# Behavior:
# - validate: fills suggested_* and distance in the output CSV (
#   same headers) and writes to S3 bucket breathesafe-<env>/bulk_imports/<write_path>.
# - save: asserts confirmed_breathesafe_mask_id is present or 'SKIP'; creates FitTest rows for non-SKIP records.
#
class BulkDataImporter
  SUPPORTED_STYLES = ['Crash2.5'].freeze
  SUPPORTED_TESTING_MODES = %w[N99 N95 qualitative].freeze

  EXPECTED_COLUMNS_CRASH25 = [
    'Mask name',
    'suggested_breathesafe_unique_internal_model_code',
    'distance',
    'suggested_breathesafe_mask_id',
    'confirmed_breathesafe_mask_id',
    *('Exercise 1'..'Exercise 12').to_a,
    'Protocol',
    'Notes'
  ].freeze

  DEFAULT_DISTANCE_THRESHOLD = 0.8

  class << self
    def dev_env?(environment)
      %w[development dev].include?(environment.to_s.strip.downcase)
    end
    def call(style:, read_path:, write_path:, environment:, user_id:, mode:, testing_mode:)
      validate_inputs!(style:, read_path:, write_path:, environment:, user_id:, mode:, testing_mode:)
      if dev_env?(environment)
        csv_in = File.read(File.expand_path(read_path))
      else
        bucket = s3_bucket_for(environment)
        csv_in = read_from_s3_or_local(bucket:, path: read_path)
      end
      table = CSV.parse(csv_in, headers: true)
      headers = table.headers

      ensure_expected_headers!(style:, headers:)

      case mode.to_s
      when 'validate'
        out_table = perform_validate(table: table, threshold: DEFAULT_DISTANCE_THRESHOLD)
        if dev_env?(environment)
          File.write(File.expand_path(write_path), out_table.to_csv)
          { status: 'ok', written_to: File.expand_path(write_path), rows: out_table.size }
        else
          write_csv_to_s3(bucket: s3_bucket_for(environment), key: s3_key_for(write_path), csv_string: out_table.to_csv)
          { status: 'ok', written_to: "s3://#{s3_bucket_for(environment)}/#{s3_key_for(write_path)}", rows: out_table.size }
        end
      when 'save'
        perform_save!(table: table, user_id:, style:, testing_mode:)
        { status: 'ok', saved_rows: table.size }
      else
        raise ArgumentError, "Unsupported mode: #{mode}"
      end
    end
    # rubocop:enable Metrics/ParameterLists

    private

    # rubocop:disable Metrics/ParameterLists
    def validate_inputs!(style:, read_path:, write_path:, environment:, user_id:, mode:, testing_mode:)
      raise ArgumentError, "Unsupported style: #{style}" unless SUPPORTED_STYLES.include?(style)
      raise ArgumentError, 'read_path is required' if read_path.to_s.strip.empty?
      raise ArgumentError, 'write_path is required' if write_path.to_s.strip.empty?
      raise ArgumentError, 'environment is required' if environment.to_s.strip.empty?
      raise ArgumentError, 'user_id is required' if user_id.to_i <= 0
      raise ArgumentError, 'mode must be validate or save' unless %w[validate save].include?(mode.to_s)

      return if SUPPORTED_TESTING_MODES.include?(testing_mode.to_s)

      raise ArgumentError,
            'testing_mode must be N99, N95, or qualitative'
    end
    # rubocop:enable Metrics/ParameterLists

    def ensure_expected_headers!(style:, headers:)
      expected = case style
                 when 'Crash2.5' then EXPECTED_COLUMNS_CRASH25
                 else []
                 end
      missing = expected - headers
      return if missing.empty?

      raise ArgumentError, "Missing required columns: #{missing.join(', ')}"
    end

    def s3_bucket_for(environment)
      env = environment.to_s.strip.downcase
      case env
      when 'production' then 'breathesafe-production'
      when 'staging' then 'breathesafe-staging'
      when 'development', 'dev' then 'breathesafe-development'
      else
        raise ArgumentError, "Unsupported environment: #{environment}"
      end
    end

    def s3_key_for(path)
      # Store under bulk_imports/<path>
      p = path.to_s.sub(%r{^/+}, '')
      "bulk_imports/#{p}"
    end

    def s3_client
      region = ENV['AWS_REGION'].presence || ENV['S3_BUCKET_REGION'].presence || 'us-east-1'
      Aws::S3::Client.new(region: region)
    end

    def read_from_s3_or_local(bucket:, path:)
      key = s3_key_for(path)
      if defined?(Aws::S3::Client)
        begin
          resp = s3_client.get_object(bucket: bucket, key: key)
          return resp.body.read
        rescue StandardError => e
          # Fallback to local if allowed
          raise e unless File.exist?(path)
        end
      end

      File.read(path)
    end

    def write_csv_to_s3(bucket:, key:, csv_string:)
      raise 'aws-sdk-s3 not available' unless defined?(Aws::S3::Client)

      s3_client.put_object(
        bucket: bucket,
        key: key,
        body: csv_string,
        content_type: 'text/csv'
      )
    end

    # VALIDATE
    def perform_validate(table:, threshold:)
      # Preload mask data
      codes = Mask.where.not(unique_internal_model_code: [nil, ''])
                  .pluck(:id, :unique_internal_model_code)

      # Precompute normalized artifacts for matching
      mask_index = codes.map do |id, code|
        norm = normalize_text(code)
        [id, code, norm, trigrams(norm)]
      end

      out_rows = table.map do |row|
        confirmed = row['confirmed_breathesafe_mask_id'].to_s.strip
        row['suggested_breathesafe_mask_id'].to_s.strip

        mask_name = row['Mask name'].to_s
        # Compute suggestion only if confirmed is blank
        suggestion = nil
        distance = nil
        if confirmed.empty?
          suggestion, distance = best_suggestion_for(mask_name, mask_index)
          if distance && distance < threshold
            row['suggested_breathesafe_mask_id'] = suggestion[:mask_id].to_s
            row['suggested_breathesafe_unique_internal_model_code'] = suggestion[:code]
          else
            row['suggested_breathesafe_mask_id'] = ''
            row['suggested_breathesafe_unique_internal_model_code'] = ''
          end
          row['distance'] = (distance ? format('%.4f', distance) : '')
        else
          # Keep existing suggested fields; compute distance against confirmed code for reference
          row['distance'] ||= ''
        end
        row
      end

      CSV::Table.new(out_rows)
    end

    def best_suggestion_for(mask_name, mask_index)
      norm = normalize_text(mask_name)
      grams = trigrams(norm)
      best = nil
      best_d = nil
      mask_index.each do |mask_id, code, norm_code, code_grams|
        d = combined_distance(norm, grams, norm_code, code_grams)
        next if d.nil?

        if best_d.nil? || d < best_d
          best_d = d
          best = { mask_id: mask_id, code: code }
        end
      end
      [best, best_d]
    end

    # Token-based fuzzy distance: 0.5*(1 - jaccard_trigram) + 0.5*lev_norm
    def combined_distance(a_norm, a_grams, b_norm, b_grams)
      return 1.0 if a_norm.empty? || b_norm.empty?

      jacc = jaccard(a_grams, b_grams) # [0,1]
      lev_norm = levenshtein(a_norm, b_norm).to_f / [a_norm.length, b_norm.length].max
      0.5 * (1.0 - jacc) + 0.5 * lev_norm
    end

    def normalize_text(s)
      s.to_s.downcase.gsub(/[^a-z0-9]+/, ' ').strip.squeeze(' ')
    end

    def trigrams(norm)
      # character trigrams across the whole normalized string (including spaces removed)
      str = norm.gsub(' ', '')
      return Set.new if str.length < 3

      grams = []
      (0..(str.length - 3)).each { |i| grams << str[i, 3] }
      Set.new(grams)
    end

    def jaccard(a_set, b_set)
      return 0.0 if a_set.empty? || b_set.empty?

      inter = (a_set & b_set).size
      union = (a_set | b_set).size
      return 0.0 if union.zero?

      inter.to_f / union
    end

    def levenshtein(a, b)
      # Iterative Levenshtein distance (O(nm))
      n = a.length
      m = b.length
      return m if n.zero?
      return n if m.zero?

      prev = (0..m).to_a
      cur = Array.new(m + 1, 0)
      (1..n).each do |i|
        cur[0] = i
        (1..m).each do |j|
          cost = a[i - 1] == b[j - 1] ? 0 : 1
          cur[j] = [
            cur[j - 1] + 1,
            prev[j] + 1,
            prev[j - 1] + cost
          ].min
        end
        prev, cur = cur, prev
      end
      prev[m]
    end

    # SAVE
    def perform_save!(table:, user_id:, style:, testing_mode:)
      missing = []
      table.each_with_index do |row, idx|
        confirmed = row['confirmed_breathesafe_mask_id'].to_s.strip
        next if confirmed == 'SKIP'

        missing << (idx + 2) if confirmed.empty? # +2 for header + 1-based row index
      end
      raise ArgumentError, "confirmed_breathesafe_mask_id blank in rows: #{missing.join(', ')}" unless missing.empty?

      fm = begin
        FacialMeasurement.latest(User.find(user_id))
      rescue StandardError
        nil
      end

      table.each do |row|
        confirmed = row['confirmed_breathesafe_mask_id'].to_s.strip
        next if confirmed == 'SKIP'

        mask_id = confirmed.to_i
        exercises = collect_exercises(row)
        notes = row['Notes'].to_s

        results = build_results(style:, testing_mode:, notes:, exercises:)

        FitTest.create!(
          mask_id: mask_id,
          user_id: user_id,
          facial_measurement_id: fm&.id,
          results: results
        )
      end
    end

    def collect_exercises(row)
      (1..12).map do |i|
        name = "Exercise #{i}"
        val = row[name].to_s
        next if val.empty?

        { 'name' => name, 'value' => val }
      end.compact
    end

    def build_results(style:, testing_mode:, notes:, exercises:)
      case testing_mode.to_s
      when 'N99', 'N95'
        {
          'testing_mode' => testing_mode,
          'quantitative' => {
            'procedure' => style,
            'notes' => notes,
            'exercises' => exercises
          }
        }
      else
        {
          'testing_mode' => 'qualitative',
          'qualitative' => {
            'procedure' => style,
            'notes' => notes,
            'exercises' => exercises
          }
        }
      end
    end
  end
end
