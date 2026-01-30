import React, {useEffect, useRef} from 'react';
import Map from "ol/Map";
import TileLayer from "ol/layer/Tile";
import {OSM, TileWMS} from "ol/source";
import {View} from "ol";
import {useGeographic} from "ol/proj";
import 'ol/ol.css';

function MapComponent(props) {
    const mapRef = useRef(null);
    useGeographic();
    useEffect(() => {
        const map = new Map({
            target: mapRef.current,
            layers:[
                new TileLayer({
                    source: new OSM(),
                }),
                new TileLayer({
                    opacity: 0.3,
                    //http://localhost:9000/geoserver/ne/wms?service=WMS&version=1.1.0&request=GetMap&layers=ne%3Acountries&bbox=-180.0%2C-90.0%2C180.0%2C83.64513&width=768&height=370&srs=EPSG%3A4326&styles=&format=application/openlayers
                    source: new TileWMS({
                        url: 'http://localhost:9000/geoserver/ne/wms?',
                        params: {
                            "layers": "ne:countries",
                            "TILED": true,
                        },
                        serverType: "geoserver",
                        transition: 1000,
                    })
                }),
                new TileLayer({
                    //http://localhost:9000/geoserver/prge/wms?service=WMS&version=1.1.0&request=GetMap&layers=prge%3Ausers&bbox=13.771362%2C49.077464%2C25.032349%2C55.043762&width=768&height=406&srs=EPSG%3A4326&styles=&format=application/openlayers
                    source: new TileWMS({
                        url: 'http://localhost:9000/geoserver/prge/wms?',
                        params: {
                            "layers": "prge:users",
                            "TILED": true,
                        },
                        serverType: "geoserver",
                        transition: 500
                    })
                })
            ],
            view: new View({
                center: [21, 51],
                zoom: 6
            })
        })
        return () => map.setTarget(null)
    },
        []);

    return (
        <div className='MapComponent' ref={mapRef}>
        </div>
    );
}

export default MapComponent;