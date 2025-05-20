import React, { createContext, useContext, useState } from 'react';
import { bookingService } from '../services';

const BookingContext = createContext(null);

export const BookingProvider = ({ children }) => {
    const [bookings, setBookings] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const createBooking = async (bookingData) => {
        setLoading(true);
        try {
            const response = await bookingService.createAppointment(bookingData);
            setBookings([...bookings, response]);
            return response;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const value = {
        bookings,
        loading,
        error,
        createBooking
    };

    return (
        <BookingContext.Provider value={value}>
            {children}
        </BookingContext.Provider>
    );
};

export const useBooking = () => {
    const context = useContext(BookingContext);
    if (!context) {
        throw new Error('useBooking must be used within a BookingProvider');
    }
    return context;
};