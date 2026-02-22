"""Structured data for the map-exploration page.

Keep additions simple:
- Add/modify entries in VISITED_LOCATIONS or MUG_COLLECTION entries below.
- Each item is rendered into map points for the frontend.
"""

def _point(
    *,
    kind,
    title,
    lat,
    lng,
    subtitle="",
    notes=None,
    gifted_by="",
    mug_type="",
    country="",
    state="",
    city="",
    photos=None,
):
    return {
        "kind": kind,  # "visited" | "mug"
        "title": title,
        "subtitle": subtitle,
        "lat": lat,
        "lng": lng,
        "notes": notes or [],
        "gifted_by": gifted_by,
        "mug_type": mug_type,
        "country": country,
        "state": state,
        "city": city,
        "photos": photos or [],
    }


# Approximate coordinates (good enough for pin placement/UI interaction).
STATE_COORDS = {
    "Alaska": (64.2008, -149.4937),
    "Maine": (45.2538, -69.4455),
    "Louisiana": (30.9843, -91.9623),
    "Indiana": (39.7684, -86.1581),
    "Rhode Island": (41.6809, -71.5118),
    "Massachusetts": (42.3601, -71.0589),
    "Connecticut": (41.7658, -72.6734),
    "West Virginia": (38.3498, -81.6326),
    "Tennessee": (36.1627, -86.7816),
    "Virginia": (37.5407, -77.4360),
    "New Mexico": (35.6870, -105.9378),
    "Delaware": (39.1582, -75.5244),
    "Colorado": (39.7392, -104.9903),
    "Illinois": (39.7984, -89.6544),
    "Ohio": (39.9612, -82.9988),
    "Maryland": (38.9784, -76.4922),
    "Florida": (30.4383, -84.2807),
    "Nevada": (39.1638, -119.7674),
    "South Carolina": (34.0007, -81.0348),
    "Texas": (30.2672, -97.7431),
    "Washington": (47.0379, -122.9007),
    "Minnesota": (44.9537, -93.0900),
    "New York": (42.6526, -73.7562),
    "California": (38.5816, -121.4944),
    "Oregon": (44.9429, -123.0351),
    "North Carolina": (35.7796, -78.6382),
    "New Jersey": (40.2206, -74.7699),
    "Pennsylvania": (40.2732, -76.8867),
}

CITY_COORDS = {
    "Pittsburgh": (40.4406, -79.9959),
    "Chicago": (41.8781, -87.6298),
    "Miami": (25.7617, -80.1918),
    "Mumbai": (19.0760, 72.8777),
    "Washington DC": (38.9072, -77.0369),
    "Seoul": (37.5665, 126.9780),
    "Dublin": (53.3498, -6.2603),
    "Venezia": (45.4408, 12.3155),
    "Barcelona": (41.3874, 2.1686),
    "Dubai": (25.2048, 55.2708),
    "Oslo": (59.9139, 10.7522),
    "Stockholm": (59.3293, 18.0686),
    "Savannah": (32.0809, -81.0912),
    "Athens": (37.9838, 23.7275),
    "Myrtle Beach": (33.6891, -78.8867),
    "Boston": (42.3601, -71.0589),
    "New Orleans": (29.9511, -90.0715),
    "Charlotte": (35.2271, -80.8431),
    "Denver": (39.7392, -104.9903),
    "Scranton": (41.4089, -75.6624),
    "Philadelphia": (39.9526, -75.1652),
    "Baltimore": (39.2904, -76.6122),
    "New York City": (40.7128, -74.0060),
}

PARK_REGION_COORDS = {
    "Acadia National Park": (44.3386, -68.2733),
    "Pennsylvania Grand Canyon": (41.7098, -77.4544),
    "Shenandoah National Park": (38.2928, -78.6796),
    "Lake Tahoe": (39.0968, -120.0324),
    "Upper Peninsula, Michigan": (46.5453, -87.3954),
}

COUNTRY_COORDS = {
    "France": (46.2276, 2.2137),
    "England": (52.3555, -1.1743),
}


