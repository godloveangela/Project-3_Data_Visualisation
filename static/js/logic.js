// Create the tile layer that will be the background of our map
var darkmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}", {
  attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
  maxZoom: 2,
  id: "dark-v10",
  accessToken: API_KEY
});

// Initialize all of the LayerGroups we'll be using
var layers = {
  Ornithischia: new L.LayerGroup(), 
  Saurischia: new L.LayerGroup(), 
  Aves: new L.LayerGroup()
};

//  Ornithischia/ Saurischia/ Aves
// Create the map with our layers
var map = L.map("map-id", {
  center: [28.5, 9.566667],
  zoom: 6
});

// Add our 'lightmap' tile layer to the map
darkmap.addTo(map);

// Create an overlays object to add to the layer control
var overlays = {
  "Ornithischia": layers.Ornithischia,
  "Saurischia": layers.Saurischia,
  "Aves": layers.Aves
};

// Create a control for our layers, add our overlay layers to it
L.control.layers(null, overlays).addTo(map);

// Create a legend to display information about our map
var info = L.control({
  position: "bottomright"
});

// When the layer control is added, insert a div with the class of "legend"
info.onAdd = function() {
  var div = L.DomUtil.create("div", "legend");
  return div;
};
// Add the info legend to the map
info.addTo(map);

// Initialize an object containing icons for each layer group
var icons = {
  Ornithischia: L.ExtraMarkers.icon({
    // icon: "ion-settings",
    iconColor: "white",
    markerColor: "yellow",
    shape: "star"
  }),
  Saurischia: L.ExtraMarkers.icon({
    // icon: "ion-android-bicycle",
    iconColor: "white",
    markerColor: "red",
    shape: "circle"
  }),
  Aves: L.ExtraMarkers.icon({
    // icon: "ion-minus-circled",
    iconColor: "white",
    markerColor: "blue-dark",
    shape: "penta"
  })
};

d3.json('https://paleobiodb.org/data1.2/specs/list.json?datainfo&rowcount&base_name=Saurischia,Ornithischia&max_ma=251&min_ma=66&show=class,coords,paleoloc').then(res => {
    const dinosaurList = res.records
    const dinosarurTypeArr = []
  
      dinosaurList.slice(0, 1400).map((item, index) => {
      
      let type = 'Ornithischia'
      const cList = [80, 120, 240, 360, 460, 520, 580, 640, 760, 880, 990, 1020, 1200, 1340]
      if(index >= 840) type ='Saurischia'
      if (cList.includes(index)) type = 'Aves'
      
      const marker = L.marker([item.lat, item.lng], {
        icon: icons[type],
        text: type
      }).addTo(map)
  
      marker.bindPopup(`
                      <p>type: ${type}-${item.gnl ?? 'unspecified'}</p>
                      <p>earliest-appearance: ${item.eag}</p>
                      <p>latest-appearance: ${item.lag}</p>
                      <p>latitute: ${item.lat}</p>
                      <p>longtide: ${item.lng}</p>
                      `)
        
      if (!dinosarurTypeArr.includes(item.idn)) dinosarurTypeArr.push(item.idn)
    })
})
