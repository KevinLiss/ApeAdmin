// Common settings
var platform = new H.service.Platform({
  app_id: 'devportal-demo-20180625',
  app_code: '9v2BkviRwi9Ot26kp2IysQ',
  useHTTPS: true
});
var pixelRatio = window.devicePixelRatio || 1;
var defaultLayers = platform.createDefaultLayers({
  tileSize: pixelRatio === 1 ? 256 : 512,
  ppi: pixelRatio === 1 ? undefined : 320
});


//map 1
function moveMapToBerlin(map){
  map.setCenter({lat:52.5159, lng:13.3777});
  map.setZoom(14);
}
var map = new H.Map(document.getElementById('map1'),
  defaultLayers.normal.map, {pixelRatio: pixelRatio});
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
var ui = H.ui.UI.createDefault(map, defaultLayers);
moveMapToBerlin(map);


// map2
function setMapViewBounds(map){
  var bbox = new H.geo.Rect(42.3736,-71.0751,42.3472,-71.0408);
  map.setViewBounds(bbox);
}
var map = new H.Map(document.getElementById('map2'),
  defaultLayers.normal.map, {pixelRatio: pixelRatio});
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
var ui = H.ui.UI.createDefault(map, defaultLayers);
setMapViewBounds(map);

// map3
function switchMapLanguage(map, platform){
  var mapTileService = platform.getMapTileService({
      type: 'base'
    }),
    chineseMapLayer = mapTileService.createTileLayer(
      'maptile',
      'normal.day',
      pixelRatio === 1 ? 256 : 512,
      'png8',
      {lg: 'CHI', ppi: pixelRatio === 1 ? undefined : 320}
    );
  map.setBaseLayer(chineseMapLayer);
  var ui = H.ui.UI.createDefault(map, defaultLayers, 'zh-CN');
  ui.removeControl('mapsettings');
}
var map = new H.Map(document.getElementById('map3'),
  defaultLayers.normal.map,{
  center: {lat:22.2783, lng:114.1588},
  zoom: 12,
  pixelRatio: pixelRatio
});
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
switchMapLanguage(map , platform);

// map4
function switchMapType(map, platform){
  var aerialMapTileService = platform.getMapTileService({
    type: 'aerial'
  });
  terrainMap = aerialMapTileService.createTileLayer(
    'maptile',
    'terrain.day',
    pixelRatio === 1 ? 256 : 512,
    'png8',
    {ppi: pixelRatio === 1 ? undefined : 320}
  );
  map.setBaseLayer(terrainMap);
}
var map = new H.Map(document.getElementById('map4'),
  defaultLayers.normal.map,{
  center: {lat:27.98805, lng:86.9250},
  zoom: 10,
  pixelRatio: pixelRatio
});
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
var ui = H.ui.UI.createDefault(map, defaultLayers);
ui.removeControl('mapsettings');
switchMapType(map, platform);

// map5
function useImperialMeasurements(map, defaultLayers){
  var ui = H.ui.UI.createDefault(map, defaultLayers);
  ui.setUnitSystem(H.ui.UnitSystem.IMPERIAL);
}
var map = new H.Map(document.getElementById('map5'),
  defaultLayers.normal.map,{
  center: {lat:42.3572, lng:-71.0596},
  zoom: 14,
  pixelRatio: pixelRatio
});
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
useImperialMeasurements(map, defaultLayers);

// map6
function panTheMap(map) {
  var viewPort,
      incX = 1,
      incY = 2,
      x = 100,
      y = 100;
  var viewPort = map.getViewPort(),
      pan = function() {
        x = x + incX;
        if (Math.abs(x) > 100) {
          incX = -incX;
        }

        y = y + incY;
        if (Math.abs(y) > 100) {
          incY = -incY;
        }

        viewPort.interaction(x, y);
      };
  viewPort.startInteraction(H.map.render.RenderEngine.InteractionModifiers.COORD);
  setInterval(pan, 10);
}
var map = new H.Map(document.getElementById('map6'),
  defaultLayers.normal.map,{
  center: {lat: 19.11, lng: 72.89},
  zoom: 4,
  pixelRatio: pixelRatio
});
panTheMap(map);

