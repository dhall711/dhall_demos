export type Airport = {
  iata: string;
  name: string;
  city: string;
  country: string;
  tz: string;
  lat: number;
  lon: number;
};

export const AIRPORTS: Airport[] = [
  { iata: "JFK", name: "John F. Kennedy International", city: "New York", country: "USA", tz: "America/New_York", lat: 40.64, lon: -73.78 },
  { iata: "EWR", name: "Newark Liberty International", city: "Newark", country: "USA", tz: "America/New_York", lat: 40.69, lon: -74.17 },
  { iata: "LGA", name: "LaGuardia", city: "New York", country: "USA", tz: "America/New_York", lat: 40.78, lon: -73.87 },
  { iata: "BOS", name: "Logan International", city: "Boston", country: "USA", tz: "America/New_York", lat: 42.36, lon: -71.01 },
  { iata: "PHL", name: "Philadelphia International", city: "Philadelphia", country: "USA", tz: "America/New_York", lat: 39.87, lon: -75.24 },
  { iata: "IAD", name: "Washington Dulles", city: "Washington", country: "USA", tz: "America/New_York", lat: 38.95, lon: -77.46 },
  { iata: "DCA", name: "Ronald Reagan National", city: "Washington", country: "USA", tz: "America/New_York", lat: 38.85, lon: -77.04 },
  { iata: "BWI", name: "Baltimore/Washington", city: "Baltimore", country: "USA", tz: "America/New_York", lat: 39.18, lon: -76.67 },
  { iata: "ATL", name: "Hartsfield-Jackson", city: "Atlanta", country: "USA", tz: "America/New_York", lat: 33.64, lon: -84.43 },
  { iata: "MIA", name: "Miami International", city: "Miami", country: "USA", tz: "America/New_York", lat: 25.8, lon: -80.29 },
  { iata: "MCO", name: "Orlando International", city: "Orlando", country: "USA", tz: "America/New_York", lat: 28.43, lon: -81.31 },
  { iata: "CLT", name: "Charlotte Douglas", city: "Charlotte", country: "USA", tz: "America/New_York", lat: 35.21, lon: -80.95 },
  { iata: "DTW", name: "Detroit Metro", city: "Detroit", country: "USA", tz: "America/Detroit", lat: 42.21, lon: -83.35 },
  { iata: "ORD", name: "O'Hare International", city: "Chicago", country: "USA", tz: "America/Chicago", lat: 41.97, lon: -87.91 },
  { iata: "MDW", name: "Chicago Midway", city: "Chicago", country: "USA", tz: "America/Chicago", lat: 41.79, lon: -87.75 },
  { iata: "MSP", name: "Minneapolis–Saint Paul", city: "Minneapolis", country: "USA", tz: "America/Chicago", lat: 44.88, lon: -93.22 },
  { iata: "DFW", name: "Dallas/Fort Worth", city: "Dallas", country: "USA", tz: "America/Chicago", lat: 32.9, lon: -97.04 },
  { iata: "IAH", name: "George Bush Intercontinental", city: "Houston", country: "USA", tz: "America/Chicago", lat: 29.99, lon: -95.34 },
  { iata: "AUS", name: "Austin-Bergstrom", city: "Austin", country: "USA", tz: "America/Chicago", lat: 30.19, lon: -97.67 },
  { iata: "BNA", name: "Nashville International", city: "Nashville", country: "USA", tz: "America/Chicago", lat: 36.13, lon: -86.68 },
  { iata: "DEN", name: "Denver International", city: "Denver", country: "USA", tz: "America/Denver", lat: 39.86, lon: -104.67 },
  { iata: "SLC", name: "Salt Lake City International", city: "Salt Lake City", country: "USA", tz: "America/Denver", lat: 40.79, lon: -111.98 },
  { iata: "PHX", name: "Phoenix Sky Harbor", city: "Phoenix", country: "USA", tz: "America/Phoenix", lat: 33.43, lon: -112.01 },
  { iata: "LAS", name: "Harry Reid International", city: "Las Vegas", country: "USA", tz: "America/Los_Angeles", lat: 36.08, lon: -115.15 },
  { iata: "LAX", name: "Los Angeles International", city: "Los Angeles", country: "USA", tz: "America/Los_Angeles", lat: 33.94, lon: -118.41 },
  { iata: "SAN", name: "San Diego International", city: "San Diego", country: "USA", tz: "America/Los_Angeles", lat: 32.73, lon: -117.19 },
  { iata: "SFO", name: "San Francisco International", city: "San Francisco", country: "USA", tz: "America/Los_Angeles", lat: 37.62, lon: -122.38 },
  { iata: "SJC", name: "Norman Y. Mineta", city: "San Jose", country: "USA", tz: "America/Los_Angeles", lat: 37.36, lon: -121.93 },
  { iata: "SEA", name: "Seattle-Tacoma", city: "Seattle", country: "USA", tz: "America/Los_Angeles", lat: 47.45, lon: -122.31 },
  { iata: "PDX", name: "Portland International", city: "Portland", country: "USA", tz: "America/Los_Angeles", lat: 45.59, lon: -122.6 },
  { iata: "HNL", name: "Daniel K. Inouye International", city: "Honolulu", country: "USA", tz: "Pacific/Honolulu", lat: 21.32, lon: -157.92 },
  { iata: "ANC", name: "Ted Stevens Anchorage", city: "Anchorage", country: "USA", tz: "America/Anchorage", lat: 61.17, lon: -150.0 },
  { iata: "YYZ", name: "Toronto Pearson", city: "Toronto", country: "Canada", tz: "America/Toronto", lat: 43.68, lon: -79.63 },
  { iata: "YVR", name: "Vancouver International", city: "Vancouver", country: "Canada", tz: "America/Vancouver", lat: 49.19, lon: -123.18 },
  { iata: "YUL", name: "Montréal-Trudeau", city: "Montreal", country: "Canada", tz: "America/Toronto", lat: 45.47, lon: -73.74 },
  { iata: "YYC", name: "Calgary International", city: "Calgary", country: "Canada", tz: "America/Edmonton", lat: 51.12, lon: -114.01 },
  { iata: "MEX", name: "Mexico City International", city: "Mexico City", country: "Mexico", tz: "America/Mexico_City", lat: 19.44, lon: -99.07 },
  { iata: "CUN", name: "Cancún International", city: "Cancun", country: "Mexico", tz: "America/Cancun", lat: 21.04, lon: -86.87 },
  { iata: "GRU", name: "São Paulo/Guarulhos", city: "Sao Paulo", country: "Brazil", tz: "America/Sao_Paulo", lat: -23.44, lon: -46.47 },
  { iata: "GIG", name: "Rio de Janeiro/Galeão", city: "Rio de Janeiro", country: "Brazil", tz: "America/Sao_Paulo", lat: -22.81, lon: -43.25 },
  { iata: "EZE", name: "Ministro Pistarini", city: "Buenos Aires", country: "Argentina", tz: "America/Argentina/Buenos_Aires", lat: -34.82, lon: -58.54 },
  { iata: "BOG", name: "El Dorado International", city: "Bogota", country: "Colombia", tz: "America/Bogota", lat: 4.7, lon: -74.15 },
  { iata: "LIM", name: "Jorge Chávez International", city: "Lima", country: "Peru", tz: "America/Lima", lat: -12.02, lon: -77.11 },
  { iata: "SCL", name: "Arturo Merino Benítez", city: "Santiago", country: "Chile", tz: "America/Santiago", lat: -33.39, lon: -70.79 },
  { iata: "LHR", name: "Heathrow", city: "London", country: "UK", tz: "Europe/London", lat: 51.47, lon: -0.45 },
  { iata: "LGW", name: "Gatwick", city: "London", country: "UK", tz: "Europe/London", lat: 51.15, lon: -0.19 },
  { iata: "STN", name: "Stansted", city: "London", country: "UK", tz: "Europe/London", lat: 51.89, lon: 0.26 },
  { iata: "CDG", name: "Charles de Gaulle", city: "Paris", country: "France", tz: "Europe/Paris", lat: 49.01, lon: 2.55 },
  { iata: "ORY", name: "Orly", city: "Paris", country: "France", tz: "Europe/Paris", lat: 48.72, lon: 2.36 },
  { iata: "AMS", name: "Amsterdam Schiphol", city: "Amsterdam", country: "Netherlands", tz: "Europe/Amsterdam", lat: 52.31, lon: 4.76 },
  { iata: "FRA", name: "Frankfurt am Main", city: "Frankfurt", country: "Germany", tz: "Europe/Berlin", lat: 50.04, lon: 8.56 },
  { iata: "MUC", name: "Munich", city: "Munich", country: "Germany", tz: "Europe/Berlin", lat: 48.35, lon: 11.79 },
  { iata: "BER", name: "Berlin Brandenburg", city: "Berlin", country: "Germany", tz: "Europe/Berlin", lat: 52.37, lon: 13.5 },
  { iata: "ZRH", name: "Zurich", city: "Zurich", country: "Switzerland", tz: "Europe/Zurich", lat: 47.46, lon: 8.55 },
  { iata: "VIE", name: "Vienna International", city: "Vienna", country: "Austria", tz: "Europe/Vienna", lat: 48.11, lon: 16.57 },
  { iata: "FCO", name: "Leonardo da Vinci–Fiumicino", city: "Rome", country: "Italy", tz: "Europe/Rome", lat: 41.8, lon: 12.25 },
  { iata: "MXP", name: "Milan Malpensa", city: "Milan", country: "Italy", tz: "Europe/Rome", lat: 45.63, lon: 8.72 },
  { iata: "MAD", name: "Adolfo Suárez Madrid–Barajas", city: "Madrid", country: "Spain", tz: "Europe/Madrid", lat: 40.47, lon: -3.56 },
  { iata: "BCN", name: "Barcelona–El Prat", city: "Barcelona", country: "Spain", tz: "Europe/Madrid", lat: 41.3, lon: 2.08 },
  { iata: "LIS", name: "Humberto Delgado", city: "Lisbon", country: "Portugal", tz: "Europe/Lisbon", lat: 38.77, lon: -9.13 },
  { iata: "DUB", name: "Dublin", city: "Dublin", country: "Ireland", tz: "Europe/Dublin", lat: 53.43, lon: -6.27 },
  { iata: "CPH", name: "Copenhagen", city: "Copenhagen", country: "Denmark", tz: "Europe/Copenhagen", lat: 55.62, lon: 12.66 },
  { iata: "ARN", name: "Stockholm Arlanda", city: "Stockholm", country: "Sweden", tz: "Europe/Stockholm", lat: 59.65, lon: 17.92 },
  { iata: "OSL", name: "Oslo Gardermoen", city: "Oslo", country: "Norway", tz: "Europe/Oslo", lat: 60.19, lon: 11.1 },
  { iata: "HEL", name: "Helsinki-Vantaa", city: "Helsinki", country: "Finland", tz: "Europe/Helsinki", lat: 60.32, lon: 24.96 },
  { iata: "WAW", name: "Warsaw Chopin", city: "Warsaw", country: "Poland", tz: "Europe/Warsaw", lat: 52.17, lon: 20.97 },
  { iata: "PRG", name: "Václav Havel", city: "Prague", country: "Czechia", tz: "Europe/Prague", lat: 50.1, lon: 14.26 },
  { iata: "BUD", name: "Budapest Ferenc Liszt", city: "Budapest", country: "Hungary", tz: "Europe/Budapest", lat: 47.44, lon: 19.26 },
  { iata: "ATH", name: "Athens International", city: "Athens", country: "Greece", tz: "Europe/Athens", lat: 37.94, lon: 23.94 },
  { iata: "IST", name: "Istanbul", city: "Istanbul", country: "Turkey", tz: "Europe/Istanbul", lat: 41.28, lon: 28.75 },
  { iata: "DXB", name: "Dubai International", city: "Dubai", country: "UAE", tz: "Asia/Dubai", lat: 25.25, lon: 55.36 },
  { iata: "AUH", name: "Abu Dhabi International", city: "Abu Dhabi", country: "UAE", tz: "Asia/Dubai", lat: 24.43, lon: 54.65 },
  { iata: "DOH", name: "Hamad International", city: "Doha", country: "Qatar", tz: "Asia/Qatar", lat: 25.27, lon: 51.61 },
  { iata: "RUH", name: "King Khalid International", city: "Riyadh", country: "Saudi Arabia", tz: "Asia/Riyadh", lat: 24.96, lon: 46.7 },
  { iata: "TLV", name: "Ben Gurion", city: "Tel Aviv", country: "Israel", tz: "Asia/Jerusalem", lat: 32.01, lon: 34.88 },
  { iata: "CAI", name: "Cairo International", city: "Cairo", country: "Egypt", tz: "Africa/Cairo", lat: 30.12, lon: 31.41 },
  { iata: "JNB", name: "O. R. Tambo", city: "Johannesburg", country: "South Africa", tz: "Africa/Johannesburg", lat: -26.14, lon: 28.25 },
  { iata: "CPT", name: "Cape Town International", city: "Cape Town", country: "South Africa", tz: "Africa/Johannesburg", lat: -33.97, lon: 18.6 },
  { iata: "NBO", name: "Jomo Kenyatta", city: "Nairobi", country: "Kenya", tz: "Africa/Nairobi", lat: -1.32, lon: 36.93 },
  { iata: "ADD", name: "Bole International", city: "Addis Ababa", country: "Ethiopia", tz: "Africa/Addis_Ababa", lat: 8.98, lon: 38.8 },
  { iata: "LOS", name: "Murtala Muhammed", city: "Lagos", country: "Nigeria", tz: "Africa/Lagos", lat: 6.58, lon: 3.32 },
  { iata: "NRT", name: "Narita International", city: "Tokyo", country: "Japan", tz: "Asia/Tokyo", lat: 35.76, lon: 140.39 },
  { iata: "HND", name: "Haneda", city: "Tokyo", country: "Japan", tz: "Asia/Tokyo", lat: 35.55, lon: 139.78 },
  { iata: "KIX", name: "Kansai International", city: "Osaka", country: "Japan", tz: "Asia/Tokyo", lat: 34.43, lon: 135.23 },
  { iata: "ICN", name: "Incheon International", city: "Seoul", country: "South Korea", tz: "Asia/Seoul", lat: 37.46, lon: 126.44 },
  { iata: "PEK", name: "Beijing Capital", city: "Beijing", country: "China", tz: "Asia/Shanghai", lat: 40.08, lon: 116.58 },
  { iata: "PVG", name: "Shanghai Pudong", city: "Shanghai", country: "China", tz: "Asia/Shanghai", lat: 31.14, lon: 121.81 },
  { iata: "HKG", name: "Hong Kong International", city: "Hong Kong", country: "Hong Kong", tz: "Asia/Hong_Kong", lat: 22.31, lon: 113.91 },
  { iata: "TPE", name: "Taiwan Taoyuan", city: "Taipei", country: "Taiwan", tz: "Asia/Taipei", lat: 25.08, lon: 121.23 },
  { iata: "SIN", name: "Singapore Changi", city: "Singapore", country: "Singapore", tz: "Asia/Singapore", lat: 1.36, lon: 103.99 },
  { iata: "BKK", name: "Suvarnabhumi", city: "Bangkok", country: "Thailand", tz: "Asia/Bangkok", lat: 13.69, lon: 100.75 },
  { iata: "SGN", name: "Tan Son Nhat", city: "Ho Chi Minh City", country: "Vietnam", tz: "Asia/Ho_Chi_Minh", lat: 10.82, lon: 106.65 },
  { iata: "MNL", name: "Ninoy Aquino", city: "Manila", country: "Philippines", tz: "Asia/Manila", lat: 14.51, lon: 121.02 },
  { iata: "KUL", name: "Kuala Lumpur International", city: "Kuala Lumpur", country: "Malaysia", tz: "Asia/Kuala_Lumpur", lat: 2.75, lon: 101.71 },
  { iata: "CGK", name: "Soekarno–Hatta", city: "Jakarta", country: "Indonesia", tz: "Asia/Jakarta", lat: -6.13, lon: 106.66 },
  { iata: "DEL", name: "Indira Gandhi International", city: "Delhi", country: "India", tz: "Asia/Kolkata", lat: 28.56, lon: 77.1 },
  { iata: "BOM", name: "Chhatrapati Shivaji Maharaj", city: "Mumbai", country: "India", tz: "Asia/Kolkata", lat: 19.09, lon: 72.87 },
  { iata: "BLR", name: "Kempegowda International", city: "Bengaluru", country: "India", tz: "Asia/Kolkata", lat: 13.2, lon: 77.71 },
  { iata: "SYD", name: "Sydney Kingsford Smith", city: "Sydney", country: "Australia", tz: "Australia/Sydney", lat: -33.94, lon: 151.18 },
  { iata: "MEL", name: "Melbourne", city: "Melbourne", country: "Australia", tz: "Australia/Melbourne", lat: -37.67, lon: 144.84 },
  { iata: "BNE", name: "Brisbane", city: "Brisbane", country: "Australia", tz: "Australia/Brisbane", lat: -27.38, lon: 153.12 },
  { iata: "PER", name: "Perth", city: "Perth", country: "Australia", tz: "Australia/Perth", lat: -31.94, lon: 115.97 },
  { iata: "AKL", name: "Auckland", city: "Auckland", country: "New Zealand", tz: "Pacific/Auckland", lat: -37.01, lon: 174.79 },
];

