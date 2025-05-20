import authService from './api/auth';
import { mapServices } from './mapSrvs';
import bookingService from './api/booking';

export {
    authService,
    mapServices,
    bookingService
};

export const API_CONFIG = {
    BASE_URL: process.env.REACT_APP_API_URL,
    MAPS_KEY: process.env.REACT_APP_GOOGLE_MAPS_API_KEY
};