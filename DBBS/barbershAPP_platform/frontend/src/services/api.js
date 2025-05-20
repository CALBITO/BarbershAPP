const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export const api = {
    // Shop endpoints
    getShops: async (lat, lng) => {
        const response = await fetch(`${API_BASE_URL}/shops?lat=${lat}&lng=${lng}`);
        return response.json();
    },

    // Booking endpoints
    createAppointment: async (data) => {
        return fetch(`${API_BASE_URL}/appointments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(res => res.json());
    }
};