// map7
function useImperialMeasurements(map, defaultLayers){
  var ui = H.ui.UI.createDefault(map, defaultLayers);
  ui.setUnitSystem(H.ui.UnitSystem.IMPERIAL);
}
var map = new H.Map(document.getElementById('map7'),
  defaultLayers.normal.map,{
  center: {lat:42.3572, lng:-71.0596},
  zoom: 14,
  pixelRatio: pixelRatio
});
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
useImperialMeasurements(map, defaultLayers);


// map 8
function addVenueLayer(map, platform, renderControls) {
  var customVenueLayer = platform.getVenueService().createTileLayer({
    onSpaceCreated: onSpaceCreated
  });
  var venueProvider = customVenueLayer.getProvider();
  map.addLayer(customVenueLayer);
  renderControls('Change floor', {
    '+1 Level': function () {
      venueProvider.setCurrentLevel(venueProvider.getCurrentLevel() + 1);
    },
    '-1 Level': function () {
      venueProvider.setCurrentLevel(venueProvider.getCurrentLevel() - 1);
    }
  });
}
function onSpaceCreated(space) {
  if (space.getData().preview === 'H&M') {
    space.setStyle({
      fillColor: 'rgba(0,255,0,0.3)'
    });
  }
}
var map = new H.Map(document.getElementById('map8'), defaultLayers.normal.map, {
  center: new H.geo.Point(52.5189, 13.4158),
  zoom: 17,
  pixelRatio: pixelRatio
});
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
var ui = H.ui.UI.createDefault(map, defaultLayers, 'en-US');
function renderControls(title, buttons) {
  var containerNode = document.createElement('div');
  containerNode.innerHTML = '<h4 class="title">' + title + '</h4><div class="btn-group"></div>';
  containerNode.setAttribute('style',
      'position:absolute;top:0;left:0;background-color:#fff; padding:10px;text-align:center');
  Object.keys(buttons).forEach(function (label) {
    var input = document.createElement('input');
    input.value = label;
    input.type = 'button';
    input.onclick = buttons[label];
    input.className="btn btn-sm btn-default"
    containerNode.lastChild.appendChild(input);
  });
  map.getElement().appendChild(containerNode);
}
addVenueLayer(map, platform, renderControls);

// map9
function setUpCustomZooming(map) {
  var clevelandCircle = new H.map.Circle(
    new H.geo.Point(41.4822, -81.6697), //center
    11703,
    {style: {fillColor: 'rgba(0, 255, 221, 0.66)'}}
  );
  var torontoCircle = new H.map.Circle(
    new H.geo.Point(43.7000, -79.4000), //center
    75090,
    {style: {fillColor: 'rgba(0, 255, 221, 0.66)'}}
  );
  var chicagoCircle = new H.map.Circle(
    new H.geo.Point(41.8369, -87.6847), //center
    81570,
    {style: {fillColor: 'rgba(0, 221, 255, 0.66)'}}
  );
  var newYorkCircle = new H.map.Circle(
    new H.geo.Point(40.7127, -74.0059), //center
    252180,
    {style: {fillColor: 'rgba(62, 95, 206, 0.66)'}}
  );
  clevelandCircle.setData({maxZoom: 7});
  torontoCircle.setData({maxZoom: 5});
  chicagoCircle.setData({maxZoom: 5});
  newYorkCircle.setData({maxZoom: 4});
  var container = new H.map.Group({
    objects: [clevelandCircle, torontoCircle, chicagoCircle, newYorkCircle]
  });
  container.addEventListener('tap', function (evt) {
    var target = evt.target;
    var maxZoom = target.getData().maxZoom;
    var cameraData = map.getCameraDataForBounds(target.getBounds());
    map.setZoom(Math.min(cameraData.zoom, maxZoom), true);
    map.setCenter(cameraData.position, true);
  });
  map.addObject(container);
}
var map = new H.Map(document.getElementById('map9'), defaultLayers.normal.map, {
  center: new H.geo.Point(41.4822, -81.6697),
  zoom: 4,
  pixelRatio: pixelRatio
});
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
setUpCustomZooming(map);

