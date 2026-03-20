# frozen_string_literal: true

module Admin
  class FitFamiliesController < ApplicationController
    before_action :authenticate_user!
    before_action :ensure_admin

    def index
      fit_families = FitFamily.order(:name).includes(:masks)

      render json: {
        fit_families: fit_families.map do |fit_family|
          {
            id: fit_family.id,
            name: fit_family.name,
            slug: fit_family.slug,
            mask_count: fit_family.masks.size,
            mismatch_summary: mismatch_summary_for(fit_family)
          }
        end
      }, status: :ok
    end

    def create
      fit_family = FitFamily.create!(
        name: fit_family_params[:name],
        slug: next_slug_for(fit_family_params[:name])
      )

      render json: {
        fit_family: {
          id: fit_family.id,
          name: fit_family.name,
          slug: fit_family.slug,
          mask_count: 0
        }
      }, status: :created
    rescue ActiveRecord::RecordInvalid => e
      render json: { error: e.record.errors.full_messages.to_sentence }, status: :unprocessable_entity
    end

    private

    def fit_family_params
      params.require(:fit_family).permit(:name)
    end

    def next_slug_for(name)
      base = name.to_s.parameterize.presence || 'fit-family'
      slug = base
      suffix = 2

      while FitFamily.exists?(slug: slug)
        slug = "#{base}-#{suffix}"
        suffix += 1
      end

      slug
    end

    def ensure_admin
      return if current_user&.admin?

      render json: { error: 'Unauthorized' }, status: :forbidden
    end

    def mismatch_summary_for(fit_family)
      {
        perimeter_mm: distinct_values_for(fit_family, :perimeter_mm),
        style: distinct_values_for(fit_family, :style),
        strap_type: distinct_values_for(fit_family, :strap_type)
      }.transform_values do |values|
        {
          mismatch: values.size > 1,
          values: values
        }
      end
    end

    def distinct_values_for(fit_family, attribute)
      fit_family.masks.filter_map do |mask|
        value = mask.public_send(attribute)
        next if value.blank?

        value
      end.uniq.sort_by(&:to_s)
    end
  end
end
