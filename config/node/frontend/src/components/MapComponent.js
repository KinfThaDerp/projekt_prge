import React, {useEffect, useRef} from 'react';
import Map from "ol/Map";
import {bbox as bboxStrategy} from 'ol/loadingstrategy.js';
import GeoJSON from 'ol/format/GeoJSON.js';
import TileLayer from "ol/layer/Tile";
import {OSM, TileWMS} from "ol/source";
import VectorLayer from 'ol/layer/Vector.js';
import VectorSource from 'ol/source/Vector.js';
import {View} from "ol";
import Style from 'ol/style/Style.js';
import Stroke from 'ol/style/Stroke.js';
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
                    //http://localhost:9000/geoserver/ne/wms?service=WMS&version=1.1.0&request=GetMap&layers=ne%3Acountries&bbox=-180.0%2C-90.0%2C180.0%2C83.64513&width=768&height=370&srs=EPSG%3A4326&styles=&format=application/openlayers
                    source: new TileWMS({
                        url: 'http://localhost:9000/geoserver/ne/wms?',
                        params: {
                            "layers": "ne:countries",
                            "TILED": true,
                        },
                        serverType: "geoserver",
                        transition: 2000000,
                        opacity: 0.5
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
                        transition: 5000
                    })
                })
                // new VectorLayer({
                //     source: new VectorSource({
                //         format: new GeoJSON(),
                //         url: function (extent) {
                //             return (
                //                 //http://localhost:9000/geoserver/ows?service=WFS&acceptversions=2.0.0&request=GetCapabilities
                //                 'http://localhost:9000/geoserver/ows?service=WFS' +
                //                 '&acceptversions=2.0.0&request=GetFeature&typename=prge:users&' +
                //                 'outputFormat=application/json&srsname=EPSG:4326&' +
                //                 'bbox=' +
                //                 extent.join(',') +
                //                 ',EPSG:4326'
                //                 );
                //             },
                //         strategy: bboxStrategy,
                //
                //         }),
                //     style: new Style({
                //         stroke: new Stroke({
                //         color: 'rgba(0, 0, 255, 1.0)',
                //         width: 2,
                //         }),
                //     })
                // })
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