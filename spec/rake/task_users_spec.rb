# frozen_string_literal: true

require 'rails_helper'
require 'rake'

Rails.application.load_tasks unless Rake::Task.task_defined?('users:delete_account')

RSpec.describe Rake::Task do
  let(:task) { described_class['users:delete_account'] }

  around do |example|
    original_user_id = ENV.fetch('USER_ID', nil)
    original_confirm = ENV.fetch('CONFIRM', nil)

    ENV.delete('USER_ID')
    ENV.delete('CONFIRM')
    task.reenable

    example.run
  ensure
    ENV['USER_ID'] = original_user_id
    ENV['CONFIRM'] = original_confirm
  end

  it 'aborts when USER_ID is missing' do
    expect { task.invoke }.to raise_error(SystemExit)
  end

  it 'aborts when CONFIRM does not match USER_ID' do
    ENV['USER_ID'] = '123'
    ENV['CONFIRM'] = '456'

    expect { task.invoke }.to raise_error(SystemExit)
  end

  it 'soft-deletes the confirmed user' do
    user = create(:user, :with_profile)
    ENV['USER_ID'] = user.id.to_s
    ENV['CONFIRM'] = user.id.to_s

    expect { task.invoke }.to output(/Deleted user #{user.id}/).to_stdout
    expect(User.with_deleted.find(user.id)).to be_deleted
  end
end
