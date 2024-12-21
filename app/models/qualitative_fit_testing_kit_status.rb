class QualitativeFitTestingKitStatus < ApplicationRecord
  def self.refresh!(datetime: nil)
    if datetime.nil?
      datetime = DateTime.now
    end

    qlft_kit_status = QualitativeFitTestingKitStatusBuilder.build

    uuid = qlft_kit_status.keys[0]
    qlft_kit = QualitativeFitTestingKitStatus.create(uuid: uuid)

    qlft_kit_status.each do |uuid, kit|

      kit['solution_uuids'].each do |sol_uuid|
        QualitativeFitTestingKitJoin.create!(
          qlft_kit_uuid: qlft_kit.uuid,
          part_type: 'SolutionStatus',
          part_uuid: sol_uuid,
          refresh_datetime: datetime
        )
      end

      kit['hood_uuids'].each do |hood_uuid|
        QualitativeFitTestingKitJoin.create!(
          qlft_kit_uuid: qlft_kit.uuid,
          part_type: 'HoodStatus',
          part_uuid: hood_uuid,
          refresh_datetime: datetime
        )
      end

      kit['nebulizer_uuids'].each do |nebulizer_uuid|
        QualitativeFitTestingKitJoin.create!(
          qlft_kit_uuid: qlft_kit.uuid,
          part_type: 'NebulizerStatus',
          part_uuid: nebulizer_uuid,
          refresh_datetime: datetime
        )
      end
    end
  end
end
