import React from 'react';
import Navbar from './Navbar';

const MainLayout = ({ children }) => {
    return (
        <div className="app-container">
            <Navbar />
            <main className="main-content">
                {children}
            </main>
        </div>
    );
};

export default MainLayout;