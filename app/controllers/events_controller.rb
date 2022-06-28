class EventsController < ApplicationController
  def new
    respond_to do |format|
      format.html do
        gon.GOOGLE_MAPS_API_KEY = ENV['GOOGLE_MAPS_API_KEY']
      end

      format.json do
        render json: {
          projects: projects
        }.to_json
      end
    end
  end
end
