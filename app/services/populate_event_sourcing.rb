class PopulateEventSourcing
  def self.create_mask_kit(data)
    mask_kit_uuid = SecureRandom.uuid

    if data['mask_kit_created_at']
      MaskKitActor.create(
        uuid: mask_kit_uuid,
        datetime: data['mask_kit_created_at'].to_datetime
      )

      MaskKitActor.add_default_masks(
        uuid: mask_kit_uuid,
        datetime: data['mask_kit_created_at'].to_datetime + 1.second
      )

      return {
        shippable_uuid: mask_kit_uuid,
        shippable_type: 'MaskKit'
      }
    end
  end

  def self.create_facial_measurement_kit(data)
    facial_measurement_kit_uuid = SecureRandom.uuid

    if data['facial_measurement_kit_created_at']
      FacialMeasurementKitActor.preset_create(
        uuid: facial_measurement_kit_uuid,
        digital_caliper_model: data['digital_caliper_model'],
        datetime: data['facial_measurement_kit_created_at'].to_datetime
      )

      return {
        shippable_uuid: facial_measurement_kit_uuid,
        shippable_type: 'FacialMeasurementKit'
      }
    end
  end

  def self.create_qualitative_fit_testing_kit(data)
    if data['qualitative_fit_testing_kit_created_at']
      qlft_uuid = SecureRandom.uuid

      if data['qualitative_fit_testing_kit_type'] == 'Allegro'
        QualitativeFitTestingKitActor.preset_allegro_create(
          uuid: qlft_uuid,
          datetime: data['qualitative_fit_testing_kit_created_at'].to_datetime
        )
      else
        QualitativeFitTestingKitActor.preset_diy_create(
          uuid: qlft_uuid,
          datetime: data['qualitative_fit_testing_kit_created_at'].to_datetime
        )
      end

      return {
        shippable_uuid: qlft_uuid,
        shippable_type: 'QualitativeFitTestingKit'
      }
    end
  end
  # Parameters:
  #   all_data: dict,
  #     The key is the email, and the value is some dict about that email
  #
  #   factory: RGeo::Geographic. Defaults to RGeo::Geographic.simple_mercator_factory()
  #
  #   from_address_uuid: UUID of the Address where a package was/would be shipped from
  #     Defaults to the address UUID associated with edderic@gmail.com
  #
  #   study_uuid: UUID of the study. Defaults to the uuid of "Mask Recommender
  #     Based on Facial Features"
  #
  #   kits: Array. Defaults to an empty list.
  #
  def self.backfill(
    all_data:,
    factory: nil,
    from_address_uuid: nil,
    sender_uuid: 'edderic@gmail.com',
    study_uuid: nil,
    kits: nil,
    send_mail: false
  )

    if factory.nil?
      factory = RGeo::Geographic.simple_mercator_factory()
    end

    if from_address_uuid.nil?
      from_address_uuid = AddressQuery.find_address_of(user_email: sender_uuid)[0]['uuid']
    end

    if study_uuid.nil?
      study_uuid = StudyQuery.default_study[0]['uuid']
    end

    all_data.each do |email, v|
      receiver_uuid = email

      data = all_data[email].with_indifferent_access
      to_address_uuid = AddressActor.find_or_create(
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
        datetime: data['accepted_datetime'].to_datetime - 1.second
      )

      StudyParticipantActor.accept_into_study(
        participant_uuid: email,
        study_uuid: study_uuid,
        datetime: data['accepted_datetime'].to_datetime
      )

      StudyParticipantActor.set_study_qualifications(
        participant_uuid: email,
        study_uuid: study_uuid,
        study_qualifications: data['study_qualifications'],
        datetime: data['accepted_datetime'].to_datetime + 1.second
      )

      if data['remove_from_study']
        StudyParticipantActor.remove_from_study(
          participant_uuid: email,
          study_uuid: study_uuid,
          datetime: data['remove_from_study'].to_datetime
        )
      end

      StudyParticipantActor.request_for_equipment(
        participant_uuid: email,
        study_uuid: study_uuid,
        equipment_request: data['request_for_equipment']['equipment_request'],
        datetime: data['accepted_datetime'].to_datetime + 1.second
      )

      kits = [
        self.create_mask_kit(data),
        self.create_facial_measurement_kit(data),
        self.create_qualitative_fit_testing_kit(data)
      ].compact

      shipping_uuid = SecureRandom.uuid
      ShippingActor.create_package(
        uuid: shipping_uuid,
        datetime: data['package_created_at']
      )

      kits.each do |kit|
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

      if data['package_received_at']
        ShippingActor.receive(
          uuid: shipping_uuid,
          datetime: data['package_received_at'].to_datetime + 1.second
        )
      end

      ShippingActor.set_from_address(
        uuid: shipping_uuid,
        from_address_uuid: from_address_uuid,
        datetime: data['package_created_at'].to_datetime + 1.day
      )

      ShippingActor.set_to_address(
        uuid: shipping_uuid,
        to_address_uuid: to_address_uuid,
      )

      if data['purchase_label'].present?
        ShippingActor.purchase_label(
          email: email,
          name: data['first_name'],
          uuid: shipping_uuid,
          purchase_label: data['purchase_label'],
          datetime: data['package_created_at'].to_datetime + 1.day,
          send_mail: send_mail
        )
      end

      if data['send_to_courier'].present?
        ShippingActor.send_to_courier(
          uuid: shipping_uuid,
          details: data['send_to_courier'],
          datetime: data['package_created_at'].to_datetime + 1.day
        )
      end
    end
  end

  def self.generate_default_data_hash(args)
    # Parameters
    #   args: hash
    #   {
    #     email: string
    #     first_name: string
    #     last_name: string
    #     address: {
    #       address_line_1: string
    #       address_line_2: string
    #       address_line_3: string
    #       town_city: string
    #       state: string
    #       country: string
    #       zip_code: string
    #     }
    #
    #     study_notes: string. Could be None
    #     number_of_people_to_potentially_test: integer
    #   }
    indiff_access = args.with_indifferent_access
    digital_caliper_model = indiff_access[:digital_caliper_model] || '8-inch iGaging'
    sender_uuid = indiff_access[:sender_uuid] || 'edderic@gmail.com'
    now = DateTime.now

    {
      all_data: {
        indiff_access[:email] => {
          'first_name' => 'Megan',
          'last_name' => 'McNeill',
          'address' => {
            address_line_1: '78 Byron Pl',
            address_line_2: '',
            address_line_3: '',
            town_city: 'New Haven',
            state: 'CT',
            country: 'US',
            zip_code: '06515',
          },
          'user_created_at' => "2025-04-06",
          'mask_kit_created_at' => "2025-04-07",
          'facial_measurement_kit_created_at' => "2025-04-07",
          'qualitative_fit_testing_kit_created_at' => "2025-04-07",
          'request_for_equipment' => {
            'study_name' => 'Mask Recommender Based on Facial Features',
            'equipment_request' => {
              'masks' => {
                'requested_at' => now.to_datetime + 1.second,
              },
              'qualitative_fit_testing_kit' => {
                'requested_at' => now.to_datetime + 1.second,
              },
              'facial_measurement_kit' => {
                'requested_at' => now.to_datetime + 1.second,
              },
              'money' => {
                'request_amount' => 0
              }
            }
          },
          'package_created_at' => now,
          'accepted_datetime' => now,
          'study_qualifications' => {
            'country_of_residence' => 'US',
            'hard_to_fit_face' => {
              'notes' => indiff_access[:study_notes]
            },
            'number_of_people_to_potentially_test' => indiff_access[:number_of_people_to_potentially_test]
          },
          'digital_caliper_model' => digital_caliper_model
        }
      },
      sender_uuid: sender_uuid
    }
  end

  def self.send_more_stuff(args)
    mask_uuids = args.fetch(:mask_uuids)
    to_user_uuid = args.fetch(:to_user_uuid)

    datetime = args[:datetime] || DateTime.now

    shipping_statuses = ShippingStatus.where("to_user_uuid = '#{to_user_uuid}'").order(:created_at)
    last_shipping_status = shipping_statuses.last

    puts(last_shipping_status)

    unless last_shipping_status
      raise ArgumentError.new("Could not find last shipping status for #{to_user_uuid}")
    end

    ActiveRecord::Base.transaction do
      shipping_uuid = SecureRandom.uuid

      ShippingActor.create_package(
        uuid: shipping_uuid,
        datetime: datetime
      )

      ShippingActor.set_receiver(
        uuid: shipping_uuid,
        receiver_uuid: last_shipping_status.to_user_uuid,
        datetime: datetime + 1.second
      )

      ShippingActor.set_sender(
        uuid: shipping_uuid,
        sender_uuid: last_shipping_status.from_user_uuid,
        datetime: datetime + 1.second
      )

      ShippingActor.set_from_address(
        uuid: shipping_uuid,
        from_address_uuid: last_shipping_status.from_address_uuid,
        datetime: datetime + 1.second
      )

      ShippingActor.set_to_address(
        uuid: shipping_uuid,
        to_address_uuid: last_shipping_status.to_address_uuid,
        datetime: datetime + 1.second
      )

      if mask_uuids
        # TODO: add foreign key constraints
        mask_kit_uuid = SecureRandom.uuid

        MaskKitActor.create(
          uuid: mask_kit_uuid,
          datetime: datetime
        )

        mask_uuids.each do |mask_uuid|
          MaskKitActor.add_masks(
            uuid: mask_kit_uuid,
            mask_uuids: mask_uuid,
            datetime: datetime + 1.second
          )
        end

        ShippingActor.add_item(
          uuid: shipping_uuid,
          shippable_uuid: mask_kit_uuid,
          shippable_type: 'MaskKit',
        )
      end
    end
  end
end
