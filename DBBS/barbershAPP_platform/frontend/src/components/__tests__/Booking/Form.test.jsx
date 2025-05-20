import React from 'react';
import { render, fireEvent, screen, waitFor } from '@testing-library/react';
import { BookingProvider } from '../../../context/BookCtx';
import BookingForm from '../../../components/Booking/Form';

describe('BookingForm', () => {
    const mockShopId = 1;
    
    beforeEach(() => {
        render(
            <BookingProvider>
                <BookingForm shopId={mockShopId} />
            </BookingProvider>
        );
    });

    it('renders all form fields', () => {
        expect(screen.getByLabelText(/service/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/date & time/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/notes/i)).toBeInTheDocument();
    });

    it('handles form submission', async () => {
        fireEvent.change(screen.getByLabelText(/service/i), {
            target: { value: 'haircut' }
        });
        
        fireEvent.change(screen.getByLabelText(/notes/i), {
            target: { value: 'Test booking' }
        });

        fireEvent.click(screen.getByText(/book appointment/i));

        await waitFor(() => {
            expect(screen.queryByText(/booking confirmed/i)).toBeInTheDocument();
        });
    });
});