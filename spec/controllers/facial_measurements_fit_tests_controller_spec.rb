# frozen_string_literal: true

require 'rails_helper'

RSpec.describe FacialMeasurementsFitTestsController, type: :controller do
  include Devise::Test::ControllerHelpers

  let(:user) { create(:user) }
  let(:manager) { create(:user) }
  let(:admin) { create(:user, admin: true) }

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
      before do
        sign_in manager
      end

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
      end

      it 'responds with proper messaging' do
        post :create, params: { facial_measurement_id: facial_measurement.id }, format: :json
        expect(JSON.parse(response.body)['messages']).to include('Unauthorized.')
      end
    end

    context 'when user is authorized and has existing fit tests' do
      let!(:first_fit_test) do
        create(:fit_test,
               :with_just_right_mask,
               user: user,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: nil)
      end

      let!(:second_fit_test) do
        create(:fit_test,
               :with_just_right_mask,
               user: user,
               quantitative_fit_testing_device: measurement_device,
               facial_measurement: nil)
      end

      before do
        sign_in manager
        post :create, params: { facial_measurement_id: facial_measurement.id }, format: :json
      end

      it 'makes the response have created status' do
        expect(response).to have_http_status(:created)
      end

      it 'has a successful message' do
        expect(
          JSON.parse(response.body)['messages']
        ).to include('Successfully assigned latest facial measurement to past fit tests.')
      end

      it 'assigns facial measurement to the first fit test' do
        expect(first_fit_test.reload.facial_measurement_id).to eq(facial_measurement.id)
      end

      it 'assigns facial measurement to the second fit test' do
        expect(second_fit_test.reload.facial_measurement_id).to eq(facial_measurement.id)
      end
    end

    context 'when user is authorized and has no fit tests' do
      before do
        sign_in manager
        post :create, params: { facial_measurement_id: facial_measurement.id }, format: :json
      end

      it 'returns success status' do
        expect(JSON.parse(response.body)['messages']).to include(
          'Successfully assigned latest facial measurement to past fit tests.'
        )
      end

      it 'has a created response' do
        expect(response).to have_http_status(:created)
      end
    end
  end

  describe 'GET #index' do
    let(:n95_fit_test) do
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

    before do
      n95_fit_test
      n99_fit_test
      qlft_fit_test
    end

    context 'when user is not authenticated' do
      it 'returns unauthorized' do
        get :index, format: :json

        expect(response).to have_http_status(:unauthorized)
      end
    end

    context 'when user is authenticated but not admin' do
      before do
        sign_in manager
      end

      it 'returns forbidden' do
        get :index, format: :json

        expect(response).to have_http_status(:forbidden)
        expect(JSON.parse(response.body)['messages']).to include('Unauthorized. Admin access required.')
      end
    end

    context 'when user is admin' do
      before do
        sign_in admin
      end

      it 'returns all fit tests with facial measurements' do
        get :index, format: :json

        expect(response).to have_http_status(:ok)
        result = JSON.parse(response.body)['fit_tests_with_facial_measurements']

        # Verify rows are consolidated to one row per fit test
        expect(result.length).to eq(3)

        # Verify each fit test has facial measurement data
        result.each do |fit_test|
          expect(fit_test).to have_key('raw_mask_id')
          expect(fit_test['raw_mask_id']).to eq(fit_test['mask_id'])
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

    context 'when internal export token is valid' do
      before do
        request.headers['X-Breathesafe-Internal-Token'] = 'secret-token'
        allow(controller).to receive(:internal_export_token).and_return('secret-token')
      end

      it 'returns the dataset without a signed in user' do
        get :index, params: { internal_export: true }, format: :json

        expect(response).to have_http_status(:ok)
        expect(JSON.parse(response.body)['fit_tests_with_facial_measurements']).not_to be_empty
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

      it 'returns unauthorized' do
        get :show, params: { mask_id: mask.id }, format: :json
        expect(response).to have_http_status(:unauthorized)
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

      it 'returns forbidden for non-admin users' do
        sign_in user
        get :show, params: { mask_id: mask.id }, format: :json

        expect(response).to have_http_status(:forbidden)
      end
    end

    context 'when user is admin' do
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
        sign_in admin
      end

      it 'returns fit tests for the specified mask' do
        get :show, params: { mask_id: mask.id }, format: :json
        expect(response).to have_http_status(:ok)

        json_response = JSON.parse(response.body)
        expect(json_response['fit_tests_with_facial_measurements']).to be_an(Array)
        expect(json_response['fit_tests_with_facial_measurements'].length).to eq(1)

        results = json_response['fit_tests_with_facial_measurements']
        expect(results.map { |row| row['mask_id'] }.uniq).to eq([mask.id])
        expect(results.map { |row| row['raw_mask_id'] }.uniq).to eq([mask.id])
        expect(results.map { |row| row['id'] }).to include(n95_fit_test.id)
      end
    end
  end
end
