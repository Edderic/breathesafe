# frozen_string_literal: true

# Controller featuring CRUD operations for MaskKits
class MaskKitController < ApplicationController
  skip_before_action :verify_authenticity_token

  def index
    managed_user_id = params[:managed_user_id]

    results = MaskKitQuery.masks_shipped_to(managed_id: managed_user_id)

    to_render = {
      data: results
    }

    status = 200

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end

  def delete
    mask_id = params[:mask_id]
    managed_user_id = params[:managed_user_id]

    if !current_user.manages?(User.find(managed_user_id))
      status = 401
    else
      results = MaskKitQuery.find_shipped_mask_accessible_to_managed_user(
        managed_user_id: managed_user_id,
        mask_id: mask_id
      )
      results.each do |res|
        mask_kit_uuid = res['mask_kit_uuid']

        MaskKitAction.create(
          name: 'RemoveMasks',
          datetime: DateTime.now,
          metadata: {
            uuid: mask_kit_uuid,
            mask_uuids: [
              mask_id.to_i
            ]
          }
        )

        MaskKitStatus.where(uuid: mask_kit_uuid).destroy_all
        MaskKitStatus.refresh!(uuid: mask_kit_uuid)
      end

      status = 200
    end

    to_render = {}

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end
end
