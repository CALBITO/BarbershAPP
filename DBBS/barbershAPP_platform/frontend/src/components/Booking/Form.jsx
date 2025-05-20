import React, { useState } from 'react';
import { TextField, Button, Box, Typography, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { useBooking } from '../../context/BookCtx';
import { DateTimePicker } from '@mui/x-date-pickers';

const BookingForm = ({ shopId }) => {
    const [bookingData, setBookingData] = useState({
        service: '',
        date: null,
        notes: ''
    });
    const { createBooking } = useBooking();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await createBooking({ ...bookingData, shopId });
        } catch (error) {
            console.error('Booking failed:', error);
        }
    };

    return (
        <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 400 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>Book Appointment</Typography>
            <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Service</InputLabel>
                <Select
                    value={bookingData.service}
                    onChange={(e) => setBookingData({ ...bookingData, service: e.target.value })}
                    required
                >
                    <MenuItem value="haircut">Haircut</MenuItem>
                    <MenuItem value="shave">Shave</MenuItem>
                    <MenuItem value="combo">Haircut & Shave</MenuItem>
                </Select>
            </FormControl>
            <DateTimePicker
                label="Date & Time"
                value={bookingData.date}
                onChange={(newValue) => setBookingData({ ...bookingData, date: newValue })}
                renderInput={(params) => <TextField {...params} fullWidth sx={{ mb: 2 }} />}
            />
            <TextField
                fullWidth
                label="Notes"
                multiline
                rows={4}
                value={bookingData.notes}
                onChange={(e) => setBookingData({ ...bookingData, notes: e.target.value })}
                sx={{ mb: 2 }}
            />
            <Button type="submit" variant="contained" fullWidth>
                Book Appointment
            </Button>
        </Box>
    );
};

export default BookingForm;