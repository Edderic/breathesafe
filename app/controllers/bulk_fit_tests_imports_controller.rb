# frozen_string_literal: true

class BulkFitTestsImportsController < ApplicationController
  def create
    if unauthorized?
      status = 401
      messages = ['Unauthorized.']
      bulk_import = {}
    else
      bulk_import = BulkFitTestsImport.create(
        bulk_import_params.merge(user: current_user)
      )

      if bulk_import.persisted?
        status = 201
        messages = []
      else
        status = 422
        messages = bulk_import.errors.full_messages
        bulk_import = {}
      end
    end

    to_render = {
      bulk_fit_tests_import: bulk_import,
      messages: messages
    }

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def show
    bulk_import = BulkFitTestsImport.find(params[:id])

    if unauthorized?
      status = 401
      messages = ['Unauthorized.']
      to_render = {}
    elsif !current_user.manages?(bulk_import.user)
      status = 422
      messages = ['Unauthorized.']
      to_render = {}
    else
      status = 200
      messages = []
      to_render = {
        bulk_fit_tests_import: JSON.parse(bulk_import.to_json),
        messages: messages
      }
    end

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  private

  def bulk_import_params
    params.require(:bulk_fit_tests_import).permit(
      :source_name,
      :source_type,
      :import_data,
      :status,
      column_matching_mapping: {},
      mask_matching: {},
      user_seal_check_matching: {},
      fit_testing_matching: {}
    )
  end
end
