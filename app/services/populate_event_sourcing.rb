from_address = {
  address_line_1: '138 Miller Ave.',
  address_line_2: '',
  address_line_3: '',
  town_city: 'Rumford',
  state: 'RI',
  country: 'US',
  zip_code: '02916',
}

factory = RGeo::Geographic.simple_mercator_factory()

sender_uuid = 'edderic@gmail.com'
UserActor.create(
  uuid: sender_uuid,
  datetime: 2.months.ago
)

from_address_uuid = AddressActor.create(
  address: from_address,
  factory: factory
)

study_uuid = SecureRandom.uuid
StudyActor.create( uuid: study_uuid, name: 'Mask Recommender Based on Facial Features')

all_data = {
  'briana@brianamontagne.com' => {
    'first_name' => 'Briana',
    'last_name' => 'Montagne',
    'address' => {
      address_line_1: '6922 Soundview Drive',
      address_line_2: '',
      address_line_3: '',
      town_city: 'Gig Harbor',
      state: 'WA',
      country: 'US',
      zip_code: '98335',
    },
    'user_created_at' => "2024-11-26",
    'mask_kit_created_at' => "2024-12-20",
    'facial_measurement_kit_created_at' => "2024-12-20",
    'qualitative_fit_testing_kit_created_at' => "2024-12-20",
    'request_for_equipment' => {
      'study_name' => 'Mask Recommender Based on Facial Features',
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-27",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => "2024-11-27",
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-27",
        }
      }
    },
    'package_created_at' => '2024-12-20',
    'accepted_into_study_at' => "2024-11-27",
    # 'purchase_label' => {
      # 'tracking_id' => '12ZEF1245ASTHEUSOTHI'
    # },
    # 'send_to_courier' => {
      # 'datetime' => "2024-12-01"
    # },
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => 'high nose bridge, small narrow face'
      },
      'number_of_people_to_potentially_test' => 4
    },
    'digital_caliper_model' => '6-inch iGaging'
  }
}

all_data.each do |email, v|
  receiver_uuid = email
  study_name = 'Mask Recommender Based on Facial Features'

  data = all_data[email]
  to_address_uuid = AddressActor.create(
    address: data['address'],
    factory: factory
  )

  UserActor.create(
    uuid: email,
    datetime: data['user_created_at'].to_datetime
  )

  UserActor.set_address(
    uuid: email,
    address_uuid: to_address_uuid
  )

  UserActor.set_name(
    uuid: email,
    first_name: data['first_name'],
    last_name: data['last_name'],
    datetime: data['user_created_at'].to_datetime + 1.second
  )

  StudyParticipantActor.create(
    participant_uuid: email,
    study_uuid: study_uuid,
    datetime: data['accepted_into_study_at'].to_datetime - 1.second
  )

  StudyParticipantActor.accept_into_study(
    participant_uuid: email,
    study_uuid: study_uuid,
    datetime: data['accepted_into_study_at'].to_datetime
  )

  StudyParticipantActor.set_study_qualifications(
    participant_uuid: email,
    study_uuid: study_uuid,
    study_qualifications: data['study_qualifications'],
    datetime: data['user_created_at'].to_datetime + 1.second
  )

  StudyParticipantActor.request_for_equipment(
    participant_uuid: email,
    study_uuid: study_uuid,
    equipment_request: data['request_for_equipment']['equipment_request'],
    datetime: data['user_created_at'].to_datetime + 1.second
  )

  facial_measurement_kit_uuid = SecureRandom.uuid
  FacialMeasurementKitActor.preset_create(
    uuid: facial_measurement_kit_uuid,
    digital_caliper_model: data['digital_caliper_model'],
    datetime: data['facial_measurement_kit_created_at'].to_datetime
  )

  mask_kit_uuid = SecureRandom.uuid
  MaskKitActor.create(
    uuid: mask_kit_uuid,
    datetime: data['mask_kit_created_at'].to_datetime
  )

  MaskKitActor.add_default_masks(
    uuid: mask_kit_uuid,
    datetime: data['mask_kit_created_at'].to_datetime
  )

  qlft_uuid = SecureRandom.uuid
  QualitativeFitTestingKitActor.preset_diy_create(
    uuid: qlft_uuid,
    datetime: data['qualitative_fit_testing_kit_created_at'].to_datetime
  )

  shipping_uuid = SecureRandom.uuid
  ShippingActor.create_package(
    uuid: shipping_uuid,
    datetime: data['package_created_at']
  )

  [
    {
      shippable_uuid: facial_measurement_kit_uuid,
      shippable_type: 'FacialMeasurementKit'
    },
    {
      shippable_uuid: qlft_uuid,
      shippable_type: 'QualitativeFitTestingKit'
    },
    {
      shippable_uuid: mask_kit_uuid,
      shippable_type: 'MaskKit'
    }
  ].each do |kit|
    ShippingActor.add_item(
      uuid: shipping_uuid,
      shippable_uuid: kit[:shippable_uuid],
      shippable_type: kit[:shippable_type],
      datetime: data['package_created_at'].to_datetime + 1.second
    )
  end

  ShippingActor.set_sender(
    uuid: shipping_uuid,
    sender_uuid: sender_uuid,
    datetime: data['package_created_at'].to_datetime + 1.second
  )

  ShippingActor.set_receiver(
    uuid: shipping_uuid,
    receiver_uuid: receiver_uuid,
    datetime: data['package_created_at'].to_datetime + 1.second
  )

  ShippingActor.set_from_address(
    uuid: shipping_uuid,
    from_address_uuid: from_address_uuid,
  )

  ShippingActor.set_to_address(
    uuid: shipping_uuid,
    to_address_uuid: to_address_uuid,
  )

  # ShippingActor.purchase_label(
    # uuid: shipping_uuid,
    # purchase_label: data['purchase_label']
  # )

end

UserStatusBuilder.build
