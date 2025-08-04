# frozen_string_literal: true

require 'open-uri'
require 'csv'

class CovidCasesUpdater
  # Download data from NYTimes
  # Check to see if the latest date available is 1 day behind
  # If so, do nothing
  # If not, redownload data
  def initialize; end

  def update
    latest_date = CovidState.get_latest_date

    # TODO: check to see if today's date corresponds with the latest date
    return unless !latest_date || latest_date != Time.zone.today - 1.day

    url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
    download = URI.open(url)

    rows = []

    CSV.foreach(download, headers: true) do |row|
      rows << row
    end

    time = DateTime.now.getutc

    CovidState.transaction do
      CovidState.delete_all

      CovidState.copy_from_client header do |copy|
        rows.each do |r|
          copy << [
            r['cases'],
            r['deaths'],
            r['fips'],
            r['state'],
            r['date'].to_date,
            time,
            time
          ]
        end
      end
    end
  end

  private

  def header
    %i[
      cases_cumulative
      deaths_cumulative
      fips
      state
      date
      created_at
      updated_at
    ]
  end
end
