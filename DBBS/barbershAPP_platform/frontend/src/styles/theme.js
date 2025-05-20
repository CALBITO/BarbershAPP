import React, { useEffect, useState } from 'react';
import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';
import { useGeolocation } from '../../hooks/useGeolocation';
import { dcGisApi } from '../../services/GISAPI';
// No auth decorator needed - public component

const BarbershopMap = () => {
    const [shops, setShops] = useState([]);
    const { location } = useGeolocation();
    
    useEffect(() => {
        const loadShops = async () => {
            const data = await dcGisApi.getBarberShops();
            setShops(data);
        };
        loadShops();
    }, []);

    return (
        <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
            <GoogleMap
                center={location || { lat: 38.9072, lng: -77.0369 }}
                zoom={13}
                mapContainerStyle={{ height: '400px', width: '100%' }}
            >
                {shops.map(shop => (
                    <Marker
                        key={shop.id}
                        position={shop.location}
                        title={shop.name}
                    />
                ))}
            </GoogleMap>
        </LoadScript>
    );
};

export default BarbershopMap;