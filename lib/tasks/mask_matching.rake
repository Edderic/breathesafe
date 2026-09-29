# frozen_string_literal: true

namespace :mask_matching do
  desc 'Prepare cached component predictions for canonical catalog masks'
  task warm_catalog: :environment do
    WarmMaskMatchingCatalogJob.perform_later(Mask.where(duplicate_of: nil).pluck(:id))
  end
end
