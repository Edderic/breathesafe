# frozen_string_literal: true

require 'rails_helper'

def get_zscores(keys, manager_id: nil)
  # Get the latest facial measurements per user, filtered by manager if provided
  measurements = if manager_id
                   managed_user_ids = ManagedUser.where(manager_id: manager_id).pluck(:managed_id)
                   FacialMeasurement.where(user_id: managed_user_ids)
                 else
                   FacialMeasurement.all
                 end

  %i[id user_id created_at] | keys
  facial_measurements_by_user = measurements.group_by(&:user_id)
  deduped_measurements = facial_measurements_by_user.each_with_object([]) do |(_key, value), accum|
    row = value.max_by(&:id)
    accum << row
  end

  means_and_std = keys.map do |key|
    values = deduped_measurements.map(&key).map(&:to_f)
    mean = values.sum / values.length
    e_of_x_squared = values.map { |v| v**2 }.sum / values.length
    mean_squared = mean**2
    std = Math.sqrt(e_of_x_squared - mean_squared)
    {
      key: key,
      "mean": mean,
      "std": std
    }
  end

  deduped_measurements.each_with_object([]) do |m, accum|
    new_m = JSON.parse(m.to_json).with_indifferent_access

    means_and_std.each do |s|
      value = new_m[s[:key]]
      new_m["#{s[:key]}_z_score"] = value.nil? ? nil : (value.to_f - s[:mean]) / s[:std]
    end
    accum << new_m
  end
end

