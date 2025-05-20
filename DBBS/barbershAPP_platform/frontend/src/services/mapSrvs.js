import axios from 'axios';

const DC_API_URL = process.env.REACT_APP_DC_API_URL;

export const mapServices = {
    getBarbershops: async () => {
        try {
            const response = await axios.get(DC_API_URL, {
                params: {
                    where: "BUSINESS_TYPE='Barber Shop'",
                    outFields: '*',
                    f: 'json'
                }
            });
            
            return response.data.features.map(feature => ({
                id: feature.attributes.OBJECTID,
                name: feature.attributes.BUSINESS_NAME,
                address: feature.attributes.FULL_ADDRESS,
                latitude: feature.geometry.y,
                longitude: feature.geometry.x,
                phone: feature.attributes.PHONE_NUMBER
            }));
        } catch (error) {
            console.error('Error fetching barbershops:', error);
            throw error;
        }
    },

    getDirections: async (origin, destination) => {
        try {
            const response = await axios.get(
                `https://maps.googleapis.com/maps/api/directions/json?origin=${origin}&destination=${destination}&key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}`
            );
            return response.data.routes[0];
        } catch (error) {
            console.error('Error fetching directions:', error);
            throw error;
        }
    },

    geocodeAddress: async (address) => {
        try {
            const response = await axios.get(
                `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(address)}&key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}`
            );
            
            if (response.data.results.length > 0) {
                const { lat, lng } = response.data.results[0].geometry.location;
                return { latitude: lat, longitude: lng };
            }
            throw new Error('No results found');
        } catch (error) {
            console.error('Geocoding error:', error);
            throw error;
        }
    }
};

export default mapServices;