import api from '../api';

const bookingService = {
    createAppointment: async (appointmentData) => {
        const response = await api.post('/appointments', appointmentData);
        return response.data;
    },

    getAppointments: async () => {
        const response = await api.get('/appointments');
        return response.data;
    },

    cancelAppointment: async (appointmentId) => {
        const response = await api.delete(`/appointments/${appointmentId}`);
        return response.data;
    },

    getAvailableSlots: async (shopId, date) => {
        const response = await api.get(`/shops/${shopId}/slots`, {
            params: { date: date.toISOString() }
        });
        return response.data;
    }
};

export default bookingService;