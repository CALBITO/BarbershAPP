import React, { useState, useEffect } from 'react';

function BarberQueue({ barbershopId }) {
    const [queues, setQueues] = useState([]);

    useEffect(() => {
        fetch(`/queue/${barbershopId}`)
            .then((response) => response.json())
            .then((data) => setQueues(data))
            .catch((error) => console.error('Error fetching queue data:', error));
    }, [barbershopId]);

    return (
        <div>
            <h3>Barber Availability</h3>
            <ul>
                {queues.map((queue) => (
                    <li key={queue.id}>
                        <strong>Barber ID:</strong> {queue.barber_id} <br />
                        <strong>Queue Size:</strong> {queue.queue_size} <br />
                        <strong>Estimated Wait Time:</strong> {queue.estimated_wait_time} minutes <br />
                        <strong>Last Updated:</strong> {new Date(queue.last_updated).toLocaleString()}
                    </li>
                ))}
            </ul>
        </div>
    );
}

