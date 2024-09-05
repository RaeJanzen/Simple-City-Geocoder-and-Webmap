import './style.css';
import {Map, View} from 'ol';
import {Tile as TileLayer, Vector as VectorLayer} from 'ol/layer.js';
import {OSM, Vector as VectorSource} from 'ol/source.js';
import GeoJSON from 'ol/format/GeoJSON.js';
import Cluster from 'ol/source/Cluster.js';
import Overlay from 'ol/Overlay.js';
import Feature from 'ol/Feature.js';
import {
	Circle as CircleStyle,
	Fill,
	Stroke,
	Style,
	Text,
} from 'ol/style.js';

/* popup config */
const content = document.getElementById('popup-text');
const closer = document.getElementById('popup-closer');
	//overlay for popup
const popup = new Overlay({
  element: document.getElementById('popup'),
  autoPan: true,
});
	//closer to hide popup 
closer.onclick = function () {
  popup.setPosition(undefined);
  closer.blur();
  return false;
};
	//function to generate popup content based on user interaction
const displayFeatureInfo = function(pixel, coordinate) {
	const features = [];
	map.forEachFeatureAtPixel(pixel, function(feature, layer) {
		features.push(feature.values_.features);
	});
    if (features[0] != undefined && features[0].length > 0) {
		let info = '';
		for (let i = 0, ii = features[0].length; i < ii; ++i) {
			let value = features[0][i].values_;
			if (i == ii - 1) {
				info = info + "Location: " + value.city + ", " + value.country +
				       "<br/>Count: " + value.count;
			} else {
				info = info + "Location: " + value.city + ", " + value.country +
					   "<br/>Count: " + value.count + "<br/><br/>";
			}
		}
		content.innerHTML = info;
		popup.setPosition(coordinate);
    } else {
		popup.setPosition(undefined);
    }
};

/* layers config */
	//data from GeoJSON
const rawData = new VectorSource({
	format: new GeoJSON(),
	url: './layers/city_locations.geojson',
});
	//cluster the data 
const clusterSource = new Cluster({
	source: rawData,
	distance: 8,
});
	//get count of features within cluster and 
	//config layer style
function clusterStyle (feature){
	let total = feature.values_.features.length;
	const circle = new CircleStyle({
		radius: total * 1.3 + 5,
		fill: new Fill({
			color: 'rgba(204, 163, 0,0.4)',
		}),
		stroke: new Stroke({
			color: 'rgba(204, 163, 0,1)',
			width: 0.8,
		}),
	});
	const style = new Style({
		image: circle,
	});
	return style
};
	//display data as clusters
const clusterLayer = new VectorLayer({
	source: clusterSource,
	style: clusterStyle,
});

/* map */

const map = new Map({
  target: 'map',
  layers: [
    new TileLayer({
      source: new OSM()
    }),
	clusterLayer,
  ],
  overlays: [popup],
  view: new View({
    center: [0, 0],
    zoom: 2
  })
});

/* popup on click */
map.on('singleclick', function (evt) {
	const coordinate = evt.coordinate;
	displayFeatureInfo(evt.pixel, coordinate);
});