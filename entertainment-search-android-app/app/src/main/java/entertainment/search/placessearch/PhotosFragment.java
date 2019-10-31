package entertainment.search.placessearch;

import android.app.Activity;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;

import com.squareup.picasso.Picasso;



import java.util.ArrayList;

import db.Database;

public class PhotosFragment extends Fragment {

    private String placeID;
    private View v;

    public PhotosFragment() {
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        // Populate the dropdown list and inflate the layout fragment
        v = inflater.inflate(R.layout.photos_fragment, container, false);

        DetailsActivity activity = (DetailsActivity) getActivity();
        placeID = activity.getDetailsPlaceID();

        populatePhotosTab(placeID);
        new AsyncPhotoLoader(placeID, activity, this).execute("");

        return v;
    }

    public void populatePhotosTab(String placeIDLocal) {


        LinearLayout linearLayout = (LinearLayout) v.findViewById(R.id.photos_container);
        Database db = new Database(getActivity());

        ArrayList<String> photosArray = null;
        photosArray = db.getDetailsPhotos(placeIDLocal);

        if (photosArray != null) {
            linearLayout.removeAllViews();
            for (String url : photosArray) {


                ImageView image = new ImageView(getActivity());
                image.setPadding(0, 0, 0, 50);


                image.setAdjustViewBounds(true);
                Picasso.get().load(url).into(image);
                linearLayout.addView(image);

            }

        }
        else {

            new Table(getActivity(), null, v, null).showEmpty("photos");
        }
    }

    private class AsyncPhotoLoader extends AsyncTask<String, Void, String> {

        private String placeID;
        private Activity activity;
        private PhotosFragment fragment;
        public AsyncPhotoLoader(String placeID, Activity activity, PhotosFragment fragment) {

            this.placeID = placeID;
            this.activity = activity;
            this.fragment = fragment;
       }
        @Override
        protected String doInBackground(String... params) {

            //Wait for the photos to arrive
            ArrayList<String> photosArray = null;
            Database db = new Database(activity);
            photosArray = db.getDetailsPhotos(placeID);

            int tries = 0;
            while (photosArray == null ) {
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    Thread.interrupted();
                }
                photosArray = db.getDetailsPhotos(placeID);
                tries++;
                if (tries > 5) {break;} //assume the place has no pictures if 5 seconds is not enough
            }
            return "Executed";
        }

        @Override
        protected void onPostExecute(String result) {

            fragment.populatePhotosTab(placeID);
        }

        @Override
        protected void onPreExecute() {}

        @Override
        protected void onProgressUpdate(Void... values) {}
    }

}

