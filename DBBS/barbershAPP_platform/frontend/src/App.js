import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { QueueProvider } from './context/QueueContext';
import MainLayout from './components/Layout/MainLayout';
import Routes from './Routes';

function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <QueueProvider>
                    <MainLayout>
                        <Routes />
                    </MainLayout>
                </QueueProvider>
            </AuthProvider>
        </BrowserRouter>
    );
}

export default App;