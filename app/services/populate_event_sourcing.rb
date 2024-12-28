class PopulateEventSourcing
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
    study_uuid: nil,
    sender_uuid: nil,
    kits: nil
  )

    if factory.nil?
      factory = RGeo::Geographic.simple_mercator_factory()
    end

    if from_address_uuid.nil?
      from_address_uuid = AddressQuery.find_address_of(user_email: nil)[0]
    end

    if study_uuid.nil?
      study_uuid = StudyQuery.default_study[0]['uuid']
    end

    all_data.each do |email, v|
      receiver_uuid = email

      data = all_data[email]
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

      if kits.nil?
        kits = []
      end

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

          kits << {
              shippable_uuid: mask_kit_uuid,
              shippable_type: 'MaskKit'
          }
      end


      if data['facial_measurement_kit_created_at']
        facial_measurement_kit_uuid = SecureRandom.uuid
        FacialMeasurementKitActor.preset_create(
          uuid: facial_measurement_kit_uuid,
          digital_caliper_model: data['digital_caliper_model'],
          datetime: data['facial_measurement_kit_created_at'].to_datetime
        )

        kits << {
          shippable_uuid: facial_measurement_kit_uuid,
          shippable_type: 'FacialMeasurementKit'
        }
      end


      if data['qualitative_fit_testing_kit_created_at']
        qlft_uuid = SecureRandom.uuid
        QualitativeFitTestingKitActor.preset_diy_create(
          uuid: qlft_uuid,
          datetime: data['qualitative_fit_testing_kit_created_at'].to_datetime
        )

        kits << {
          shippable_uuid: qlft_uuid,
          shippable_type: 'QualitativeFitTestingKit'
        }
      end

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
          send_mail: false
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
end
