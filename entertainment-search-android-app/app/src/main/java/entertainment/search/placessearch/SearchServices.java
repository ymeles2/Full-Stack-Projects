package entertainment.search.placessearch;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Intent;
import android.util.Log;
import android.view.View;
import com.android.volley.DefaultRetryPolicy;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONObject;


import db.Database;

public class SearchServices {

    private ProgressDialog progressBar;
    private Activity activity;
    private View view;

    public SearchServices(Activity activity, View view) {

            this.activity = activity;
            this.view = view;
    }


    private String getGETParams(JSONObject formData) {

        String queryString = "?";

        try {

            queryString += "keyword=" + formData.getString("keyword");
            queryString += "&distance=" + formData.getString("distance");
            queryString += "&customLoc=" + formData.getString("customLoc");
            queryString += "&category=" + formData.getString("category");
            queryString += "&centerLat=" + formData.getString("centerLat");
            queryString += "&centerLon=" + formData.getString("centerLon");
            queryString += "&requestType=" + "nearbyPlaces";

        }
        catch(Exception e){
            Log.e("error", e.toString());
        }

        return queryString;
    }

    /*
    * Make results and details search requests. For details, decouple yelp review request by
    * indicating as such in the querystring. Otherwise, calls to Yelp in the backend would
    * be too slow. Since we don't need the reviews right away, we'll just save them to the
    * database with a callback when they arrive.
    * */
    public void search(final String placeID, final JSONObject formData, String entryPoint) {

        String url = "";
        String yelpURL = null;
        String photosURL = null;
        boolean loadFromDB = false;

        if (placeID != null) {
            url = "http://bizyb2.us-east-2.elasticbeanstalk.com/places-details-endpoint";
            url += "?placeID=" + placeID;
            yelpURL = url + "&requestForYelp=true";
            photosURL = url + "&requestForPhotos=true";
            loadFromDB = new Database(activity).detailsInDB(placeID);
        }
        else {

            String queryString = getGETParams(formData);
            url = "http://bizyb2.us-east-2.elasticbeanstalk.com/search-endpoint" + queryString;
        }

        if (loadFromDB) {

            Intent intent =  new Intent(activity, DetailsActivity.class);
            intent.putExtra("placeID", placeID);
            intent.putExtra("loadFromDB", "true");
            intent.putExtra("response", "");
            intent.putExtra("entryPoint", entryPoint);
            activity.startActivity(intent);
        }
        else {
            requestHelper(url, placeID, false, false, entryPoint);
            if (yelpURL != null) { requestHelper(yelpURL, placeID, true, false, entryPoint);}
            if (photosURL != null) { requestHelper(photosURL, placeID, false, true, entryPoint);}

        }
    }

    private void requestHelper(final String url, final String placeID, final  boolean getYelpReviews,
                               final boolean getPhotos, final String entryPoint) {

        RequestQueue queue = Volley.newRequestQueue(activity);

        JsonObjectRequest getRequest = new JsonObjectRequest(
                Request.Method.GET, url, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        // display response
                        Intent intent = new Intent(activity, ResultsActivity.class);
                        Log.d("Response", response.toString());

                        if (placeID == null) {

                            intent.putExtra("resultType", "SEARCH_RESULTS");

                        } else {


                            intent = new Intent(activity, DetailsActivity.class);
                            intent.putExtra("placeID", placeID);
                            intent.putExtra("loadFromDB", "false");
                            intent.putExtra("entryPoint", entryPoint);
                        }
                        intent.putExtra("response", response.toString());
                        if (getYelpReviews) {

                            new Database(activity).saveYelpReviews(response.toString());
                        }
                        else if (getPhotos) {

                            new Database(activity).savePhotos(response.toString(), placeID);
                        }
                        else {
                            progressBar.dismiss();
                            activity.startActivity(intent);
                        }

                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Log.e("Error.Response", error.toString());
                        progressBar.dismiss();
                    }
                }
        );
        getRequest.setRetryPolicy(new DefaultRetryPolicy(
                10000,
                DefaultRetryPolicy.DEFAULT_MAX_RETRIES,
                DefaultRetryPolicy.DEFAULT_BACKOFF_MULT));

        // add it to the RequestQueue
        queue.add(getRequest);
        if (!getYelpReviews && !getPhotos) { showProgressBar(placeID);}
    }


    public void showProgressBar(String placeID) {

        String msg = activity.getResources().getString(R.string.fetching_results);
        if (placeID != null) {msg = "Fetching details";}

        progressBar = new ProgressDialog(activity, R.style.FetchingResultsStyle);
        progressBar.setCancelable(true);
        progressBar.setMessage(msg);
        progressBar.setProgressStyle(ProgressDialog.STYLE_SPINNER);
        progressBar.show();

        new Thread(new Runnable() {

            public void run() {

            }
        }).start();
    }
}
