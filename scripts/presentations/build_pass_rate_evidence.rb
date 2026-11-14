# frozen_string_literal: true

require 'json'
require 'digest'
require 'time'
require_relative '../../app/services/dashboard_pass_rates_service'

input, output = ARGV
abort 'Usage: ruby build_pass_rate_evidence.rb PRIVATE_ROWS.json EVIDENCE.json' unless input && output

raw = File.read(input)
rows = JSON.parse(raw)
rates = DashboardPassRatesService.call(rows)
calculator = File.expand_path('../../app/services/dashboard_pass_rates_service.rb', __dir__)
report = {
  source: 'Local development database: canonical labeled records from FitTestsWithFacialMeasurementsService.call',
  retrieved_at_utc: Time.now.utc.iso8601,
  input_sha256: Digest::SHA256.hexdigest(raw),
  calculator_sha256: Digest::SHA256.file(calculator).hexdigest,
  cohort_note: 'This local snapshot is separate from the dated public dashboard snapshots on the preceding slides.',
  policy: 'Mean outcomes per person–mask; mean pair rates per person–family; ' \
          'mean people per family; mean families per style.',
  pass_rates: rates
}
File.write(output, "#{JSON.pretty_generate(report)}\n")
puts JSON.pretty_generate(
  tests: rates[:overall], equal_person_mask: rates[:equal_person_mask][:overall],
  styles: rates[:equal_family_by_style].map { |style| style.except(:families) }
)
