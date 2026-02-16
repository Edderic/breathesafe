# frozen_string_literal: true

# MaskStatus represents the computed state of a mask at a specific point in time
# It's built by applying events to an initial state
class MaskStatus
  attr_reader :mask_id, :as_of_date, :attributes

  def initialize(mask_id:, as_of_date: Time.current)
    @mask_id = mask_id
    @as_of_date = as_of_date
    @attributes = {}
  end

  # Set the initial state from a MaskState record
  def apply_initial_state(mask_state)
    @attributes = mask_state.to_mask_attributes.deep_dup
    self
  end

  # Apply an event to modify the state
  def apply_event(event)
    case event.event_type
    when 'breakdown_updated'
      apply_breakdown_update(event)
    when 'color_changed'
      apply_color_change(event)
    when 'colors_updated'
      apply_colors_update(event)
    when 'duplicate_marked'
      apply_duplicate_marked(event)
    when 'perimeter_updated'
      apply_perimeter_update(event)
    when 'where_to_buy_urls_updated'
      apply_where_to_buy_urls_update(event)
    when 'filtration_efficiencies_updated'
      apply_filtration_efficiencies_update(event)
    when 'breathability_updated'
      apply_breathability_update(event)
    when 'style_updated'
      apply_style_update(event)
    when 'exhalation_valve_updated'
      apply_exhalation_valve_update(event)
    when 'unique_internal_model_code_updated'
      apply_unique_internal_model_code_update(event)
    when 'author_updated'
      apply_author_update(event)
    when 'brand_updated'
      apply_brand_update(event)
    when 'strap_type_updated'
      apply_strap_type_update(event)
    when 'image_urls_updated'
      apply_image_urls_update(event)
    when 'mass_updated'
      apply_mass_update(event)
    when 'dimensions_updated'
      apply_dimensions_update(event)
    when 'gasket_updated'
      apply_gasket_update(event)
    when 'cost_updated'
      apply_cost_update(event)
    when 'sources_updated'
      apply_sources_update(event)
    when 'modifications_updated'
      apply_modifications_update(event)
    when 'notes_updated'
      apply_notes_update(event)
    when 'filter_type_updated'
      apply_filter_type_update(event)
    when 'age_range_updated'
      apply_age_range_update(event)
    when 'payable_datetimes_updated'
      apply_payable_datetimes_update(event)
    when 'bulk_import_updated'
      apply_bulk_import_update(event)
    when 'availability_updated'
      apply_available_update(event)
    end

    self
  end

  # Serialize to a hash suitable for Mask.update
  def serialize
    @attributes.deep_dup
  end

  # Get a specific attribute
  def [](key)
    @attributes[key.to_s]
  end

  # Set a specific attribute
  def []=(key, value)
    @attributes[key.to_s] = value
  end

  private

  # Event application methods
  def apply_breakdown_update(event)
    @attributes['current_state'] ||= {}
    @attributes['current_state']['breakdown'] = event.data['breakdown']
  end

  def apply_color_change(event)
    @attributes['color'] = event.data['color']
  end

  def apply_colors_update(event)
    # Merge colors array
    @attributes['colors'] ||= []

    case event.data['action']
    when 'add'
      @attributes['colors'] |= Array(event.data['colors'])
    when 'remove'
      @attributes['colors'] -= Array(event.data['colors'])
    when 'set'
      @attributes['colors'] = event.data['colors']
    end
  end

  def apply_duplicate_marked(event)
    @attributes['duplicate_of'] = event.data['duplicate_of']
  end

  def apply_perimeter_update(event)
    @attributes['perimeter_mm'] = event.data['perimeter_mm']
  end

  def apply_where_to_buy_urls_update(event)
    @attributes['where_to_buy_urls'] ||= []

    case event.data['action']
    when 'add'
      @attributes['where_to_buy_urls'] |= Array(event.data['urls'])
    when 'remove'
      @attributes['where_to_buy_urls'] -= Array(event.data['urls'])
    when 'set'
      @attributes['where_to_buy_urls'] = event.data['urls']
    end
  end

  def apply_filtration_efficiencies_update(event)
    @attributes['filtration_efficiencies'] ||= []

    case event.data['action']
    when 'add'
      @attributes['filtration_efficiencies'] |= Array(event.data['efficiencies'])
    when 'remove'
      @attributes['filtration_efficiencies'] -= Array(event.data['efficiencies'])
    when 'set'
      @attributes['filtration_efficiencies'] = event.data['efficiencies']
    end
  end

  def apply_breathability_update(event)
    @attributes['breathability'] = event.data['breathability']
  end

  def apply_style_update(event)
    @attributes['style'] = event.data['style']
  end

  def apply_exhalation_valve_update(event)
    @attributes['has_exhalation_valve'] = event.data['has_exhalation_valve']
  end

  def apply_unique_internal_model_code_update(event)
    @attributes['unique_internal_model_code'] = event.data['unique_internal_model_code']
  end

  def apply_author_update(event)
    @attributes['author_id'] = event.data['author_id']
  end

  def apply_brand_update(event)
    @attributes['brand_id'] = event.data['brand_id']
  end

  def apply_strap_type_update(event)
    @attributes['strap_type'] = event.data['strap_type']
  end

  def apply_image_urls_update(event)
    @attributes['image_urls'] ||= []

    case event.data['action']
    when 'add'
      @attributes['image_urls'] |= Array(event.data['urls'])
    when 'remove'
      @attributes['image_urls'] -= Array(event.data['urls'])
    when 'set'
      @attributes['image_urls'] = event.data['urls']
    end
  end

  def apply_mass_update(event)
    @attributes['mass_grams'] = event.data['mass_grams']
  end

  def apply_dimensions_update(event)
    @attributes['height_mm'] = event.data['height_mm'] if event.data.key?('height_mm')
    @attributes['width_mm'] = event.data['width_mm'] if event.data.key?('width_mm')
    @attributes['depth_mm'] = event.data['depth_mm'] if event.data.key?('depth_mm')
  end

  def apply_gasket_update(event)
    @attributes['has_gasket'] = event.data['has_gasket']
  end

  def apply_cost_update(event)
    if event.data.key?('initial_cost_us_dollars')
      @attributes['initial_cost_us_dollars'] =
        event.data['initial_cost_us_dollars']
    end
    return unless event.data.key?('filter_change_cost_us_dollars')

    @attributes['filter_change_cost_us_dollars'] =
      event.data['filter_change_cost_us_dollars']
  end

  def apply_sources_update(event)
    @attributes['sources'] ||= []

    case event.data['action']
    when 'add'
      @attributes['sources'] |= Array(event.data['sources'])
    when 'remove'
      @attributes['sources'] -= Array(event.data['sources'])
    when 'set'
      @attributes['sources'] = event.data['sources']
    end
  end

  def apply_modifications_update(event)
    @attributes['modifications'] = event.data['modifications']
  end

  def apply_notes_update(event)
    @attributes['notes'] = event.data['notes']
  end

  def apply_filter_type_update(event)
    @attributes['filter_type'] = event.data['filter_type']
  end

  def apply_age_range_update(event)
    @attributes['age_range'] = event.data['age_range']
  end

  def apply_payable_datetimes_update(event)
    @attributes['payable_datetimes'] ||= []

    case event.data['action']
    when 'add'
      @attributes['payable_datetimes'] |= Array(event.data['datetimes'])
    when 'remove'
      @attributes['payable_datetimes'] -= Array(event.data['datetimes'])
    when 'set'
      @attributes['payable_datetimes'] = event.data['datetimes']
    end
  end

  def apply_bulk_import_update(event)
    @attributes['bulk_fit_tests_import_id'] = event.data['bulk_fit_tests_import_id']
  end

  def apply_available_update(event)
    @attributes['available'] = event.data['available']
  end
end