RSpec.describe FacialMeasurementOutliersService do
  let(:manager) { create(:user, :with_profile) }
  let(:user) { create(:user, :with_profile) }
  let(:other_user) { create(:user, :with_profile) }
  let(:unrelated_user) { create(:user, :with_profile) }

  describe '.call' do
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
             lip_width: 50,
             created_at: 2.days.ago)
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
             lip_width: 55,
             created_at: 1.day.ago)
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
             lip_width: 1000,
             created_at: 2.days.ago)
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
             lip_width: 52,
             created_at: 1.day.ago)
    end

    let(:fit_test_1) do
      create(:fit_test,
             user: user,
             facial_measurement: measurement2)
    end

    let(:fit_test_2) do
      create(:fit_test,
             user: other_user,
             facial_measurement: other_user_measurement)
    end

    let(:fit_test_3) do
      create(:fit_test,
             user: other_user,
             facial_measurement: other_user_measurement)
    end

    before do
      # Create managed user relationships
      create(:managed_user, manager: manager, managed: user)
      create(:managed_user, manager: manager, managed: other_user)

      fit_test_1
      fit_test_2
      fit_test_3
    end

    context 'with multiple measurements for a user' do
      it 'calculates z-scores and returns latest measurements per user' do
        results = described_class.call(manager_id: manager.id).to_a
        measurements_list = %i[face_width jaw_width face_depth]

        # Check measurement2's z-scores (latest measurement for user)
        measurement2_result = results.find { |r| r['id'] == measurement2.id }

        zscores = get_zscores(measurements_list, manager_id: manager.id)
        expected_measurement2_zscores = zscores.find { |m| m[:id] == measurement2_result['id'] }

        measurements_list.each do |m|
          expect(measurement2_result["#{m}_z_score"]).to be_within(0.03)\
            .of(expected_measurement2_zscores["#{m}_z_score"])
        end

        # Check other_user_measurement's z-scores (latest measurement for other_user)
        other_user_result = results.find { |r| r['id'] == other_user_measurement.id }
        expected_other_user_zscores = zscores.find { |m| m[:id] == other_user_result['id'] }

        measurements_list.each do |m|
          expect(other_user_result["#{m}_z_score"]).to be_within(0.03)\
            .of(expected_other_user_zscores["#{m}_z_score"])
        end

        # Verify measurement1 is not returned (not the latest for user)
        measurement1_result = results.find { |r| r['id'] == measurement1.id }
        expect(measurement1_result).to be_nil
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
               lip_width: 50)
      end

      let(:fit_test_1) do
        create(:fit_test,
               user: user,
               facial_measurement: measurement)
      end

      before do
        fit_test_1
      end

      it 'returns null z-scores for null measurements' do
        results = described_class.call(manager_id: manager.id).to_a
        result = results.find { |row| row['id'] == measurement.id }

        expect(result['jaw_width_z_score']).to be_nil
        expect(result['face_length_z_score']).to be_nil
        expect(result['bitragion_subnasale_arc_z_score']).to be_nil
        expect(result['nose_bridge_height_z_score']).to be_nil
      end
    end

    context 'with no measurements' do
      let(:no_measurements_manager) { create(:user, :with_profile) }
      let(:no_measurements_user) { create(:user, :with_profile) }

      before do
        create(:managed_user, manager: no_measurements_manager, managed: no_measurements_user)
      end

      it 'returns empty array' do
        results = described_class.call(manager_id: no_measurements_manager.id).to_a
        expect(results).to be_empty
      end
    end

    context 'with manager_id scoping' do
      let!(:unrelated_measurement) do
        create(:facial_measurement,
               user: unrelated_user,
               face_width: 200,
               jaw_width: 180,
               face_depth: 150,
               face_length: 250,
               lower_face_length: 90,
               bitragion_menton_arc: 400,
               bitragion_subnasale_arc: 350,
               nasal_root_breadth: 30,
               nose_protrusion: 30,
               nose_bridge_height: 25,
               lip_width: 70,
               created_at: 1.day.ago)
      end

      let(:unrelated_fit_test) do
        create(:fit_test,
               user: unrelated_user,
               facial_measurement: unrelated_measurement)
      end

      before do
        unrelated_fit_test
      end

      it 'only returns measurements for users managed by the specified manager' do
        results = described_class.call(manager_id: manager.id).to_a
        # Should only include measurements for user and other_user (managed by manager)
        user_ids = results.map { |r| r['user_id'] }
        expect(user_ids).to include(user.id, other_user.id)
        expect(user_ids).not_to include(unrelated_user.id)
      end

      it 'returns empty array when manager has no managed users' do
        other_manager = create(:user)
        results = described_class.call(manager_id: other_manager.id).to_a
        expect(results).to be_empty
      end

      it 'returns all measurements when no manager_id is provided' do
        results = described_class.call.to_a

        # Should include all measurements
        user_ids = results.map { |r| r['user_id'] }
        expect(user_ids).to include(user.id, other_user.id, unrelated_user.id)
      end
    end

    context 'with bounds filtering' do
      let!(:lower_bound_measurement) do
        create(:facial_measurement,
               user: create(:user, :with_profile),
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
               lip_width: 50)
      end

      let!(:upper_bound_measurement) do
        create(:facial_measurement,
               user: create(:user, :with_profile),
               face_width: 170,
               jaw_width: 150,
               face_depth: 130,
               face_length: 220,
               lower_face_length: 80,
               bitragion_menton_arc: 350,
               bitragion_subnasale_arc: 300,
               nasal_root_breadth: 25,
               nose_protrusion: 25,
               nose_bridge_height: 20,
               lip_width: 60)
      end

      it 'filters measurements based on lower and upper bounds' do
        results = described_class.call(
          manager_id: manager.id,
          facial_measurement_id_of_lower_bound: lower_bound_measurement.id,
          facial_measurement_id_of_upper_bound: upper_bound_measurement.id
        ).to_a

        # measurement2 should be included (within bounds)
        measurement2_result = results.find { |r| r['id'] == measurement2.id }
        expect(measurement2_result).not_to be_nil

        # other_user_measurement should be included (within bounds)
        other_user_result = results.find { |r| r['id'] == other_user_measurement.id }
        expect(other_user_result).not_to be_nil

        # facial_measurement_not_associated_to_fit_test should be excluded (outside bounds)
        outlier_result = results.find { |r| r['id'] == facial_measurement_not_associated_to_fit_test.id }
        expect(outlier_result).to be_nil
      end
    end
  end
end
