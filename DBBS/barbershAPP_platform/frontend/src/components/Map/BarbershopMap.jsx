import React, { useEffect, useState } from 'react';
import { GoogleMap, LoadScript, Marker, InfoWindow } from '@react-google-maps/api';
import { useGeolocation } from '../../hooks/useGeolocation';
import { useAuth } from '../../hooks/useAuth';
import { dcGisApi } from '../../services/GISAPI';

const BarbershopMap = () => {
    const [shops, setShops] = useState([]);
    const [selectedShop, setSelectedShop] = useState(null);
    const [loading, setLoading] = useState(true);
    const { location } = useGeolocation();
    const { user } = useAuth();

    const defaultCenter = {
        lat: 38.9072,
        lng: -77.0369
    };

    const mapStyles = {
        height: '600px',
        width: '100%',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    };

    useEffect(() => {
        const loadShops = async () => {
            try {
                setLoading(true);
                const data = await dcGisApi.getBarberShops();
                setShops(data);
            } catch (error) {
                console.error('Failed to load shops:', error);
            } finally {
                setLoading(false);
            }
        };

        loadShops();
    }, []);

    const handleMarkerClick = (shop) => {
        setSelectedShop(shop);
    };

    const handleInfoWindowClose = () => {
        setSelectedShop(null);
    };

    if (loading) {
        return <div className="loading">Loading barbershops...</div>;
    }

    return (
        <div className="map-container">
            <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
                <GoogleMap
                    mapContainerStyle={mapStyles}
                    zoom={13}
                    center={location || defaultCenter}
                    options={{
                        streetViewControl: false,
                        mapTypeControl: false,
                        fullscreenControl: true
                    }}
                >
                    {shops.map(shop => (
                        <Marker
                            key={shop.id}
                            position={{
                                lat: shop.location.lat,
                                lng: shop.location.lng
                            }}
                            onClick={() => handleMarkerClick(shop)}
                            icon={{
                                url: '/barber-pin.png',
                                scaledSize: new window.google.maps.Size(30, 30)
                            }}
                        />
                    ))}

                    {selectedShop && (
                        <InfoWindow
                            position={{
                                lat: selectedShop.location.lat,
                                lng: selectedShop.location.lng
                            }}
                            onCloseClick={handleInfoWindowClose}
                        >
                            <div className="info-window">
                                <h3>{selectedShop.name}</h3>
                                <p>{selectedShop.address}</p>
                                {selectedShop.phone && (
                                    <p>Phone: {selectedShop.phone}</p>
                                )}
                                {user ? (
                                    <button 
                                        onClick={() => window.location.href = `/book/${selectedShop.id}`}
                                        className="book-button"
                                    >
                                        Book Appointment
                                    </button>
                                ) : (
                                    <p className="login-prompt">
                                        Please login to book appointments
                                    </p>
                                )}
                            </div>
                        </InfoWindow>
                    )}
                </GoogleMap>
            </LoadScript>
        </div>
    );
};

export default BarbershopMap;