const byIata = new Map(AIRPORTS.map((airport) => [airport.iata, airport]));

export function getAirport(iata: string): Airport | undefined {
  return byIata.get(iata.toUpperCase());
}

export function requireAirport(iata: string): Airport {
  const airport = getAirport(iata);
  if (!airport) {
    throw new Error(`Unknown airport ${iata}`);
  }
  return airport;
}

export function searchAirports(query: string, limit = 8): Airport[] {
  const q = query.trim().toLowerCase();
  if (!q) {
    return AIRPORTS.slice(0, limit);
  }
  const scored = AIRPORTS.map((airport) => {
    const iata = airport.iata.toLowerCase();
    const city = airport.city.toLowerCase();
    const name = airport.name.toLowerCase();
    const country = airport.country.toLowerCase();
    let score = 0;
    if (iata === q) score = 100;
    else if (iata.startsWith(q)) score = 90;
    else if (city.startsWith(q)) score = 80;
    else if (city.includes(q)) score = 60;
    else if (name.toLowerCase().includes(q)) score = 40;
    else if (country.startsWith(q)) score = 20;
    else if (`${city} ${iata} ${name} ${country}`.includes(q)) score = 10;
    return { airport, score };
  })
    .filter((row) => row.score > 0)
    .sort((a, b) => b.score - a.score || a.airport.city.localeCompare(b.airport.city));
  return scored.slice(0, limit).map((row) => row.airport);
}

export function airportLabel(airport: Airport): string {
  return `${airport.city} (${airport.iata})`;
}
