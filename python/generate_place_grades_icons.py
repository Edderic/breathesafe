import os
from pathlib import Path

colorPaletteFall = [
  {
    'name': 'darkRed',
    'r': 174,
    'g': 17,
    'b': 0,
    'letterGrade': 'F'
  },
  {
    'name': 'red',
    'r': 219,
    'g': 21,
    'b': 0,
    'letterGrade': 'E'
  },
  {
    'name': 'orange',
    'r': 245,
    'g': 150,
    'b': 2,
    'letterGrade': 'D'
  },
  {
    'name': 'yellow',
    'r': 255,
    'g': 233,
    'b': 56,
    'letterGrade': 'C'
  },
  {
    'name': 'green',
    'r': 87,
    'g': 195,
    'b': 40,
    'letterGrade': 'B'
  },
  {
    'name': 'dark green',
    'r': 11,
    'g': 161,
    'b': 3,
    'letterGrade': 'A'
  },
  {
    'name': 'grey',
    'r': 200,
    'g': 200,
    'b': 200,
    'letterGrade': 'NA'
  }
]

placeTypeToIconMapping = {
  'accounting': '🧾',
  'airport': '✈️',
  'amusement_park': '🎢',
  'aquarium': '🐠',
  'art_gallery': '🖼',
  'atm': '🏧',
  'bakery': '🥖',
  'bank': '🏦',
  'bar': '🍷',
  'beauty_salon': '💇',
  'bicycle_store': '🚴',
  'book_store': '📚',
  'bowling_alley': '🎳',
  'bus_station': '🚌',
  'cafe': '☕️',
  'campground': '🏕',
  'car_dealer': '🚘',
  'car_rental': '🚙',
  'car_repair': '🚗',
  'car_wash': '🚗',
  'casino': '🎰',
  'cemetery': '🪦',
  'church': '⛪️',
  'city_hall': '🏢',
  'clothing_store': '👗',
  'convenience_store': '🏪',
  'courthouse': '⚖️ ',
  'dentist': '🦷',
  'department_store': '🏬',
  'doctor': '🩺',
  'drugstore': '💊',
  'electrician': '⚡️',
  'electronics_store': '🎚 ',
  'embassy': '🛂',
  'fire_station': '🚒',
  'florist': '🌺 ',
  'funeral_home': '⚰️ ',
  'furniture_store': '🛋',
  'gas_station': '⛽️',
  'gym': '🏋',
  'hair_care': '💇🏼 ',
  'hardware_store': '🪜',
  'health': '⚕️',
  'hindu_temple': '🛕',
  'home_goods_store': '🛠',
  'hospital': '🏥 ',
  'insurance_agency': '👩',
  'jewelry_store': '💍',
  'laundry': '🧺',
  'lawyer': '⚖️ ',
  'library': '📚',
  'light_rail_station': '🚈',
  'liquor_store': '🥃',
  'local_government_office': '🏬',
  'locksmith': '🔐 ',
  'lodging': '🏨',
  'meal_delivery': '🍕',
  'meal_takeaway': '🍕',
  'mosque': '🕌',
  'movie_rental': '🎞',
  'movie_theater': '🍿',
  'moving_company': '🚚',
  'museum': '👀',
  'night_club': '💃',
  'painter': '🎨',
  'parking': '🅿️',
  'pet_store': '🐶',
  'pharmacy': '💊 ',
  'physiotherapist': '⚕️',
  'plumber': '🪠 ',
  'police': '👮',
  'post_office': '🏤',
  'point_of_interest': '🌟',
  'premise': '🏠',
  'primary_school': '🎓',
  'real_estate_agency': '🏠',
  'restaurant': '🍴',
  'roofing_contractor': '🛖',
  'rv_park': '🚐 ',
  'school': '🎓',
  'secondary_school': '🎓',
  'shoe_store': '👠',
  'shopping_mall': '🏬',
  'spa': '🧖',
  'stadium': '🏟',
  'storage': '📦 ',
  'store': '🏬',
  'subway_station': '🚉',
  'supermarket': '🏬',
  'synagogue': '🕍',
  'taxi_stand': '🚕',
  'tourist_attraction': '🌟',
  'train_station': '🚉',
  'transit_station': '🚉',
  'travel_agency': '🛅',
  'university': '🎓',
  'veterinary_care': '🐕',
  'zoo': '🦁',
}

def generate_svg(color, iconString):
    return f'''
    <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" width="30px" height="30px">
      <circle cx="40" cy="40" r="40" fill="{color}"/>
      <text x="50%" y="30%" text-anchor="middle" fill="#EEE" dy=".4em" style="text-shadow: 1px 1px 2px black;">
        <tspan x="48%" dy="0.65em" style="&#10; font-size: xxx-large;&#10;" >
            {iconString}
        </tspan>
      </text>
    </svg>
    '''

if __name__ == '__main__':
    for place, iconString in placeTypeToIconMapping.items():
        for color in colorPaletteFall:
            rgb = f'rgb({color["r"]}, {color["g"]}, {color["b"]})'

            path = Path(os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))) / "app" / "assets" / "images" /"generated" / f"{place}--{color['letterGrade']}.svg"
            with open(path, 'w', encoding='utf-8') as f:
                f.write(generate_svg(rgb, iconString))


