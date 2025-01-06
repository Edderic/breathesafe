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
        manager_user_id: manager_user_id,
        mask_id: mask_id
      )
      if results.count == 1
        mask_kit_uuid = results[0]['mask_kit_uuid']

        MaskKitAction.create(
          name: 'RemoveMasks',
          datetime: DateTime.now,
          metadata: {
            uuid: mask_kit_uuid,
            mask_uuids: [
              mask_id.to_i
            ],
          }
        )

        MaskKitStatus.where(uuid: mask_kit_uuid).destroy_all
        MaskKitStatus.refresh!(uuid: mask_kit_uuid)

        status = 200
      else
        # https://stackoverflow.com/questions/17884469/what-is-the-http-response-code-for-failed-http-delete-operation
        status = 405
      end
    end

    # TODO:
    #   display that the mask was "not received" under the "Untested" tab

    to_render = {}

    respond_to do |format|
      format.json do
        render json: to_render.to_json, status: status
      end
    end
  end
end