VISITED_LOCATIONS = [
    {
        "title": "Texas, USA",
        "lat": 31.0,
        "lng": -99.0,
        "subtitle": "Visited Places",
        "notes": ["TX Trip", "TX Trip", "TX Trip", "Parents' Trip"],
        "state": "Texas",
        "country": "USA",
    },
    {
        "title": "Connecticut, USA",
        "lat": 41.6032,
        "lng": -73.0877,
        "subtitle": "Visited Places",
        "notes": ["CT Drive"],
        "state": "Connecticut",
        "country": "USA",
    },
    {
        "title": "New York, USA",
        "lat": 42.9,
        "lng": -75.5,
        "subtitle": "Visited Places",
        "notes": ["Zaid comes over - NY, PA, Boston trips", "Parents' Trip", "CG NY Trip"],
        "state": "New York",
        "country": "USA",
    },
    {
        "title": "Pennsylvania, USA",
        "lat": 41.0,
        "lng": -77.5,
        "subtitle": "Visited Places",
        "notes": [
            "Zaid comes over - NY, PA, Boston trips",
            "PA Grand Canyon trip with Tapas and Kirti",
            "Trips - Scranton",
            "Parents' Trip",
            "Car trips - Philly",
        ],
        "state": "Pennsylvania",
        "country": "USA",
    },
    {
        "title": "Boston, Massachusetts, USA",
        "lat": CITY_COORDS["Boston"][0],
        "lng": CITY_COORDS["Boston"][1],
        "subtitle": "Visited Places",
        "notes": ["Zaid comes over - NY, PA, Boston trips"],
        "state": "Massachusetts",
        "city": "Boston",
        "country": "USA",
    },
    {
        "title": "Indiana, USA",
        "lat": 39.7684,
        "lng": -86.1581,
        "subtitle": "Visited Places",
        "notes": ["Saad's Wedding - IN Trip with Octavium"],
        "state": "Indiana",
        "country": "USA",
    },
    {
        "title": "New Orleans, Louisiana, USA",
        "lat": CITY_COORDS["New Orleans"][0],
        "lng": CITY_COORDS["New Orleans"][1],
        "subtitle": "Visited Places",
        "notes": ["New Orleans trip"],
        "state": "Louisiana",
        "city": "New Orleans",
        "country": "USA",
    },
    {
        "title": "Acadia National Park, Maine, USA",
        "lat": 44.3386,
        "lng": -68.2733,
        "notes": ["Acadia Trip"],
        "state": "Maine",
        "country": "USA",
        "photos": [
            {
                "path": "images/travel/pins/acadia-profile.JPG",
                "alt": "Sunrise view at Acadia"
            }
        ],
    },
    {
        "title": "Pennsylvania Grand Canyon (Pine Creek Gorge), USA",
        "lat": PARK_REGION_COORDS["Pennsylvania Grand Canyon"][0],
        "lng": PARK_REGION_COORDS["Pennsylvania Grand Canyon"][1],
        "subtitle": "Visited Places",
        "notes": ["PA Grand Canyon trip with Tapas and Kirti"],
        "state": "Pennsylvania",
        "country": "USA",
    },
    {
        "title": "Charlotte, North Carolina, USA",
        "lat": CITY_COORDS["Charlotte"][0],
        "lng": CITY_COORDS["Charlotte"][1],
        "subtitle": "Visited Places",
        "notes": ["Charlotte trip to visit Areej"],
        "state": "North Carolina",
        "city": "Charlotte",
        "country": "USA",
    },
    {
        "title": "California, USA",
        "lat": 36.7783,
        "lng": -119.4179,
        "subtitle": "Visited Places",
        "notes": ["CA Trip - cousins / Tahoe / United layover + bag experience", "Parents' Trip"],
        "state": "California",
        "country": "USA",
    },
    {
        "title": "Lake Tahoe, USA",
        "lat": PARK_REGION_COORDS["Lake Tahoe"][0],
        "lng": PARK_REGION_COORDS["Lake Tahoe"][1],
        "subtitle": "Visited Places",
        "notes": ["CA Trip - Tahoe"],
        "state": "California",
        "country": "USA",
    },
    {
        "title": "Denver, Colorado, USA",
        "lat": CITY_COORDS["Denver"][0],
        "lng": CITY_COORDS["Denver"][1],
        "subtitle": "Visited Places",
        "notes": ["Trips - Denver"],
        "state": "Colorado",
        "city": "Denver",
        "country": "USA",
    },
    {
        "title": "Scranton, Pennsylvania, USA",
        "lat": CITY_COORDS["Scranton"][0],
        "lng": CITY_COORDS["Scranton"][1],
        "subtitle": "Visited Places",
        "notes": ["Trips - Scranton"],
        "state": "Pennsylvania",
        "city": "Scranton",
        "country": "USA",
    },
    {
        "title": "Shenandoah National Park, Virginia, USA",
        "lat": PARK_REGION_COORDS["Shenandoah National Park"][0],
        "lng": PARK_REGION_COORDS["Shenandoah National Park"][1],
        "subtitle": "Visited Places",
        "notes": ["Trips - Shenandoah"],
        "state": "Virginia",
        "country": "USA",
    },
    {
        "title": "Delaware, USA",
        "lat": 39.0,
        "lng": -75.5,
        "subtitle": "Visited Places",
        "notes": ["Trips - DE", "Parents' Trip"],
        "state": "Delaware",
        "country": "USA",
    },
    {
        "title": "New Jersey, USA",
        "lat": 40.0583,
        "lng": -74.4057,
        "subtitle": "Visited Places",
        "notes": ["Parents' Trip", "Car trips - NJ"],
        "state": "New Jersey",
        "country": "USA",
    },
    {
        "title": "Tennessee, USA",
        "lat": 35.5175,
        "lng": -86.5804,
        "subtitle": "Visited Places",
        "notes": ["TN Trip with CG"],
        "state": "Tennessee",
        "country": "USA",
    },
    {
        "title": "Maryland, USA",
        "lat": 39.0458,
        "lng": -76.6413,
        "subtitle": "Visited Places",
        "notes": ["Visiting Tapas / Maryland Trip", "Car trips - MD", "Car trips - Baltimore"],
        "state": "Maryland",
        "country": "USA",
    },
    {
        "title": "Philadelphia, Pennsylvania, USA",
        "lat": CITY_COORDS["Philadelphia"][0],
        "lng": CITY_COORDS["Philadelphia"][1],
        "subtitle": "Visited Places",
        "notes": ["Car trips - Philly"],
        "state": "Pennsylvania",
        "city": "Philadelphia",
        "country": "USA",
    },
    {
        "title": "Baltimore, Maryland, USA",
        "lat": CITY_COORDS["Baltimore"][0],
        "lng": CITY_COORDS["Baltimore"][1],
        "subtitle": "Visited Places",
        "notes": ["Car trips - Baltimore"],
        "state": "Maryland",
        "city": "Baltimore",
        "country": "USA",
    },
    {
        "title": "Upper Peninsula, Michigan, USA",
        "lat": PARK_REGION_COORDS["Upper Peninsula, Michigan"][0],
        "lng": PARK_REGION_COORDS["Upper Peninsula, Michigan"][1],
        "subtitle": "Visited Places",
        "notes": ["Car trips - UP"],
        "state": "Michigan",
        "country": "USA",
    },
]


