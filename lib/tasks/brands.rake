# frozen_string_literal: true

namespace :brands do
  desc 'Prepopulate brands table with brand names'
  task prepopulate: :environment do
    # Cleaned list: removed duplicates (TRI-TITANS, Trident) and fixed missing comma after 4CAir
    BRAND_NAMES = [
      '3M',
      '4CAir',
      'AER',
      'AKGK',
      'ANYGUARD',
      'AOTDAOU',
      'ARUN',
      'AYYBF',
      'Aegle',
      'Ahotop',
      'Airboss',
      'All Keeper',
      'Ananbros',
      'Aoxing',
      'Armbrust',
      'BAOMAO',
      'BIO-th',
      'BLSCODE',
      'BNX',
      'BOTN',
      'BUGGYBOP',
      'Posh',
      'Birdy Friends',
      'BluNa',
      'Blue',
      'Boncare',
      'BreatheTeq',
      'Breatheze',
      'CNSTRONG',
      'COVAFLU',
      'Canada Masq',
      'Champak',
      'Chengde',
      'Clean & Science',
      'Cleantop',
      'Coast',
      'CocoMong',
      "Daddy's Choice Purism",
      'Demetech',
      'Dentec',
      'Dobu',
      'Dolce',
      'Dr. Puri',
      'Dr. Smile',
      'Drager',
      'EHH',
      'ETIQA',
      'Elastomask',
      'Envo',
      'Evolve Together',
      'Flexmon',
      'Flo',
      'GRZ',
      'GVS',
      'Gerson',
      'Gill',
      'Good Comfort',
      'Good Manner',
      'GoodDay Happy Life',
      'H.A.C',
      'HALIDODO',
      'HANMAUM',
      'HAPPYDAY',
      'HDX',
      'HOM',
      'HUMETA',
      'Homeland Hardware',
      'Honeywell',
      'HotoDeal',
      'Hygenix',
      'Indiana',
      'Innonix',
      'JCJZ',
      'Jingwei',
      'KAMZSZMF',
      'KN Flax',
      'MASKOVER',
      'TS Guard',
      "Kim Well's",
      'Kingfa',
      'LG',
      'LUCIFER',
      'Laianzhi',
      'Lutema',
      'MISSAA',
      'MSA',
      'Makrite',
      'Maxima',
      'MediMask',
      'MedicPro',
      'Miuphro',
      'Moldex',
      'NEWMARK',
      'NYBEE',
      'Novita',
      'O&M Halyard',
      'O2',
      'OPECTICID',
      'BYD Care',
      'Omnimask',
      'Outdoor Research',
      'PalmJoy 3D Protective KN95 Mask',
      'Posh',
      'Powecom',
      'Prestige Ameritech',
      'Primacare',
      'ProductLabs',
      'Trident',
      'Readimask',
      'RightCare',
      'Rose',
      'Ryeziiio',
      'SEJIN-AIRSOOM',
      'SUMFREE',
      'Savewo',
      'Shawmut',
      'Scott',
      'Sheal',
      'Suncoo',
      'TRI-TITANS',
      'TRY Mask',
      'The Bio',
      'Tia / BOTN',
      'Trend',
      'WellBefore',
      'United States Mask Company',
      'Vitacore',
      'Vogmask',
      'WWDOLL',
      'Weldots Fender',
      'Welkeeps',
      'WesGen',
      'Yongjie',
      'Yuikio',
      'ACI',
      'Zerobay',
      'Zimi',
      'Zovator (Harley)',
      'blox',
      'stealth'
    ].freeze

    puts "Prepopulating brands table with #{BRAND_NAMES.length} brand names..."

    created_count = 0
    skipped_count = 0
    error_count = 0
    errors = []

    BRAND_NAMES.each do |brand_name|
      begin
        brand = Brand.find_or_create_by(name: brand_name)
        if brand.persisted? && brand.previous_changes.key?('id')
          created_count += 1
          puts "Created: #{brand_name}"
        else
          skipped_count += 1
          puts "Skipped (already exists): #{brand_name}"
        end
      rescue StandardError => e
        error_count += 1
        error_message = "Error processing '#{brand_name}': #{e.message}"
        errors << error_message
        puts "ERROR: #{error_message}"
      end
    end

    puts "\nSummary:"
    puts "  Created: #{created_count}"
    puts "  Skipped: #{skipped_count}"
    puts "  Errors: #{error_count}"
    puts "  Total brands in database: #{Brand.count}"

    if errors.any?
      puts "\nErrors encountered:"
      errors.each { |error| puts "  - #{error}" }
      exit 1
    end
  end
end
