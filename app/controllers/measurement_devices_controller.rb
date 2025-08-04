# frozen_string_literal: true

# Controller enabling CRUD operations for MeasurementDevices
class MeasurementDevicesController < ApplicationController
  skip_before_action :verify_authenticity_token

  def create
    if unauthorized?
      status = 401
      messages = ['Unauthorized.']
      measurement_device = {}
    else
      hashed_measurement_device_data = measurement_device_data.to_hash
      hashed_measurement_device_data[:owner_id] = current_user.id
      measurement_device = MeasurementDevice.create(hashed_measurement_device_data)

      if measurement_device.errors.full_messages.empty?
        status = 201
        messages = []
      else
        status = 422
        messages = measurement_device.errors.full_messages
        measurement_device = {}
      end
    end

    to_render = {
      measurement_device: measurement_device,
      messages: messages
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def index
    to_render = {
      measurement_devices: MeasurementDevice.viewable(current_user)
    }
    messages = []

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status, messages: messages
      end
    end
  end

  def show
    # TODO: For now, only current user can access facial measurements
    # Later on, parents should be able to view / edit their children's data
    messages = []
    status = 200

    unless current_user
      status = 401
      messages = ['Unauthorized.']
      to_render = {}
    end

    measurement_device = MeasurementDevice.find(params[:id])

    unless current_user.manages?(measurement_device.owner)
      measurement_device = {}
      messages = ['Unauthorized.']
    end

    to_render = {
      measurement_device: measurement_device,
      messages: messages
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def update
    # TODO: For now, only current user can access facial measurements
    # Later on, parents should be able to view / edit their children's data
    unless current_user
      status = 401
      messages = ['Unauthorized.']
      to_render = {}
    end

    measurement_device = MeasurementDevice.find(params[:id])

    # TODO: admins should be able to update data no matter who owns it.
    if measurement_device.owner_id != current_user.id
      status = 401
      to_render = {}
      messages = ['Current user is not the owner.']
    elsif measurement_device.update(measurement_device_data)
      status = 204
      to_render = {}
      messages = []
    else
      status = 400 # bad request
      messages = []
    end

    to_render = {
      messages: messages,
      measurement_device: measurement_device
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def delete
    unless current_user
      status = 401
      to_render = {}
    end

    measurement_device_data = MeasurementDevice.viewable(
      current_user,
      params[:id]
    )[0]

    measurement_device = MeasurementDevice.find(measurement_device_data['id'])

    if measurement_device['owner_id'] != current_user.id
      status = 401
      messages = ['Current user is not the MeasurementDevice author.']
      to_render = {
        messages: messages
      }
    elsif measurement_device_data['num_fit_tests'].positive?
      status = 401
      to_render = {
        messages: ['Cannot delete a measurement_device that already has a Fit Test assigned to it.']
      }
    elsif measurement_device.delete
      status = 200
      messages = []
      to_render = {
        messages: messages
      }
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def measurement_device_data
    params.require(:measurement_device).permit(
      :measurement_device_type,
      :model,
      :manufacturer,
      :serial,
      :notes,
      :remove_from_service
    )
  end
end
