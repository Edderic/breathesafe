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
    debugger
    results = JSON.parse(
      ActiveRecord::Base.connection.exec_query(
        <<-SQL
        SELECT *, mks.uuid as mask_kit_uuid
        FROM masks
        INNER JOIN mask_kit_statuses mks
          ON mks.mask_uuid = masks.id
        INNER JOIN shipping_status_joins ssj
          ON ssj.shippable_uuid = mks.uuid
        INNER JOIN shipping_statuses ss
          ON ss.uuid = ssj.shipping_uuid
        INNER JOIN users
          ON users.email = ss.to_user_uuid
        INNER JOIN managed_users mu
          ON mu.manager_id = users.id

        WHERE masks.id = #{mask_id}
          AND mu.managed_id = #{managed_user_id}
          AND users.admin = false
        SQL
      ).to_json
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
