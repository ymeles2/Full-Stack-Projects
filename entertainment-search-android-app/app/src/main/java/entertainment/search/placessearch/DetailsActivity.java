package entertainment.search.placessearch;

import android.app.Activity;
import android.content.Intent;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.support.design.widget.TabLayout;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;
import android.support.v4.view.ViewPager;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.List;

import db.Database;


public class DetailsActivity extends AppCompatActivity {

    private String place_id;
    private String placeName;
    private String placeWebsite;
    private String placeAddress;
    private String response;
    private Toolbar toolbar;
    private TabLayout tabLayout;
    private ViewPager viewPager;
    private String entryPoint;
    private int[] tabIcons = {
            R.drawable.info_outline,
            R.drawable.photos,
            R.drawable.maps,
            R.drawable.review,
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_details);



        toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

//        // add a back button and a listener
//        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
//        getSupportActionBar().setDisplayShowHomeEnabled(true);
//        toolbar.setNavigationOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View v) {
//                startActivity(new Intent(getApplicationContext(), ResultsActivity.class));
//                finish();
//            }
//        });

        viewPager = findViewById(R.id.viewpager);
        setupViewPager(viewPager);

        tabLayout = findViewById(R.id.tabs);
        tabLayout.setupWithViewPager(viewPager);
        setupTabIcons();

        Intent intent = getIntent();
        response = intent.getStringExtra("response");
        place_id = intent.getStringExtra("placeID");
        entryPoint = intent.getStringExtra("entryPoint");

        // Save to the database only if the place has not already been downloaded
        String loadFromDB = intent.getStringExtra("loadFromDB");
        if (loadFromDB.equals("false")) {saveToDB(response);}

        Database db = new Database(this);
        placeName = db.getPlaceName(place_id, "name");
        placeAddress =  db.getPlaceName(place_id, "address");
        placeWebsite = db.getPlaceName(place_id, "website");

        setBackButton(toolbar, entryPoint);
        setPageTitle();
        setTwitterListener();
        setDetailsFavListener();

    }

    /*
    * Set main back button to point to the entry point.
    * */
    private void setBackButton(Toolbar toolbar, String entryPoint) {

        // add a back button and a listener

        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        getSupportActionBar().setDisplayShowHomeEnabled(true);

        if (entryPoint.equals("searchResults")) {

            toolbar.setNavigationOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    startActivity(new Intent(getApplicationContext(), ResultsActivity.class));
                    finish();
                }
            });
        }

        else if (entryPoint.equals("favorites")) {

            toolbar.setNavigationOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    startActivity(new Intent(getApplicationContext(), MainActivity.class));
                    finish();
                }
            });

        }

    }

    /*
    * Set twitter share button and fav icon click listener.
    * */
    private void setTwitterListener() {

        ImageView twitterLink = findViewById(R.id.details_twitter);
        twitterLink.setClickable(true);
        String url = getTwitterURL();
        twitterLink.setTag(url);
        twitterLink.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                openBrowser(v);
            }
        });
    }

    public void openBrowser(View v){

        //Get url from tag
        String url = (String)v.getTag();

        Intent intent = new Intent();
        intent.setAction(Intent.ACTION_VIEW);
        intent.addCategory(Intent.CATEGORY_BROWSABLE);

        //pass the url to intent data
        intent.setData(Uri.parse(url));

        startActivity(intent);
    }

    /*
    * Set details activity fav icon click listener. If the place is already in favorites,
    * highlight the icon.
    * */
    private void setDetailsFavListener() {

        final ImageView favIcon = findViewById(R.id.details_fav_icon);
        favIcon.setClickable(true);
        final Activity activity = this;

        // Call the fav button click handler twice to set the icon state of what it was in the
        // results/favorites page to be the same in the details page
        Table tableObj = new Table(activity, null, null, null);
        tableObj.resultsFavClickHandler(favIcon, place_id, "Details", false);
        tableObj.resultsFavClickHandler(favIcon, place_id, "Details", false);

        favIcon.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {


                Table tableObj = new Table(activity, null, null, null);
                tableObj.resultsFavClickHandler(favIcon, place_id, "Details", true);

            }
        });
    }



    public String getDetailsPlaceID() {

        return place_id;
    }

    private void saveToDB(String response) {

        Database db = new Database(this);
        db.saveDetailsToDB(response);

    }


    private void setPageTitle() {

        // Set the global toolbar title for all the fragments

        TextView textView = this.findViewById(R.id.action_bar_title);
        textView.setText(placeName);

        getSupportActionBar().setTitle("");

    }


    private void setupTabIcons() {

        TextView infoTab = (TextView) LayoutInflater.from(this).inflate(R.layout.info_tab, null);
        tabLayout.getTabAt(0).setCustomView(infoTab);

        TextView photosTab = (TextView) LayoutInflater.from(this).inflate(R.layout.photos_tab, null);
        tabLayout.getTabAt(1).setCustomView(photosTab);

        TextView mapTab = (TextView) LayoutInflater.from(this).inflate(R.layout.map_tab, null);
        tabLayout.getTabAt(2).setCustomView(mapTab);

        TextView reviewsTab = (TextView) LayoutInflater.from(this).inflate(R.layout.reviews_tab, null);
        tabLayout.getTabAt(3).setCustomView(reviewsTab);

        View root = tabLayout.getChildAt(0);
        if (root instanceof LinearLayout) {
            ((LinearLayout) root).setShowDividers(LinearLayout.SHOW_DIVIDER_MIDDLE);
            GradientDrawable drawable = new GradientDrawable();
            drawable.setColor(getResources().getColor(R.color.separator));
            drawable.setSize(1, 1);
            ((LinearLayout) root).setDividerPadding(10);
            ((LinearLayout) root).setDividerDrawable(drawable);
        }

    }

    private void setupViewPager(ViewPager viewPager) {
        ViewPagerAdapter adapter = new ViewPagerAdapter(getSupportFragmentManager());
        adapter.addFrag(new InfoFragment(), null);
        adapter.addFrag(new PhotosFragment(), null);
        adapter.addFrag(new MapFragment(), null);
        adapter.addFrag(new ReviewsFragment(), null);;
        viewPager.setAdapter(adapter);
    }

    private String getTwitterURL() {

        String url = "";
        String text = "Check out " + placeName + " located at "+ placeAddress + ". Website: ";
        text += placeWebsite + "  #TravelAndEntertainmentSearch";
        try {
            text = URLEncoder.encode(text, "UTF-8");
            url = "https://twitter.com/intent/tweet?text=" + text;
        }
        catch(Exception e){

            Log.e("error", e.toString());
        }
        return url;
    }

    class ViewPagerAdapter extends FragmentPagerAdapter {
        private final List<Fragment> mFragmentList = new ArrayList<>();
        private final List<String> mFragmentTitleList = new ArrayList<>();

        public ViewPagerAdapter(FragmentManager manager) {
            super(manager);
        }

        @Override
        public Fragment getItem(int position) {
            return mFragmentList.get(position);
        }

        @Override
        public int getCount() {
            return mFragmentList.size();
        }

        public void addFrag(Fragment fragment, String title) {
            mFragmentList.add(fragment);
            mFragmentTitleList.add(title);
        }

        @Override
        public CharSequence getPageTitle(int position) {
            return mFragmentTitleList.get(position);
        }
    }
}