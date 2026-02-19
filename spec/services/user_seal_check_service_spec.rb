# frozen_string_literal: true

require 'rails_helper'

RSpec.describe UserSealCheckService, type: :service do
  describe '.evaluate' do
    let(:sizing_question) { 'What do you think about the sizing of this mask relative to your face?' }
    let(:air_movement_question) { '...how much air movement on your face along the seal of the mask did you feel?' }

    context 'when user_seal_check is nil or empty' do
      it 'returns "incomplete" for nil' do
        expect(described_class.evaluate(nil)).to eq('incomplete')
      end

      it 'returns "incomplete" for empty hash' do
        expect(described_class.evaluate({})).to eq('incomplete')
      end
    end

    context 'when questions are missing' do
      it 'returns "incomplete" when sizing question is missing' do
        user_seal_check = {
          'positive' => {
            air_movement_question => 'No air movement'
          }
        }
        expect(described_class.evaluate(user_seal_check)).to eq('incomplete')
      end

      it 'returns "incomplete" when air movement question is missing' do
        user_seal_check = {
          'sizing' => {
            sizing_question => 'Somewhere in-between too small and too big'
          }
        }
        expect(described_class.evaluate(user_seal_check)).to eq('incomplete')
      end

      it 'returns "incomplete" when sizing answer is empty string' do
        user_seal_check = {
          'sizing' => {
            sizing_question => ''
          },
          'positive' => {
            air_movement_question => 'No air movement'
          }
        }
        expect(described_class.evaluate(user_seal_check)).to eq('incomplete')
      end

      it 'returns "incomplete" when air movement answer is empty string' do
        user_seal_check = {
          'sizing' => {
            sizing_question => 'Somewhere in-between too small and too big'
          },
          'positive' => {
            air_movement_question => ''
          }
        }
        expect(described_class.evaluate(user_seal_check)).to eq('incomplete')
      end
    end

    context 'when user seal check fails' do
      it 'returns "fail" when sizing is "Too big"' do
        user_seal_check = {
          'sizing' => {
            sizing_question => 'Too big'
          },
          'positive' => {
            air_movement_question => 'No air movement'
          }
        }
        expect(described_class.evaluate(user_seal_check)).to eq('fail')
      end

      it 'returns "fail" when sizing is "Too small"' do
        user_seal_check = {
          'sizing' => {
            sizing_question => 'Too small'
          },
          'positive' => {
            air_movement_question => 'No air movement'
          }
        }
        expect(described_class.evaluate(user_seal_check)).to eq('fail')
      end

      it 'returns "fail" when air movement is "A lot of air movement"' do
        user_seal_check = {
          'sizing' => {
            sizing_question => 'Somewhere in-between too small and too big'
          },
          'positive' => {
            air_movement_question => 'A lot of air movement'
          }
        }
        expect(described_class.evaluate(user_seal_check)).to eq('fail')
      end
    end

    context 'when user seal check passes' do
      it 'returns "pass" when sizing is correct and air movement is "No air movement"' do
        user_seal_check = {
          'sizing' => {
            sizing_question => 'Somewhere in-between too small and too big'
          },
          'positive' => {
            air_movement_question => 'No air movement'
          }
        }
        expect(described_class.evaluate(user_seal_check)).to eq('pass')
      end

      it 'returns "pass" when sizing is correct and air movement is "Some air movement"' do
        user_seal_check = {
          'sizing' => {
            sizing_question => 'Somewhere in-between too small and too big'
          },
          'positive' => {
            air_movement_question => 'Some air movement'
          }
        }
        expect(described_class.evaluate(user_seal_check)).to eq('pass')
      end
    end

    context 'when using symbol keys' do
      it 'works with symbol keys for sizing' do
        user_seal_check = {
          sizing: {
            sizing_question => 'Too big'
          },
          positive: {
            air_movement_question => 'No air movement'
          }
        }
        expect(described_class.evaluate(user_seal_check)).to eq('fail')
      end
    end

    context 'when combination does not match pass criteria' do
      it 'returns "incomplete" for unexpected combinations' do
        user_seal_check = {
          'sizing' => {
            sizing_question => 'Somewhere in-between too small and too big'
          },
          'positive' => {
            air_movement_question => 'Unexpected value'
          }
        }
        expect(described_class.evaluate(user_seal_check)).to eq('incomplete')
      end
    end
  end

  describe '.qlft_pass_value' do
    it 'returns false when user seal check fails' do
      user_seal_check = {
        'sizing' => {
          'What do you think about the sizing of this mask relative to your face?' => 'Too big'
        },
        'positive' => {
          '...how much air movement on your face along the seal of the mask did you feel?' => 'No air movement'
        }
      }
      expect(described_class.qlft_pass_value(user_seal_check)).to be(false)
    end

    it 'returns nil when user seal check passes' do
      sizing_response = 'Somewhere in-between too small and too big'
      user_seal_check = {
        'sizing' => {
          'What do you think about the sizing of this mask relative to your face?' => sizing_response
        },
        'positive' => {
          '...how much air movement on your face along the seal of the mask did you feel?' => 'No air movement'
        }
      }
      expect(described_class.qlft_pass_value(user_seal_check)).to be_nil
    end

    it 'returns nil when user seal check is incomplete' do
      expect(described_class.qlft_pass_value(nil)).to be_nil
    end
  end
end
