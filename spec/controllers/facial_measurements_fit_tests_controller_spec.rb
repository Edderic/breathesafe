# frozen_string_literal: true

require 'rails_helper'

RSpec.describe FacialMeasurementsFitTestsController, type: :controller do
  include Devise::Test::ControllerHelpers

  let(:user) { create(:user) }
  let(:manager) { create(:user) }

  let(:profile) do
    create(:profile, user: user)
  end

  let(:facial_measurement) { create(:facial_measurement, user: user) }
  let(:measurement_device) { create(:measurement_device) }

  let(:mask) do
    create(:mask)
  end

  before do
    # Set up manager-managed relationship
    profile
    create(:managed_user, manager: manager, managed: user)
  end

  describe 'POST #create' do
    context 'when user is not authenticated' do
      it 'returns unauthorized status' do
        post :create, params: { facial_measurement_id: facial_measurement.id }, format: :json
        expect(response).to have_http_status(:unauthorized)
      end
    end

    context 'when facial measurement does not exist' do
      before { sign_in manager }

      it 'returns unauthorized status' do
        post :create, params: { facial_measurement_id: 999_999 }, format: :json
        expect(response).to have_http_status(:unauthorized)
      end


      it 'includes correct messaging' do
        post :create, params: { facial_measurement_id: 999_999 }, format: :json
        expect(JSON.parse(response.body)['messages']).to include('No facial measurement found for this id.')
      end
    end

    context 'when user is not authorized to manage the facial measurement owner' do
      let(:unauthorized_user) { create(:user) }

      before { sign_in unauthorized_user }

      it 'returns unauthorized status' do
        post :create, params: { facial_measurement_id: facial_measurement.id }, format: :json
        expect(response).to have_http_status(:unauthorized)
        expect(JSON.parse(response.body)['messages']).to include('Unauthorized.')
      end
    end

    context 'when user is authorized' do
      before { sign_in manager }

      context 'when user has existing fit tests' do
        let!(:fit_test1) do
          create(:fit_test,
                 :with_just_right_mask,
                 user: user,
                 quantitative_fit_testing_device: measurement_device,
                 facial_measurement: nil)
        end
        let!(:fit_test2) do
          create(:fit_test,
                 :with_just_right_mask,
                 user: user,
                 quantitative_fit_testing_device: measurement_device,
                 facial_measurement: nil)
        end

        it 'assigns facial measurement to all user fit tests' do
          post :create, params: { facial_measurement_id: facial_measurement.id }, format: :json

          expect(response).to have_http_status(:created)
          expect(JSON.parse(response.body)['messages']).to include('Successfully assigned latest facial measurement to past fit tests.')

          # Verify fit tests were updated
          expect(fit_test1.reload.facial_measurement_id).to eq(facial_measurement.id)
          expect(fit_test2.reload.facial_measurement_id).to eq(facial_measurement.id)
        end
      end

      context 'when user has no fit tests' do
        it 'returns success status' do
          post :create, params: { facial_measurement_id: facial_measurement.id }, format: :json

          expect(response).to have_http_status(:created)
          expect(JSON.parse(response.body)['messages']).to include('Successfully assigned latest facial measurement to past fit tests.')
        end
      end
    end
  end

  describe 'GET #index' do
    context 'when user is authenticated' do
      before { sign_in manager }

      let!(:n95_fit_test) do
        create(:fit_test,
               :with_just_right_mask,
               user: user,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'quantitative' => {
                   'testing_mode' => 'N95',
                   'exercises' => [
                     {
                       'name' => 'Normal breathing',
                       'fit_factor' => '200'
                     }
                   ]
                 }
               })
      end

      let!(:n99_fit_test) do
        create(:fit_test,
               :with_just_right_mask,
               user: user,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'quantitative' => {
                   'testing_mode' => 'N99',
                   'exercises' => [
                     {
                       'name' => 'Normal breathing',
                       'fit_factor' => '200'
                     },
                     {
                       'name' => 'Normal breathing (SEALED)',
                       'fit_factor' => '200'
                     }
                   ]
                 }
               })
      end

      let!(:qlft_fit_test) do
        create(:fit_test,
               :with_just_right_mask,
               user: user,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'qualitative' => {
                   'exercises' => [
                     {
                       'name' => 'Normal breathing',
                       'result' => 'Pass'
                     }
                   ]
                 }
               })
      end

      it 'returns all fit tests with facial measurements' do
        get :index, format: :json

        expect(response).to have_http_status(:ok)
        result = JSON.parse(response.body)['fit_tests_with_facial_measurements']

        # Verify all three types of fit tests are included
        expect(result.length).to eq(3)

        # Verify each fit test has facial measurement data
        result.each do |fit_test|
          expect(fit_test['face_width']).to be_present
          expect(fit_test['jaw_width']).to be_present
          expect(fit_test['face_depth']).to be_present
          expect(fit_test['face_length']).to be_present
          expect(fit_test['lower_face_length']).to be_present
          expect(fit_test['bitragion_menton_arc']).to be_present
          expect(fit_test['bitragion_subnasale_arc']).to be_present
          expect(fit_test['nasal_root_breadth']).to be_present
          expect(fit_test['nose_protrusion']).to be_present
          expect(fit_test['nose_bridge_height']).to be_present
          expect(fit_test['lip_width']).to be_present
          expect(fit_test['head_circumference']).to be_present
          expect(fit_test['nose_breadth']).to be_present
        end
      end
    end
  end

  describe 'GET #show' do
    context 'when user is not authenticated' do
      let!(:n95_fit_test) do
        create(:fit_test,
               :with_just_right_mask,
               mask: mask,
               user: user,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'quantitative' => {
                   'testing_mode' => 'N95',
                   'exercises' => [
                     {
                       'name' => 'Normal breathing',
                       'fit_factor' => '200'
                     }
                   ]
                 }
               })
      end

      it 'returns fit tests for the specified mask' do
        get :show, params: { mask_id: mask.id }, format: :json
        expect(response).to have_http_status(:ok)

        json_response = JSON.parse(response.body)
        expect(json_response['fit_tests_with_facial_measurements']).to be_an(Array)
        expect(json_response['fit_tests_with_facial_measurements'].length).to eq(1)

        result = json_response['fit_tests_with_facial_measurements'].first
        expect(result['mask_id']).to eq(mask.id)
        expect(result['id']).to eq(n95_fit_test.id)
      end

      it 'returns empty array when mask has no fit tests' do
        other_mask = create(:mask)
        get :show, params: { mask_id: other_mask.id }, format: :json

        expect(response).to have_http_status(:ok)
        json_response = JSON.parse(response.body)
        expect(json_response['fit_tests_with_facial_measurements']).to be_empty
      end

      it 'handles invalid mask_id gracefully' do
        get :show, params: { mask_id: 'invalid_id' }, format: :json
        expect(response).to have_http_status(:ok)

        json_response = JSON.parse(response.body)
        expect(json_response['fit_tests_with_facial_measurements']).to be_empty
      end

      it 'sanitizes the mask_id parameter' do
        malicious_mask_id = '1; DROP TABLE users; --'
        expect do
          get :show, params: { mask_id: malicious_mask_id }, format: :json
        end.not_to raise_error

        expect(response).to have_http_status(:ok)
      end
    end

    context 'when user is authenticated' do
      let!(:n95_fit_test) do
        create(:fit_test,
               :with_just_right_mask,
               user: user,
               mask: mask,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: facial_measurement,
               results: {
                 'quantitative' => {
                   'testing_mode' => 'N95',
                   'exercises' => [
                     {
                       'name' => 'Normal breathing',
                       'fit_factor' => '200'
                     }
                   ]
                 }
               })
      end

      before do
        sign_in user
      end

      it 'returns fit tests for the specified mask' do
        get :show, params: { mask_id: mask.id }, format: :json
        expect(response).to have_http_status(:ok)

        json_response = JSON.parse(response.body)
        expect(json_response['fit_tests_with_facial_measurements']).to be_an(Array)
        expect(json_response['fit_tests_with_facial_measurements'].length).to eq(1)

        result = json_response['fit_tests_with_facial_measurements'].first
        expect(result['mask_id']).to eq(mask.id)
        expect(result['id']).to eq(n95_fit_test.id)
      end
    end
  end
end
