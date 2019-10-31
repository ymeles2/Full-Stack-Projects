<?php

$request_type = $_GET["requestType"];
if ($request_type == "placeDetails") get_place_details();
else if ($request_type == "nearbyPlaces")  get_nearby_places();

function get_api_key($key_type) {

   $places_key = "AIzaSyCNb7xTlRWC9mg0Nqam1HzgP5ACRIZe1Pg";
   $geo_key =  "AIzaSyCDa9Xi3TfpA7DyIXZ_9fX5p_KNlHM1tro";

   return $key_type == "geo" ? $geo_key : $places_key;
}

function get_photos($response) {
   // Download top five photos, save them to disk with a unique name, and populate 
   // the image array with their names to be passed to the client

   $imageArry = array();
   if (isset(json_decode($response)->result->photos)) {

      $photo_ref = json_decode($response)->result->photos[0]->photo_reference;
      $base_url = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&";
      
      $THRESHOLD = 4;

      $i = 0;
      foreach(json_decode($response)->result->photos as $photo) {

            $photo_ref = $photo->photo_reference;
            $url = $base_url . "photoreference=" . $photo_ref . "&key=" .get_api_key("places");
            $file_name = "images/" . uniqid() . ".jpg"; // saving them as jpeg
            file_put_contents($file_name, file_get_contents($url));
            $imageArry[$i] = $file_name;

            if ($i == $THRESHOLD) break;
            $i = $i+1;
      }
   }

   return $imageArry;

}

function get_place_details() {

   $base_url = "https://maps.googleapis.com/maps/api/place/details/json?"; 
   $place_id = $_GET["place_id"];
   $api_key = get_api_key("places");

   $url = $base_url . "placeid=" . $place_id . "&key=" . $api_key;
   $response = file_get_contents($url);
   
   $newJson = new stdClass();
   $newJson->photos = get_photos($response);

   if (isset(json_decode($response)->result->reviews)) {
      $newJson->reviews = json_decode($response)->result->reviews;
   }
   else {
      $newJson->reviews = null;
   }
   
   $newJson->name = json_decode($response)->result->name;
   $jsonObj = json_encode($newJson);
   echo $jsonObj;

}

function get_nearby_places() {

   $base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"; 

   $keyword = str_replace(" ", "+", $_GET["keyword"]);
   $category = str_replace(" ", "+", $_GET["category"]);
   $distance = str_replace(" ", "+", $_GET["distance"]); 
   $location = isset($_GET["location"]) ? str_replace(" ", "+", $_GET["location"]): "";
   $lat = isset($_GET["lat"]) ? $_GET["lat"] : -1;
   $lon = isset($_GET["lon"]) ? $_GET["lon"] : -1;

   // Get latitude/logitude if only $location is given
   if ($lat == -1) {

      $jsonObj = json_decode(get_lon_lat($location));
      
      $lat = $jsonObj->results[0]->geometry->location->lat;
      $lon = $jsonObj->results[0]->geometry->location->lng;
   }

   $url = $base_url . "location=" . $lat . "," . $lon . "&radius=" . $distance . "&type=" . $category;
   $url = $url . "&keyword=" . $keyword . "&key=" . get_api_key("places");
   $response =  file_get_contents($url);

   // Set location center point
   $newJson = new stdClass();
   $newJson->lat = $lat;
   $newJson->lon = $lon;
   $newJson->data = json_decode($response);
   $jsonObj = json_encode($newJson);
   echo $jsonObj;
   
}

function get_lon_lat($location) {

   $base_url = "https://maps.googleapis.com/maps/api/geocode/json?address=";
   $base_url = $base_url . $location . "&key="  . get_api_key("geo");

   $response = file_get_contents($base_url);

   return $response;

}
?>



