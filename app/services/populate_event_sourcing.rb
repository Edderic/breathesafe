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

# TODO: find_or_create
UserActor.set_name(
  uuid: sender_uuid,
  first_name: 'Edderic',
  last_name: 'Ugaddan'
)

from_address_uuid = AddressActor.find_or_create(
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
        },
        'money' => {
          'request_amount' => 0
        }
      }
    },
    'package_created_at' => '2024-12-20',
    'accepted_datetime' => "2024-11-27",
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
  },
  'ghhughes@gmail.com' => {
    'first_name' => 'Gerard',
    'last_name' => 'Hughes',
    'address' => {
      address_line_1: '2203a San Antonio Ave',
      address_line_2: '',
      address_line_3: '',
      town_city: 'Alameda',
      state: 'CA',
      country: 'US',
      zip_code: '94501',
    },
    'user_created_at' => "2024-11-01",
    'mask_kit_created_at' => "2024-11-13",
    'facial_measurement_kit_created_at' => nil,
    'qualitative_fit_testing_kit_created_at' => nil,
    'request_for_equipment' => {
      'equipment_request' => {
        'money' => {
          'request_amount' => 0
        },
        'masks' => {
          'requested_at' => "2024-11-20",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => nil,
        },
        'facial_measurement_kit' => {
          'requested_at' => nil,
        }
      }
    },
    'package_created_at' => '2024-11-13',
    'accepted_datetime' => "2024-11-02",
    'purchase_label' => {
      'tracking_id' => 'UNKNOWN-BACKFILL',
      'datetime' => '2024-11-13'.to_datetime + 1.second,
    },
    'send_to_courier' => {
      'datetime' => '2024-11-13'.to_datetime + 2.seconds,
    },
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => ''
      },
      'number_of_people_to_potentially_test' => 1
    },
    'digital_caliper_model' => nil
  },

  'quackduck314@gmail.com' => {
    'first_name' => 'Amanda',
    'last_name' => 'Abbott',
    'address' => {
      address_line_1: '11132 SE Grant Ct',
      address_line_2: '',
      address_line_3: '',
      town_city: 'Portland',
      state: 'OR',
      country: 'US',
      zip_code: '97216',
    },
    'user_created_at' => "2024-11-01",
    'mask_kit_created_at' => "2024-11-13",
    'facial_measurement_kit_created_at' => "2024-11-13",
    'qualitative_fit_testing_kit_created_at' => nil,
    'request_for_equipment' => {
      'study_name' => 'Mask Recommender Based on Facial Features',
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-05",
          'received_at' => "2024-11-19",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => nil,
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-05",
          'received_at' => "2024-11-19",
        },
        'money' => {
          'request_amount' => 200
        }
      }
    },
    'package_created_at' => '2024-11-13',
    'accepted_datetime' => "2024-11-02",
    'purchase_label' => {
      'tracking_id' => 'UNKNOWN-BACKFILL',
      'datetime' => '2024-11-13'.to_datetime + 1.second,
    },
    'send_to_courier' => {
      'datetime' => '2024-11-13'.to_datetime + 2.seconds,
    },
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => ''
      },
      'number_of_people_to_potentially_test' => 1
    },
    'digital_caliper_model' => nil
  },
  'robert.pearson.215@gmail.com' => {
    'first_name' => 'Robert',
    'last_name' => 'Pearson',
    'address' => {
      address_line_1: '11132 SE Grant Ct',
      address_line_2: '',
      address_line_3: '',
      town_city: 'Portland',
      state: 'OR',
      country: 'US',
      zip_code: '97216',
    },
    'user_created_at' => "2024-11-01",
    'accepted_datetime' => "2024-11-02",
    'mask_kit_created_at' => "2024-11-13",
    'facial_measurement_kit_created_at' => "2024-11-13",
    'qualitative_fit_testing_kit_created_at' => nil,
    'request_for_equipment' => {
      'study_name' => 'Mask Recommender Based on Facial Features',
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-05",
          'received_at' => "2024-11-19",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => nil,
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-05",
          'received_at' => "2024-11-19",
        },
        'money' => {
          'request_amount' => 200
        }
      }
    },
    'package_created_at' => '2024-11-13',
    'purchase_label' => {
      'tracking_id' => 'UNKNOWN-BACKFILL',
      'datetime' => '2024-11-13'.to_datetime + 1.second,
    },
    'send_to_courier' => {
      'datetime' => '2024-11-13'.to_datetime + 2.seconds,
    },
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => ''
      },
      'number_of_people_to_potentially_test' => 2
    },
    'digital_caliper_model' => nil
  },
  'disastertrash3@gmail.com' => {
    'first_name' => 'Gabriel',
    'last_name' => 'B',
    'address' => {
      address_line_1: '400 NE 100th Ave',
      address_line_2: 'Apt 405',
      address_line_3: '',
      town_city: 'Portland',
      state: 'OR',
      country: 'US',
      zip_code: '97220',
    },
    'user_created_at' => "2024-11-07",
    'accepted_datetime' => "2024-11-08",
    'mask_kit_created_at' => "2024-11-18",
    'facial_measurement_kit_created_at' => "2024-11-18",
    'qualitative_fit_testing_kit_created_at' => "2024-11-18",
    'request_for_equipment' => {
      'study_name' => 'Mask Recommender Based on Facial Features',
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-10",
          'received_at' => "2024-11-25",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => "2024-11-10",
          'received_at' => "2024-11-25",
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-10",
          'received_at' => "2024-11-25",
        },
        'money' => {
          'request_amount' => 100
        }
      }
    },
    'package_created_at' => '2024-11-18',
    'purchase_label' => {
      'tracking_id' => 'UNKNOWN-BACKFILL',
      'datetime' => '2024-11-19'.to_datetime + 1.second,
    },
    'send_to_courier' => {
      'datetime' => '2024-11-19'.to_datetime + 2.seconds,
    },
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => ''
      },
      'number_of_people_to_potentially_test' => 1
    },
    'digital_caliper_model' => '6-inch iGaging'
  },
  'piggybuttercup@gmail.com' => {
    'first_name' => 'Bug',
    'last_name' => 'Jaeger',
    'address' => {
      address_line_1: '',
      address_line_2: '',
      address_line_3: '',
      town_city: 'Portland',
      state: 'OR',
      country: 'US',
      zip_code: '',
    },
    'user_created_at' => "2024-11-05",
    'accepted_datetime' => "2024-11-06",
    'mask_kit_created_at' => "2024-11-13",
    'facial_measurement_kit_created_at' => "2024-11-13",
    'qualitative_fit_testing_kit_created_at' => "2024-11-13",
    'request_for_equipment' => {
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-10",
          'received_at' => "2024-11-19",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => "2024-11-10",
          'received_at' => "2024-11-19",
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-10",
          'received_at' => "2024-11-19",
        },
        'money' => {
          'request_amount' => 0
        }
      }
    },
    'package_created_at' => '2024-11-18',
    'purchase_label' => {
      'tracking_id' => 'UNKNOWN-BACKFILL',
      'datetime' => '2024-11-19'.to_datetime + 1.second,
    },
    'send_to_courier' => {
      'datetime' => '2024-11-19'.to_datetime + 2.seconds,
    },
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => ''
      },
      'number_of_people_to_potentially_test' => 1
    },
    'digital_caliper_model' => '6-inch iGaging'
  },
  'aditi.devices@gmail.com' => {
    'first_name' => 'Aditi',
    'last_name' => 'Joshi',
    'address' => {
      address_line_1: '150 E 57th Street',
      address_line_2: 'Apt P1A',
      address_line_3: '',
      town_city: 'New York City',
      state: 'NY',
      country: 'US',
      zip_code: '10022',
    },
    'user_created_at' => "2024-11-10",
    'accepted_datetime' => "2024-11-11",
    'mask_kit_created_at' => "2024-11-18",
    'facial_measurement_kit_created_at' => "2024-11-18",
    'qualitative_fit_testing_kit_created_at' => "2024-11-18",
    'request_for_equipment' => {
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-11",
          'received_at' => "2024-11-19",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => "2024-11-11",
          'received_at' => "2024-11-19",
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-11",
          'received_at' => "2024-11-19",
        },
        'money' => {
          'request_amount' => 0
        }
      }
    },
    'package_created_at' => '2024-11-18',
    'purchase_label' => {
      'tracking_id' => 'UNKNOWN-BACKFILL',
      'datetime' => '2024-11-19'.to_datetime + 1.second,
    },
    'send_to_courier' => {
      'datetime' => '2024-11-19'.to_datetime + 2.seconds,
    },
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => ''
      },
      'number_of_people_to_potentially_test' => 1
    },
    'digital_caliper_model' => '6-inch iGaging'
  },
  'matthew.b.clifford@gmail.com' => {
    'first_name' => 'Matt',
    'last_name' => 'C',
    'address' => {
      address_line_1: '124 Manns Ave',
      address_line_2: '',
      address_line_3: '',
      town_city: 'Newark',
      state: 'DE',
      country: 'US',
      zip_code: '19711',
    },
    'user_created_at' => "2024-11-24",
    'accepted_datetime' => "2024-11-25",
    'mask_kit_created_at' => "2024-11-25",
    'facial_measurement_kit_created_at' => "2024-11-25",
    'qualitative_fit_testing_kit_created_at' => "2024-11-25",
    'request_for_equipment' => {
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-25",
          'received_at' => "2024-12-03",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => "2024-11-25",
          'received_at' => "2024-12-03",
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-25",
          'received_at' => "2024-12-03",
        },
        'money' => {
          'request_amount' => 200
        }
      }
    },
    'package_created_at' => '2024-11-29',
    'purchase_label' => {
      'tracking_id' => 'UNKNOWN-BACKFILL',
      'datetime' => '2024-11-29'.to_datetime + 1.second,
    },
    'send_to_courier' => {
      'datetime' => '2024-11-29'.to_datetime + 2.seconds,
    },
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => ''
      },
      'number_of_people_to_potentially_test' => 2
    },
    'digital_caliper_model' => '8-inch iGaging'
  },
  '4johnfitz' => {
    'first_name' => 'John',
    'last_name' => 'Fitzgerald',
    'address' => {
      address_line_1: '17440 82nd Ave North',
      address_line_2: '',
      address_line_3: '',
      town_city: 'Maple Grove',
      state: 'MN',
      country: 'US',
      zip_code: '55311',
    },
    'user_created_at' => "2024-11-24",
    'accepted_datetime' => "2024-11-25",
    'removal_from_study'=> {
      'reason' => 'Can no longer fulfill the time commitment.',
      'removal_datetime' => '2024-12-07',
    },
    'mask_kit_created_at' => "2024-11-25",
    'facial_measurement_kit_created_at' => "2024-11-25",
    'qualitative_fit_testing_kit_created_at' => "2024-11-25",
    'request_for_equipment' => {
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-26",
          'received_at' => "2024-12-07",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => "2024-11-26",
          'received_at' => "2024-12-07",
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-26",
          'received_at' => "2024-12-07",
        },
        'money' => {
          'request_amount' => 0
        }
      }
    },
    'package_created_at' => '2024-11-26',
    'purchase_label' => {
      'tracking_id' => 'UNKNOWN-BACKFILL',
      'datetime' => '2024-11-29'.to_datetime + 1.second,
    },
    'send_to_courier' => {
      'datetime' => '2024-11-29'.to_datetime + 2.seconds,
    },
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => ''
      },
      'number_of_people_to_potentially_test' => 2
    },
    'digital_caliper_model' => '8-inch iGaging'
  },
  'kate.history.nerd@gmail.com' => {
    'first_name' => 'Kate',
    'last_name' => 'Alexander',
    'address' => {
      address_line_1: '55 Elm St.',
      address_line_2: 'Apt. 451',
      address_line_3: '',
      town_city: 'Hartford',
      state: 'CT',
      country: 'US',
      zip_code: '06106',
    },
    'user_created_at' => "2024-11-26",
    'accepted_datetime' => "2024-12-22",
    'mask_kit_created_at' => "2024-12-22",
    'facial_measurement_kit_created_at' => "2024-11-22",
    'qualitative_fit_testing_kit_created_at' => "2024-11-22",
    'request_for_equipment' => {
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-27",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => "2024-11-27",
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-27",
        },
        'money' => {
          'request_amount' => 0
        }
      }
    },
    'package_created_at' => '2024-12-23',
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => ''
      },
      'number_of_people_to_potentially_test' => 1
    },
    'digital_caliper_model' => '8-inch iGaging'
  },
  'brean.farquharson@thermofisher.com' => {
    'first_name' => 'Brean',
    'last_name' => 'Farquharson',
    'address' => {
      address_line_1: '69 Bryant rd',
      address_line_2: '',
      address_line_3: '',
      town_city: 'Jaffrey',
      state: 'NH',
      country: 'US',
      zip_code: '03452',
    },
    'user_created_at' => "2024-11-26",
    'accepted_datetime' => "2024-12-22",
    'mask_kit_created_at' => "2024-12-22",
    'facial_measurement_kit_created_at' => "2024-11-22",
    'qualitative_fit_testing_kit_created_at' => "2024-11-22",
    'request_for_equipment' => {
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-27",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => "2024-11-27",
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-27",
        },
        'money' => {
          'request_amount' => 0
        }
      }
    },
    'package_created_at' => '2024-12-23',
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => ''
      },
      'number_of_people_to_potentially_test' => 1
    },
    'digital_caliper_model' => '8-inch iGaging'
  },
  'aleta.kolan@gmail.com' => {
    'first_name' => 'Aleta',
    'last_name' => 'Wild',
    'address' => {
      address_line_1: '709 Sibley Drive',
      address_line_2: '',
      address_line_3: '',
      town_city: 'Northfield',
      state: 'MN',
      country: 'US',
      zip_code: '55057',
    },
    'user_created_at' => "2024-11-26",
    'accepted_datetime' => "2024-12-22",
    'mask_kit_created_at' => "2024-12-22",
    'facial_measurement_kit_created_at' => "2024-11-22",
    'qualitative_fit_testing_kit_created_at' => "2024-11-22",
    'request_for_equipment' => {
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-27",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => "2024-11-27",
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-27",
        },
        'money' => {
          'request_amount' => 0
        }
      }
    },
    'package_created_at' => '2024-12-23',
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => 'children ages 4 and 5 are having a hard time finding masks that fit'
      },
      'number_of_people_to_potentially_test' => 2
    },
    'digital_caliper_model' => '8-inch iGaging'
  },
  'lesliejacobs222@gmail.com' => {
    'first_name' => 'Leslie',
    'last_name' => 'Jacobs',
    'address' => {
      address_line_1: '7836 Ward Pkwy',
      address_line_2: '',
      address_line_3: '',
      town_city: 'Kansas City',
      state: 'MO',
      country: 'US',
      zip_code: '64114',
    },
    'user_created_at' => "2024-11-26",
    'accepted_datetime' => "2024-12-22",
    'mask_kit_created_at' => "2024-12-22",
    'facial_measurement_kit_created_at' => "2024-11-22",
    'qualitative_fit_testing_kit_created_at' => "2024-11-22",
    'request_for_equipment' => {
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-27",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => "2024-11-27",
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-27",
        },
        'money' => {
          'request_amount' => 0
        }
      }
    },
    'package_created_at' => '2024-12-23',
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => 'narrow face, beaky nose. Husband is Chinese American'
      },
      'number_of_people_to_potentially_test' => 4
    },
    'digital_caliper_model' => '8-inch iGaging'
  },
  'jennifer.platt@gmail.com' => {
    'first_name' => 'Jennifer',
    'last_name' => 'Platt',
    'address' => {
      address_line_1: '65 Harriet Watson Rd',
      address_line_2: '',
      address_line_3: '',
      town_city: 'Pittsboro',
      state: 'NC',
      country: 'US',
      zip_code: '27312',
    },
    'user_created_at' => "2024-11-26",
    'accepted_datetime' => "2024-12-22",
    'mask_kit_created_at' => "2024-12-22",
    'facial_measurement_kit_created_at' => "2024-11-22",
    'qualitative_fit_testing_kit_created_at' => "2024-11-22",
    'request_for_equipment' => {
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-27",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => "2024-11-27",
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-27",
        },
        'money' => {
          'request_amount' => 0
        }
      }
    },
    'package_created_at' => '2024-12-23',
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => 'Hello! My son (15yo) and I would be totally down with this! He’s got a big face - hard to find masks that he likes. Thanks for doing this work!'
      },
      'number_of_people_to_potentially_test' => 2
    },
    'digital_caliper_model' => '8-inch iGaging'
  },
  'aemacwade@gmail.com' => {
    'first_name' => 'Alexandra',
    'last_name' => 'MacWade',
    'address' => {
      address_line_1: '792 President Street',
      address_line_2: 'Apt. 2L',
      address_line_3: '',
      town_city: 'Brooklyn',
      state: 'NY',
      country: 'US',
      zip_code: '11215',
    },
    'user_created_at' => "2024-11-26",
    'accepted_datetime' => "2024-12-22",
    'mask_kit_created_at' => "2024-12-22",
    'facial_measurement_kit_created_at' => "2024-11-22",
    'qualitative_fit_testing_kit_created_at' => "2024-11-22",
    'request_for_equipment' => {
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-27",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => "2024-11-27",
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-27",
        },
        'money' => {
          'request_amount' => 0
        }
      }
    },
    'package_created_at' => '2024-12-23',
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => ''
      },
      'number_of_people_to_potentially_test' => 2
    },
    'digital_caliper_model' => '8-inch iGaging'
  },
  'hleighsullivan@gmail.com' => {
    'first_name' => 'Hannah',
    'last_name' => 'Nowland',
    'address' => {
      address_line_1: '2611 Madison Street',
      address_line_2: '',
      address_line_3: '',
      town_city: 'Tyler',
      state: 'TX',
      country: 'US',
      zip_code: '75701',
    },
    'user_created_at' => "2024-11-26",
    'accepted_datetime' => "2024-12-22",
    'mask_kit_created_at' => "2024-12-22",
    'facial_measurement_kit_created_at' => "2024-11-22",
    'qualitative_fit_testing_kit_created_at' => "2024-11-22",
    'request_for_equipment' => {
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-27",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => "2024-11-27",
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-27",
        },
        'money' => {
          'request_amount' => 0
        }
      }
    },
    'package_created_at' => '2024-12-23',
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => 'Hi there! My fellow covid cautious friend mentioned that there is a study looking for volunteers for fit testing and facial measurements. My family is definitely interested in helping!  We are a family of 3, with a child age 4 (with a very large head), and have not had the tools to be able to fit test any masks, despite needing to and wearing them everyday and everywhere.  If volunteers are still needed, please let me know what you need from us going forward! Thank you so much!  Hannah Nowland'
      },
      'number_of_people_to_potentially_test' => 3
    },
    'digital_caliper_model' => '8-inch iGaging'
  },
  'vmichellelee@gmail.com' => {
    'first_name' => 'Veronica',
    'last_name' => 'Lee',
    'address' => {
      address_line_1: '824 1/2 E Cottage Grove Avenue',
      address_line_2: 'Apt. 2',
      address_line_3: '',
      town_city: 'Bloomington',
      state: 'IN',
      country: 'US',
      zip_code: '47408',
    },
    'user_created_at' => "2024-11-26",
    'accepted_datetime' => "2024-12-22",
    'mask_kit_created_at' => "2024-12-22",
    'facial_measurement_kit_created_at' => "2024-11-22",
    'qualitative_fit_testing_kit_created_at' => "2024-11-22",
    'request_for_equipment' => {
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-27",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => "2024-11-27",
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-27",
        },
        'money' => {
          'request_amount' => 0
        }
      }
    },
    'package_created_at' => '2024-12-23',
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => 'Hi Mr. Edderic Ugaddan, I saw your post on Twitter looking for volunteers for the development of a mask recommender and my family of three would like to volunteer. For reference we a mixed race family of three with a kindergartner. We’ve dedicated the past five years on making sure we breathe clean air but have had a hard time finding masks that fit well. Could we please be a part of your research?  Thank you for your time and consideration!  Sincerely, Veronica Lee'
      },
      'number_of_people_to_potentially_test' => 3
    },
    'digital_caliper_model' => '8-inch iGaging'
  },
  'Lkrueger13@hotmail.com' => {
    'first_name' => 'Lisa',
    'last_name' => 'Krueger',
    'address' => {
      address_line_1: '1060 CR 257',
      address_line_2: '#204',
      address_line_3: '',
      town_city: 'Liberty Hill',
      state: 'TX',
      country: 'US',
      zip_code: '78642',
    },
    'user_created_at' => "2024-11-26",
    'accepted_datetime' => "2024-12-22",
    'mask_kit_created_at' => "2024-12-22",
    'facial_measurement_kit_created_at' => "2024-11-22",
    'qualitative_fit_testing_kit_created_at' => "2024-11-22",
    'request_for_equipment' => {
      'equipment_request' => {
        'masks' => {
          'requested_at' => "2024-11-27",
        },
        'qualitative_fit_testing_kit' => {
          'requested_at' => "2024-11-27",
        },
        'facial_measurement_kit' => {
          'requested_at' => "2024-11-27",
        },
        'money' => {
          'request_amount' => 0
        }
      }
    },
    'package_created_at' => '2024-12-23',
    'study_qualifications' => {
      'country_of_residence' => 'US',
      'hard_to_fit_face' => {
        'notes' => 'Hi, I would be interested in participating in the mask fit study. My family consists of myself, my husband, 10 year old daughter and 6 year old son. My son is petite and I have had a very difficult time finding a good fit for him.  Thank you, Lisa Krueger'
      },
      'number_of_people_to_potentially_test' => 3
    },
    'digital_caliper_model' => '8-inch iGaging'
  },
}

def backfill(all_data, factory, from_address_uuid, study_uuid, sender_uuid)
  all_data.each do |email, v|
    receiver_uuid = email
    study_name = 'Mask Recommender Based on Facial Features'

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

    mask_kit_uuid = SecureRandom.uuid
    MaskKitActor.create(
      uuid: mask_kit_uuid,
      datetime: data['mask_kit_created_at'].to_datetime
    )

    MaskKitActor.add_default_masks(
      uuid: mask_kit_uuid,
      datetime: data['mask_kit_created_at'].to_datetime + 1.second
    )

    kits = [
      {
        shippable_uuid: mask_kit_uuid,
        shippable_type: 'MaskKit'
      }
    ]

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
        uuid: shipping_uuid,
        purchase_label: data['purchase_label'],
        datetime: data['package_created_at'].to_datetime + 1.day
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

backfill(all_data, factory, from_address_uuid, study_uuid, sender_uuid)
