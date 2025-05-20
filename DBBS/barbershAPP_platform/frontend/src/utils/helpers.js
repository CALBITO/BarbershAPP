/**
 * Utility functions for the barbershop application
 */

// Time formatting
export const formatTime = (minutes) => {
    if (!minutes) return '0m';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
};

// Distance calculations
export const calculateDistance = (point1, point2) => {
    const R = 3959; // Earth's radius in miles
    const lat1 = toRadian(point1.lat);
    const lat2 = toRadian(point2.lat);
    const dLat = toRadian(point2.lat - point1.lat);
    const dLon = toRadian(point2.lng - point1.lng);

    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1) * Math.cos(lat2) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return Math.round((R * c) * 10) / 10; // Round to 1 decimal place
};

// Convert degrees to radians
const toRadian = (degree) => degree * Math.PI / 180;

// Phone number formatting
export const formatPhoneNumber = (phone) => {
    if (!phone) return '';
    const cleaned = phone.replace(/\D/g, '');
    return cleaned.length === 10 ? 
        `(${cleaned.slice(0,3)}) ${cleaned.slice(3,6)}-${cleaned.slice(6)}` : 
        cleaned;
};

// Date and time formatting
export const formatDateTime = (date) => {
    return new Date(date).toLocaleString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
    });
};

// Input validation
export const validators = {
    email: (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email),
    phone: (phone) => /^\+?[\d\s-]{10,}$/.test(phone),
    name: (name) => name.length >= 2
};

// Queue estimation
export const estimateWaitTime = (position, averageServiceTime = 30) => {
    return position * averageServiceTime;
};

// Error handling
export const getErrorMessage = (error) => {
    if (error.response) {
        return error.response.data.message || 'Server error occurred';
    }
    return error.message || 'An unexpected error occurred';
};

// Local storage helpers
export const storage = {
    set: (key, value) => localStorage.setItem(key, JSON.stringify(value)),
    get: (key) => {
        try {
            return JSON.parse(localStorage.getItem(key));
        } catch {
            return null;
        }
    },
    remove: (key) => localStorage.removeItem(key)
};