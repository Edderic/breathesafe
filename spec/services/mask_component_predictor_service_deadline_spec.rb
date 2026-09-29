# frozen_string_literal: true

require 'rails_helper'

RSpec.describe MaskComponentPredictorService do
  it 'terminates and reaps a stalled inline predictor before falling back' do
    allow(Rails.application.config).to receive(:use_lambda_predictor).and_return(false)
    allow(ENV).to receive(:[]).and_call_original
    allow(ENV).to receive(:[]).with('USE_FLASK_PREDICTOR').and_return(nil)
    child_pid = nil
    allow(Open3).to receive(:popen3).and_wrap_original do |original, *_args, &block|
      original.call(RbConfig.ruby, '-e', 'sleep 60', pgroup: true) do |stdin, stdout, stderr, wait|
        child_pid = wait.pid
        block.call(stdin, stdout, stderr, wait)
      end
    end
    start = Process.clock_gettime(Process::CLOCK_MONOTONIC)
    result = described_class.predict_with_timeout('Zimi B95-XL', seconds: 0.1)
    expect(result).to be_nil
    expect(Process.clock_gettime(Process::CLOCK_MONOTONIC) - start).to be < 2
    expect { Process.kill(0, child_pid) }.to raise_error(Errno::ESRCH)
  end

  it 'bounds adapter calls even when an adapter rescues StandardError' do
    allow(Rails.application.config).to receive(:use_lambda_predictor).and_return(true)
    allow(MaskComponentPredictorLambdaService).to receive(:predict) do
      sleep 60
    rescue StandardError
      sleep 60
    end
    start = Process.clock_gettime(Process::CLOCK_MONOTONIC)
    expect(described_class.predict_with_timeout('Zimi', seconds: 0.05)).to be_nil
    expect(Process.clock_gettime(Process::CLOCK_MONOTONIC) - start).to be < 1
  end
end
