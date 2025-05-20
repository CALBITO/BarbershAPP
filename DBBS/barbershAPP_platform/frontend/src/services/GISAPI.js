import { api } from './api';

const DC_API_URL = 'https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Business_Goods_and_Service_WebMercator/MapServer/36/query';

export const dcGisApi = {
    async getBarberShops() {
        const params = new URLSearchParams({
            where: '1=1',
            outFields: '*',
            outSR: '4326',
            f: 'json'
        });

        try {
            const response = await fetch(`${DC_API_URL}?${params}`);
            const data = await response.json();
            return this.transformShopData(data.features);
        } catch (error) {
            console.error('Failed to fetch DC barber shops:', error);
            throw error;
        }
    },

    transformShopData(features) {
        return features.map(feature => ({
            id: feature.attributes.OBJECTID,
            name: feature.attributes.NAME,
            address: feature.attributes.FULLADDRESS,
            location: {
                lat: feature.geometry.y,
                lng: feature.geometry.x
            },
            phone: feature.attributes.PHONE || '',
            website: feature.attributes.WEBSITE || ''
        }));
    }
};