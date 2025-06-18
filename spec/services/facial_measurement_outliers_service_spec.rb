require 'rails_helper'

def get_zscores(keys)
  facial_measurement_id = FitTest.all.select(:facial_measurement_id)
  measurements = FacialMeasurement.where(id: facial_measurement_id)
  copy_measurements = measurements.map do |m|
    copy = {
      id: m.id,
    }
    keys.each do |key|
      copy[key] = m.send(key)
    end

    copy
  end

  means_and_std = keys.map do |key|
    mean = measurements.map(&key).sum() / measurements.length
    e_of_x_squared = measurements.map{|m| m.send(key)** 2}.sum() / measurements.length
    mean_squared = mean**2
    std = Math.sqrt(e_of_x_squared - mean_squared)
    {
      key: key,
      "mean": mean,
      "std": std,
    }
  end

  copy_measurements.reduce([]) do |accum, m|

    means_and_std.each do |s|
      m["#{s[:key]}_z_score"] = (m[s[:key]] - s[:mean]) / s[:std]
    end
    accum << m
    accum
  end
end

RSpec.describe FacialMeasurementOutliersService do
  let(:user) { create(:user) }
  let(:other_user) { create(:user) }

  describe '.call' do
    context 'with multiple measurements for a user' do
      let!(:fit_test_1) do
        create(:fit_test,
          user: user,
          facial_measurement: measurement1
        )
      end

      let!(:fit_test_2) do
        create(:fit_test,
          user: other_user,
          facial_measurement: measurement2
        )
      end

      let!(:fit_test_3) do
        create(:fit_test,
          user: other_user,
          facial_measurement: other_user_measurement
        )
      end

      let!(:measurement1) do
        create(:facial_measurement,
          user: user,
          face_width: 150,
          jaw_width: 130,
          face_depth: 110,
          face_length: 200,
          lower_face_length: 70,
          bitragion_menton_arc: 330,
          bitragion_subnasale_arc: 280,
          nasal_root_breadth: 20,
          nose_protrusion: 20,
          nose_bridge_height: 15,
          lip_width: 50
        )
      end

      let!(:measurement2) do
        create(:facial_measurement,
          user: user,
          face_width: 160,
          jaw_width: 140,
          face_depth: 120,
          face_length: 210,
          lower_face_length: 75,
          bitragion_menton_arc: 340,
          bitragion_subnasale_arc: 290,
          nasal_root_breadth: 22,
          nose_protrusion: 22,
          nose_bridge_height: 17,
          lip_width: 55
        )
      end

      let!(:other_user_measurement) do
        create(:facial_measurement,
          user: other_user,
          face_width: 155,
          jaw_width: 135,
          face_depth: 115,
          face_length: 205,
          lower_face_length: 72,
          bitragion_menton_arc: 335,
          bitragion_subnasale_arc: 285,
          nasal_root_breadth: 21,
          nose_protrusion: 21,
          nose_bridge_height: 16,
          lip_width: 52
        )
      end

      let!(:facial_measurement_not_associated_to_fit_test) do
        create(:facial_measurement,
          user: other_user,
          face_width: 1000,
          jaw_width: 1000,
          face_depth: 1000,
          face_length: 1000,
          lower_face_length: 1000,
          bitragion_menton_arc: 1000,
          bitragion_subnasale_arc: 1000,
          nasal_root_breadth: 1000,
          nose_protrusion: 1000,
          nose_bridge_height: 1000,
          lip_width: 1000
        )
      end

      it 'calculates z-scores and ignores facial measurements not associated to a fit test' do
        results = described_class.call.to_a
        measurements_list = [:face_width, :jaw_width, :face_depth]

        # Check first measurement's z-scores
        first_measurement = results.find { |r| r['id'] == measurement1.id }

        zscores = get_zscores(measurements_list)
        expected_first_measurement_zscores = zscores.find {|m| m[:id] == first_measurement['id']}

        measurements_list.each do |m|
          # puts("m: #{m}, first_measurement_zscore: #{first_measurement["#{m}_z_score"]}, expected: #{expected_first_measurement_zscores["#{m}_z_score"]}")
          expect(first_measurement["#{m}_z_score"]).to be_within(0.03)\
            .of(expected_first_measurement_zscores["#{m}_z_score"])
        end

        # Check second measurement's z-scores
        second_measurement = results.find { |r| r['id'] == measurement2.id }
        expected_second_measurement_zscores = zscores.find {|m| m[:id] == second_measurement['id']}

        measurements_list.each do |m|
          expect(second_measurement["#{m}_z_score"]).to be_within(0.03)\
            .of(expected_second_measurement_zscores["#{m}_z_score"])
        end
      end
    end

    context 'with null measurements' do
      let!(:measurement) do
        create(:facial_measurement,
          user: user,
          face_width: 150,
          jaw_width: nil,
          face_depth: 110,
          face_length: nil,
          lower_face_length: 70,
          bitragion_menton_arc: 330,
          bitragion_subnasale_arc: nil,
          nasal_root_breadth: 20,
          nose_protrusion: 20,
          nose_bridge_height: nil,
          lip_width: 50
        )
      end

      let!(:fit_test_1) do
        create(:fit_test,
          user: user,
          facial_measurement: measurement
        )
      end

      it 'returns null z-scores for null measurements' do
        results = described_class.call.to_a
        result = results.first

        expect(result['jaw_width_z_score']).to be_nil
        expect(result['face_length_z_score']).to be_nil
        expect(result['bitragion_subnasale_arc_z_score']).to be_nil
        expect(result['nose_bridge_height_z_score']).to be_nil
      end
    end

    context 'with no measurements' do
      it 'returns empty array' do
        results = described_class.call.to_a
        expect(results).to be_empty
      end
    end
  end
end
