// Geocoding utility replacing @pderas/vue2-geocoder
// Uses the native Google Maps Geocoding API loaded via @fawmi/vue-google-maps

interface AddressResult {
  formatted_address: string;
  geometry: {
    location: {
      lat: () => number;
      lng: () => number;
    };
  };
  address_components: Array<{
    short_name: string;
    long_name: string;
    types: string[];
  }>;
}

interface GeocodeResponse {
  status: string;
  results: AddressResult[];
}

type GeocodeMode = "address" | "lat-lng";

export function geocode(
  mode: GeocodeMode,
  addressObj: Record<string, string | number>,
  callback: (response: GeocodeResponse) => void
): void {
  const geocoder = new (window as any).google.maps.Geocoder();

  let request: Record<string, unknown>;
  if (mode === "address") {
    request = {
      address: `${addressObj.address_line_1}, ${addressObj.city}`
    };
  } else {
    request = {
      location: { lat: Number(addressObj.lat), lng: Number(addressObj.lng) }
    };
  }

  geocoder.geocode(
    request,
    (results: AddressResult[], status: string) => {
      callback({ status, results: results || [] });
    }
  );
}
