class Users::CarbonDioxideMonitorsController < ApplicationController
  skip_before_action :verify_authenticity_token

  def index
    if !authorized?
      status = 401
      co2_monitors = []
    else
      status = 200
      co2_monitors = current_user.carbon_dioxide_monitors
    end

    respond_to do |format|
      format.json do
        render json: {
          'carbonDioxideMonitors': co2_monitors
        }.to_json, status: status
      end
    end
  end

  def create_or_update
    # TODO: check that user specified is the current user
    message = "created"
    successful = true
    updated = false

    co2_monitor = CarbonDioxideMonitor.find_by('serial': co2_monitor_data['serial'])

    if !authorized?
      message = 'Unauthorized'
      status = 401
    elsif co2_monitor
      updated = co2_monitor.update(co2_monitor_data)
      if updated
        message = "Updated data for CO2 Monitor with serial #{co2_monitor.serial}"
        status = 200
      else
        message = "Failed to update CO2 Monitor with serial #{co2_monitor.serial}"
        status = 200
      end
    else
      c = false
      u = false

      ActiveRecord::Base.transaction do
        c = CarbonDioxideMonitor.create!(co2_monitor_data)
        u = UserCarbonDioxideMonitor.create!( user_id: current_user.id, serial: c.serial, model: c.model)
      end

      if !!c and !!u
        message = "Successfully created CO2 Monitor with serial #{c.serial}"
        status = 200
      else
        message = "Failed to create CO2 Monitor with serial #{co2_monitor_data['serial']}"
        status = 200
      end
    end

    respond_to do |format|
      format.json do
        render json: {
          message: message
        }.to_json, status: status, content_type: 'application/json'
      end
    end
  end

  def delete
    if !authorized?
      message = 'unauthorized'
      status = 401
    else
      co2_monitor = CarbonDioxideMonitor.find(params.require("carbon_dioxide_monitor_id"))
      user_monitors = UserCarbonDioxideMonitor.where(serial: co2_monitor.serial)

      message = ""
      if user_monitors.size > 1
        # Just delete the user monitor
        user_monitors.first.destroy
        message = "Deleted association between current user and monitor with serial #{co2_monitor.serial}."
      else
        user_monitor = UserCarbonDioxideMonitor.find_by(
          model: co2_monitor.model,
          serial: co2_monitor.serial,
          user_id: current_user.id
        )

        begin
          ActiveRecord::Base.transaction do
            user_monitor.destroy!
            co2_monitor.destroy!
          end

          message = "Deleted association between current user and monitor with serial #{co2_monitor.serial}, and the monitor itself. Note: you will not be able to add new measurements of venues without a CO₂ monitor. Please add at least one."
        rescue StandardError => e
          message = "Something went wrong with the deletion of CO2 monitor and the relationship between CO2 monitor and current user."
        end
      end
    end

    respond_to do |format|
      format.json do
        render json: {
          message: message
        }.to_json
      end
    end
  end

  private

  def authorized?
    current_user.id == params.require('user_id').to_i
  end

  def co2_monitor_data
    params.require("carbonDioxideMonitor").permit("serial", "model", "name")
  end
end
