import React, { createContext, useContext, useState } from 'react';
import { api } from '../services/api';

const QueueContext = createContext(null);

export const QueueProvider = ({ children }) => {
    const [queueStatus, setQueueStatus] = useState(null);
    const [currentPosition, setCurrentPosition] = useState(null);

    const updateQueue = async (shopId) => {
        try {
            const status = await api.getQueueStatus(shopId);
            setQueueStatus(status);
            return status;
        } catch (error) {
            console.error('Queue update failed:', error);
            return null;
        }
    };

    const joinQueue = async (shopId, userId) => {
        try {
            const position = await api.joinQueue(shopId, userId);
            setCurrentPosition(position);
            return position;
        } catch (error) {
            console.error('Failed to join queue:', error);
            return null;
        }
    };

    return (
        <QueueContext.Provider value={{
            queueStatus,
            currentPosition,
            updateQueue,
            joinQueue
        }}>
            {children}
        </QueueContext.Provider>
    );
};

export const useQueue = () => useContext(QueueContext);