MUG_STATES = [
    ("Alaska", "Viraj"),
    ("Maine", ""),
    ("Louisiana", "Tapas"),
    ("Indiana", ""),
    ("Rhode Island", ""),
    ("Massachusetts", ""),
    ("Connecticut", ""),
    ("West Virginia", ""),
    ("Tennessee", ""),
    ("Virginia", ""),
    ("New Mexico", "CG"),
    ("Delaware", ""),
    ("Colorado", ""),
    ("Illinois", ""),
    ("Ohio", "Puneeth"),
    ("Maryland", ""),
    ("Florida", "Hannah"),
    ("Nevada", "Viraj"),
    ("South Carolina", "Nishita"),
    ("Texas", "Tathagat Uncle"),
    ("Washington", "Advait"),
    ("Minnesota", "Anthony"),
    ("New York", ""),
    ("California", ""),
    ("Oregon", "Shreeansh"),
    ("North Carolina", "Sanika"),
    ("New Jersey", "Advait"),
    ("Pennsylvania", ""),
]

MUG_CITIES = [
    ("Pittsburgh", "Shamitha", "USA", "Pennsylvania"),
    ("Chicago", "Rishabh", "USA", "Illinois"),
    ("Miami", "Hamdi", "USA", "Florida"),
    ("Mumbai", "Shantnu", "India", ""),
    ("Washington DC", "Sara", "USA", "District of Columbia"),
    ("Seoul", "Roshnee's Sister", "South Korea", ""),
    ("Dublin", "Michael", "Ireland", ""),
    ("Venezia", "Michael", "Italy", ""),
    ("Barcelona", "Michael", "Spain", ""),
    ("Dubai", "Areej", "UAE", ""),
    ("Oslo", "Michael", "Norway", ""),
    ("Stockholm", "Michael", "Sweden", ""),
    ("Savannah", "Lohith", "USA", "Georgia"),
    ("Athens", "Michael", "Greece", ""),
    ("Myrtle Beach", "Tapas and Kirti", "USA", "South Carolina"),
]

