from typing import Dict

class NotificationMessages:
    WELCOME = {
        'en': "Greetings thank you for joining BarbershAPP",
        'es': "BIENVENIDOS gracias por unirte con BarbershAPP"
    }
    
    AVAILABILITY = {
        'en': "Good Day, barber {barber} is available today at {location} from {timeslots}. Book an appointment via {booking_url}",
        'es': "Buenas, barbero {barber} estas disponible desde {horarios}. Cronogramase un appointment al {booking_url}"
    }
    
    APPOINTMENT_CONFIRMED = {
        'en': "Appointment scheduled successfully: {date} at {address} with {barber}. To reschedule, call your barber or click here {change_url}",
        'es': "Appointment cronogramado: {date} en {address} con {barber}. Para cambiar, llama su barbero o haga click aqui {change_url}"
    }
    AVAILABILITY_UPDATE = {
        'en': "Barber {barber_name} at {shop_name} has new availability:\n"
              "Date: {date}\n"
              "Times: {time_slots}\n"
              "Book now: {booking_url}",
        'es': "Barbero {barber_name} en {shop_name} tiene nueva disponibilidad:\n"
              "Fecha: {date}\n"
              "Horarios: {time_slots}\n"
              "Reserva ahora: {booking_url}"
    }