require 'rails_helper'

RSpec.describe MaskMatching::Scorer do
  def score_for(file_components, mask_components)
    described_class.score(file_components, mask_components)[:score]
  end

  describe 'age group handling' do
    it 'heavily penalizes adult vs kids mismatches' do
      adult_row = { brand: ['WellBefore'], model: ['Wellbefore 3D KN95 Adult Regular'] }
      kids_catalog = { brand: ['WellBefore'], model: ['Wellbefore Kids KN95 Petite Regular'] }

      expect(score_for(adult_row, kids_catalog)).to be < 0.2
    end

    it 'defaults unspecified from-file rows to adult to avoid matching kids masks' do
      unspecified_row = { brand: ['WellBefore'], model: ['Wellbefore KN95'] }
      kids_catalog = { brand: ['WellBefore'], model: ['Wellbefore Kids KN95 Petite Regular'] }

      expect(score_for(unspecified_row, kids_catalog)).to be < 0.2
    end
  end

  describe 'size conflicts' do
    it 'penalizes mismatched explicit sizes' do
      file_components = { brand: ['Laianzhi'], model: ['HYX1002'], size: ['Small'] }
      catalog_components = { brand: ['Laianzhi'], model: ['HYX1002'], size: ['Large'] }

      expect(score_for(file_components, catalog_components)).to be < 0.2
    end

    it 'keeps matching sizes above the threshold' do
      file_components = { brand: ['Laianzhi'], model: ['HYX1002'], size: ['Small'] }
      catalog_components = { brand: ['Laianzhi'], model: ['HYX1002'], size: ['Small'] }

      expect(score_for(file_components, catalog_components)).to be > 0.6
    end
  end

  describe 'brand and model heuristics' do
    it 'infers brands from distinctive model numbers when missing' do
      file_components = { model: ['Aura 9210+'] }
      catalog_components = { brand: ['3M'], model: ['Aura 9210+'] }

      expect(score_for(file_components, catalog_components)).to be > 0.7
    end

    it 'prevents dissimilar brands from matching even with similar strings' do
      file_components = { brand: ['Readimask'], model: ['Readimask Small'] }
      catalog_components = { brand: ['Medimask'], model: ['KF95 Korea Filter'] }

      expect(score_for(file_components, catalog_components)).to be < 0.2
    end
  end
end
