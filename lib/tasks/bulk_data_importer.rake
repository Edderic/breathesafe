# frozen_string_literal: true

# rubocop:disable Layout/LineLength
namespace :bulk_data do
  desc 'Run BulkDataImporter. Example: rake bulk_data:import style=Crash2.5 read=./in.csv write=./out.csv env=staging user_id=123 mode=validate testing_mode=N95'
  task import: :environment do
    style = ENV['style'] || ENV['STYLE'] || 'Crash2.5'
    read  = ENV['read']  || ENV['READ']
    write = ENV['write'] || ENV['WRITE']
    env   = ENV['env']   || ENV['ENV'] || ENV['HEROKU_ENVIRONMENT']
    user  = (ENV['user_id'] || ENV['USER_ID']).to_i
    mode  = ENV['mode'] || ENV['MODE'] || 'validate'
    testing_mode = ENV['testing_mode'] || ENV['TESTING_MODE'] || 'N95'

    if read.blank? || write.blank? || user <= 0
      abort 'Usage: rake bulk_data:import style=Crash2.5 read=./in.csv write=./out.csv env=staging user_id=123 mode=validate testing_mode=N99'
    end

    result = BulkDataImporter.call(
      style: style,
      read_path: read,
      write_path: write,
      environment: env,
      user_id: user,
      mode: mode,
      testing_mode: testing_mode
    )
    puts result.inspect
  end
end
# rubocop:enable Layout/LineLength
