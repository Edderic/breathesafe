# frozen_string_literal: true

require 'csv'

class CsvHelper
  def self.parse(csv_string)
    counter = 0
    header = []
    rows = []

    # Build a JSON-like representation of rows
    CSV.parse(csv_string) do |row|
      accum = {}

      if counter.zero?
        header = row.map(&:strip)
      else
        row.each.with_index do |value, index|
          accum[header[index]] = value.strip
        end
        rows << accum
      end
      counter += 1
    end

    {
      'header': header,
      'rows': rows
    }
  end
end