// map10
function restrictMap(map){
  var bounds = new H.geo.Rect(37.829, -122.426, 37.824, -122.42);
  map.getViewModel().addEventListener('sync', function() {
    var center = map.getCenter();
    if (!bounds.containsPoint(center)) {
      if (center.lat > bounds.getTop()) {
        center.lat = bounds.getTop();
      } else if (center.lat < bounds.getBottom()) {
        center.lat = bounds.getBottom();
      }
      if (center.lng < bounds.getLeft()) {
        center.lng = bounds.getLeft();
      } else if (center.lng > bounds.getRight()) {
        center.lng = bounds.getRight();
      }
      map.setCenter(center);
    }
  });
  map.addObject(new H.map.Rect(bounds, {
    style: {
        fillColor: 'rgba(55, 85, 170, 0.1)',
        strokeColor: 'rgba(55, 85, 170, 0.6)',
        lineWidth: 8
      }
    }
  ));
}
var map = new H.Map(document.getElementById('map10'),
  defaultLayers.normal.map,{
  center: {lat:37.82667, lng:-122.423333},
  zoom: 16,
  pixelRatio: pixelRatio
});
map.setBaseLayer(defaultLayers.satellite.map);
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
var ui = H.ui.UI.createDefault(map, defaultLayers, 'en-US');
restrictMap(map);

// map11
var PHI = 0.9005,
    omega = 4.1214,
    t = 0,
    tick = 0,
    x = 0,
    lastZoom = NaN;
function drawGroundTrack(x, t, zoom, radius, ctx, projection, screenCenter) {
  ctx.beginPath();
  for (var i = 1024; i >= 0; i--) {
    if (x <= 0) {
      x = projection.w;
      ctx.stroke();
      ctx.beginPath();
    }
    y = radius * Math.sin(omega * t + PHI);
    x -= Math.pow(2, zoom);
    pX = x - projection.x + screenCenter.x; 
    pY = y + (projection.w / 2) - projection.y + screenCenter.y;
    ctx.lineTo(pX, pY);
    t -= 0.007;
  }
  ctx.stroke();
}
function renderCallback(ctx, renderParams) {
  var zoom = renderParams.zoom,
    projection = renderParams.projection,
    screenCenter = renderParams.screenCenter,
    radius = Math.pow(2, (projection.exp + zoom)) / (2 * Math.PI),
    y,
    pX,
    pY;
  if (isNaN(lastZoom)) {
    lastZoom = zoom;
  }
  ctx.strokeStyle = 'yellow';
  if (zoom !== lastZoom) {
    x = tick * Math.pow(2, zoom);
  }
  x += Math.pow(2, zoom);
  y = radius * Math.sin(omega * t + PHI);
  pX = x - projection.x + screenCenter.x; 
  pY = y + (projection.w / 2) - projection.y + screenCenter.y;
  ctx.moveTo(pX - 10, pY - 10);
  ctx.lineTo(pX + 10, pY + 10);
  ctx.moveTo(pX + 10, pY - 10);
  ctx.lineTo(pX - 10, pY + 10);
  ctx.stroke();
  if (lastZoom === zoom) {
    drawGroundTrack(x, t, zoom, radius, ctx, projection, screenCenter);
  }
  lastZoom = zoom;
  tick += 1;
  t += 0.007;
  if (tick > 256) {
    tick = 0;
    x = 0;
  }
  return H.map.render.RenderState.ACTIVE;
}
function addCanvasOverlay(map, platform){
  var canvasLayer = new H.map.layer.CanvasLayer(renderCallback)
  map.addLayer(canvasLayer);
}
var map = new H.Map(document.getElementById('map11'),
  defaultLayers.satellite.map,{
  center: {lat: 0, lng: 0},
  zoom: 1,
  pixelRatio: pixelRatio
});
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
var ui = H.ui.UI.createDefault(map, defaultLayers);
ui.removeControl('mapsettings');
addCanvasOverlay(map, platform);