MUG_COUNTRIES = [
    ("France", "Zaid"),
    ("England", "Puneeth's Sister"),
]


def build_travel_points():
    points = []

    for item in VISITED_LOCATIONS:
        points.append(
            _point(
                kind="visited",
                title=item["title"],
                lat=item["lat"],
                lng=item["lng"],
                subtitle=item.get("subtitle", "Visited Places"),
                notes=item.get("notes", []),
                country=item.get("country", ""),
                state=item.get("state", ""),
                city=item.get("city", ""),
                photos=item.get("photos", []),
            )
        )

    for state_name, gifted_by in MUG_STATES:
        lat, lng = STATE_COORDS[state_name]
        points.append(
            _point(
                kind="mug",
                title=f"{state_name}, USA",
                lat=lat,
                lng=lng,
                subtitle="Starbucks Mug Collection",
                gifted_by=gifted_by,
                mug_type="State",
                state=state_name,
                country="USA",
            )
        )

    for city_name, gifted_by, country_name, state_name in MUG_CITIES:
        lat, lng = CITY_COORDS[city_name]
        points.append(
            _point(
                kind="mug",
                title=city_name,
                lat=lat,
                lng=lng,
                subtitle="Starbucks Mug Collection",
                gifted_by=gifted_by,
                mug_type="City",
                city=city_name,
                state=state_name,
                country=country_name,
            )
        )

    for country_name, gifted_by in MUG_COUNTRIES:
        lat, lng = COUNTRY_COORDS[country_name]
        points.append(
            _point(
                kind="mug",
                title=country_name,
                lat=lat,
                lng=lng,
                subtitle="Starbucks Mug Collection",
                gifted_by=gifted_by,
                mug_type="Country",
                country=country_name,
            )
        )

    return points


def travel_page_context():
    points = build_travel_points()
    return {
        "travel_points": points,
        "travel_gallery": [
            {
                "title": "Mug Collection (atleast a part of it lol)",
                "caption": "Starbucks mug collection display",
                "img_id": "travel-mugs-photo",
                "fallback_id": "travel-mugs-fallback",
                "primary_path": "images/travel/mugs.JPEG",
                "fallback_paths": [
                    "images/travel/mug-collection.jpeg",
                    "images/travel/mug-collection.jpg",
                    "images/travel/mugs.jpeg",
                    "images/travel/mugs.JPG",
                    "images/travel/mugs.JPEG",
                    "images/travel/mugs.jpg",
                ],
            },
            {
                "title": "Travel Magnets",
                "caption": "Fridge magnet collection",
                "img_id": "travel-magnet-photo",
                "fallback_id": "travel-magnet-fallback",
                "primary_path": "images/travel/fridge-magnets.jpeg",
                "fallback_paths": [
                    "images/travel/fridge-magnets.jpg",
                    "images/travel/fridge-magnets.png",
                    "images/travel/magnets.jpeg",
                    "images/travel/magnets.jpg",
                ],
            },
        ],
    }
