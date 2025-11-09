# frozen_string_literal: true

require 'rails_helper'

RSpec.describe FacialMeasurement, type: :model do
  let(:user) do
    User.create(
      email: 'test@example.com',
      password: 'password123'
    )
  end

  describe 'arkit validation' do
    context 'when arkit is nil' do
      it 'is valid' do
        measurement = described_class.new(
          user_id: user.id,
          arkit: nil
        )
        expect(measurement).to be_valid
      end
    end

    context 'when arkit is not present' do
      it 'is valid' do
        measurement = described_class.new(
          user_id: user.id
        )
        expect(measurement).to be_valid
      end
    end

    context 'with valid arkit structure' do
      let(:valid_arkit) do
        {
          'average_measurements' => {
            '14-818' => {
              'value' => 123.45,
              'description' => 'nose right 1'
            },
            '15-819' => {
              'value' => 234.56,
              'description' => 'nose right 2'
            }
          }
        }
      end

      it 'is valid' do
        measurement = described_class.new(
          user_id: user.id,
          arkit: valid_arkit
        )
        expect(measurement).to be_valid
      end

      it 'allows integer values that are positive' do
        arkit_with_int = {
          'average_measurements' => {
            '14-818' => {
              'value' => 100,
              'description' => 'nose right 1'
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit_with_int
        )
        expect(measurement).to be_valid
      end

      it 'allows float values that are positive' do
        arkit_with_float = {
          'average_measurements' => {
            '14-818' => {
              'value' => 123.456789,
              'description' => 'nose right 1'
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit_with_float
        )
        expect(measurement).to be_valid
      end
    end

    context 'when arkit is not a hash' do
      it 'is invalid with string' do
        measurement = described_class.new(
          user_id: user.id,
          arkit: 'not a hash'
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include('must be a hash')
      end

      it 'is invalid with array' do
        measurement = described_class.new(
          user_id: user.id,
          arkit: ['array', 'not', 'hash']
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include('must be a hash')
      end

      it 'is invalid with integer' do
        measurement = described_class.new(
          user_id: user.id,
          arkit: 123
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include('must be a hash')
      end
    end

    context 'when average_measurements key is missing' do
      let(:arkit_without_average) do
        {
          'other_key' => 'some value'
        }
      end

      it 'is invalid' do
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit_without_average
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include('must have an "average_measurements" key')
      end
    end

    context 'when average_measurements is not a hash' do
      it 'is invalid with string' do
        arkit = {
          'average_measurements' => 'not a hash'
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include('"average_measurements" must be a hash')
      end

      it 'is invalid with array' do
        arkit = {
          'average_measurements' => ['array', 'not', 'hash']
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include('"average_measurements" must be a hash')
      end
    end

    context 'when average_measurements keys have invalid format' do
      it 'is invalid with key that does not match digits-dash-digits pattern' do
        arkit = {
          'average_measurements' => {
            'invalid-key' => {
              'value' => 123.45,
              'description' => 'description'
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include(match(/key in average_measurements must match pattern/))
      end

      it 'is invalid with key that has no dash' do
        arkit = {
          'average_measurements' => {
            '14818' => {
              'value' => 123.45,
              'description' => 'description'
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include(match(/key in average_measurements must match pattern/))
      end

      it 'is invalid with key that has multiple dashes' do
        arkit = {
          'average_measurements' => {
            '14-818-999' => {
              'value' => 123.45,
              'description' => 'description'
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include(match(/key in average_measurements must match pattern/))
      end

      it 'is invalid with key that has non-digit characters' do
        arkit = {
          'average_measurements' => {
            '14-abc' => {
              'value' => 123.45,
              'description' => 'description'
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include(match(/key in average_measurements must match pattern/))
      end

      it 'is invalid with non-string key (symbols get converted to strings in JSONB)' do
        # Note: In JSONB, symbol keys are converted to strings, so we test with a numeric key
        arkit = {
          'average_measurements' => {
            14_818 => { # numeric key
              'value' => 123.45,
              'description' => 'description'
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include(match(/key in average_measurements must match pattern/))
      end
    end

    context 'when value for measurement key is not a hash' do
      it 'is invalid with string value' do
        arkit = {
          'average_measurements' => {
            '14-818' => 'not a hash'
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include('value for key \'14-818\' in average_measurements must be a hash')
      end

      it 'is invalid with array value' do
        arkit = {
          'average_measurements' => {
            '14-818' => ['array', 'not', 'hash']
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include('value for key \'14-818\' in average_measurements must be a hash')
      end
    end

    context 'when value key is missing' do
      it 'is invalid' do
        arkit = {
          'average_measurements' => {
            '14-818' => {
              'description' => 'nose right 1'
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include('hash for key \'14-818\' in average_measurements must have \'value\' key')
      end
    end

    context 'when value is not a positive float' do
      it 'is invalid with negative number' do
        arkit = {
          'average_measurements' => {
            '14-818' => {
              'value' => -123.45,
              'description' => 'nose right 1'
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include(match(/value for key '14-818' in average_measurements must be a positive float/))
      end

      it 'is invalid with zero' do
        arkit = {
          'average_measurements' => {
            '14-818' => {
              'value' => 0,
              'description' => 'nose right 1'
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include(match(/value for key '14-818' in average_measurements must be a positive float/))
      end

      it 'is invalid with string' do
        arkit = {
          'average_measurements' => {
            '14-818' => {
              'value' => 'not a number',
              'description' => 'nose right 1'
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include(match(/value for key '14-818' in average_measurements must be a positive float/))
      end

      it 'is invalid with nil' do
        arkit = {
          'average_measurements' => {
            '14-818' => {
              'value' => nil,
              'description' => 'nose right 1'
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include(match(/value for key '14-818' in average_measurements must be a positive float/))
      end
    end

    context 'when description key is missing' do
      it 'is invalid' do
        arkit = {
          'average_measurements' => {
            '14-818' => {
              'value' => 123.45
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include('hash for key \'14-818\' in average_measurements must have \'description\' key')
      end
    end

    context 'when description is not a string' do
      it 'is invalid with integer' do
        arkit = {
          'average_measurements' => {
            '14-818' => {
              'value' => 123.45,
              'description' => 123
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include(match(/description for key '14-818' in average_measurements must be a string/))
      end

      it 'is invalid with hash' do
        arkit = {
          'average_measurements' => {
            '14-818' => {
              'value' => 123.45,
              'description' => { 'key' => 'value' }
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include(match(/description for key '14-818' in average_measurements must be a string/))
      end

      it 'is invalid with nil' do
        arkit = {
          'average_measurements' => {
            '14-818' => {
              'value' => 123.45,
              'description' => nil
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit]).to include(match(/description for key '14-818' in average_measurements must be a string/))
      end
    end

    context 'with multiple measurement entries' do
      it 'validates all entries' do
        arkit = {
          'average_measurements' => {
            '14-818' => {
              'value' => 123.45,
              'description' => 'nose right 1'
            },
            '15-819' => {
              'value' => -234.56, # invalid: negative
              'description' => 'nose right 2'
            },
            'invalid-key' => { # invalid: wrong format
              'value' => 345.67,
              'description' => 'nose right 3'
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).not_to be_valid
        expect(measurement.errors[:arkit].length).to be >= 2
        expect(measurement.errors[:arkit]).to include(match(/value for key '15-819'/))
        expect(measurement.errors[:arkit]).to include(match(/key in average_measurements must match pattern/))
      end

      it 'is valid when all entries are correct' do
        arkit = {
          'average_measurements' => {
            '14-818' => {
              'value' => 123.45,
              'description' => 'nose right 1'
            },
            '15-819' => {
              'value' => 234.56,
              'description' => 'nose right 2'
            },
            '16-820' => {
              'value' => 345.67,
              'description' => 'nose right 3'
            }
          }
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).to be_valid
      end
    end

    context 'with empty average_measurements hash' do
      it 'is valid' do
        arkit = {
          'average_measurements' => {}
        }
        measurement = described_class.new(
          user_id: user.id,
          arkit: arkit
        )
        expect(measurement).to be_valid
      end
    end
  end
end