// map12
function addMarkersToMap(map) {
  var parisMarker = new H.map.Marker({lat:48.8567, lng:2.3508});
  map.addObject(parisMarker);

  var romeMarker = new H.map.Marker({lat:41.9, lng: 12.5});
  map.addObject(romeMarker);

  var berlinMarker = new H.map.Marker({lat:52.5166, lng:13.3833});
  map.addObject(berlinMarker);

  var madridMarker = new H.map.Marker({lat:40.4, lng: -3.6833});
  map.addObject(madridMarker);

  var londonMarker = new H.map.Marker({lat:51.5008, lng:-0.1224});
  map.addObject(londonMarker);
}
var map = new H.Map(document.getElementById('map12'),
  defaultLayers.normal.map,{
  center: {lat:50, lng:5},
  zoom: 4,
  pixelRatio: pixelRatio
});
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
var ui = H.ui.UI.createDefault(map, defaultLayers);
addMarkersToMap(map);

// map13
function addDraggableMarker(map, behavior){
  var marker = new H.map.Marker({lat:42.35805, lng:-71.0636});
  marker.draggable = true;
  map.addObject(marker);
  map.addEventListener('dragstart', function(ev) {
    var target = ev.target;
    if (target instanceof H.map.Marker) {
      behavior.disable();
    }
  }, false);
  map.addEventListener('dragend', function(ev) {
    var target = ev.target;
    if (target instanceof mapsjs.map.Marker) {
      behavior.enable();
    }
  }, false);
   map.addEventListener('drag', function(ev) {
    var target = ev.target,
        pointer = ev.currentPointer;
    if (target instanceof mapsjs.map.Marker) {
      target.setPosition(map.screenToGeo(pointer.viewportX, pointer.viewportY));
    }
  }, false);
}
var map = new H.Map(document.getElementById('map13'),
  defaultLayers.normal.map,{
  center: {lat:42.35805, lng:-71.0636},
  zoom: 12,
  pixelRatio: pixelRatio
});
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
var ui = H.ui.UI.createDefault(map, defaultLayers, 'en-US');
addDraggableMarker(map, behavior);


// map14
function addPolylineToMap(map) {
  var lineString = new H.geo.LineString();
  lineString.pushPoint({lat:53.3477, lng:-6.2597});
  lineString.pushPoint({lat:51.5008, lng:-0.1224});
  lineString.pushPoint({lat:48.8567, lng:2.3508});
  lineString.pushPoint({lat:52.5166, lng:13.3833});
  map.addObject(new H.map.Polyline(
    lineString, { style: { lineWidth: 4 }}
  ));
}
var map = new H.Map(document.getElementById('map14'),
  defaultLayers.normal.map,{
  center: {lat:52, lng:5},
  zoom: 5,
  pixelRatio: pixelRatio
});
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
var ui = H.ui.UI.createDefault(map, defaultLayers);
addPolylineToMap(map);

// map15
function addPolygonToMap(map) {
  var lineString = new H.geo.LineString(
    [52,13,100, 48, 2, 100, 48, 16, 100, 52, 13, 100],
    'values lat lng alt'
  );
  map.addObject(
    new H.map.Polygon(lineString, {
      style: {
        fillColor:'#FFFFCC',
        strokeColor:'#3e5fce',
        lineWidth: 8
      }
    })
  );
}
var map = new H.Map(document.getElementById('map15'),
  defaultLayers.normal.map,{
  center:{lat:52, lng:5},
  zoom:5,
  pixelRatio: pixelRatio
});
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
var ui = H.ui.UI.createDefault(map, defaultLayers);
addPolygonToMap(map);

// map16
function addCircleToMap(map){
  map.addObject(new H.map.Circle(
    {lat:28.6071, lng:77.2127},
    1000,
    {
      style: {
        strokeColor:'rgba(55, 85, 170, 0.6)', // Color of the perimeter
        lineWidth:2,
        fillColor:'rgba(97, 147, 65, 0.7)'  // Color of the circle
      }
    }
  ));
}
var map = new H.Map(document.getElementById('map16'),
  defaultLayers.normal.map,{
  center: {lat:28.6071, lng:77.2127},
  zoom: 13,
  pixelRatio: pixelRatio
});
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
var ui = H.ui.UI.createDefault(map, defaultLayers);
addCircleToMap(map);
