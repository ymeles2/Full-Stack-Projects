package entertainment.search.placessearch;

import android.app.Activity;
import android.graphics.PorterDuff;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.LayerDrawable;
import android.text.Html;
import android.text.Spannable;
import android.text.SpannableString;
import android.text.TextPaint;
import android.text.method.LinkMovementMethod;
import android.text.style.URLSpan;
import android.text.util.Linkify;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.ViewTreeObserver;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RatingBar;
import android.widget.RelativeLayout;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;
import android.widget.Toast;

import com.squareup.picasso.Picasso;

import org.json.JSONArray;
import org.json.JSONObject;

import db.Database;

public class Table {

    private String response;
    private Activity activity;
    private View view;
    private TableLayout instanceTable;
    FavoritesFragment favInstance;


    public Table(Activity activity, String response, View view, FavoritesFragment favInstance) {

        this.activity = activity;
        this.response = response;
        this.view = view;
        this.favInstance = favInstance;
        this.instanceTable = null;

    }

    private TableRow getTableRow(String name, String vicinity, String iconURL, String placeID,
                                 String tableFor, String entryPoint) {

        //TODO: set listeners for both search resutls and favorites
        TableRow tr;

        tr = new TableRow(activity);
        tr.setPadding(50, 0, 0, 0);

        TextView placeName = new TextView(activity);
        ImageView favIcon = new ImageView(activity);
        ImageView catIcon = new ImageView(activity);


        // Category icon
        LinearLayout.LayoutParams iconLayout = new LinearLayout.LayoutParams(
                TableLayout.LayoutParams.WRAP_CONTENT,
                TableLayout.LayoutParams.WRAP_CONTENT);

        iconLayout.gravity = Gravity.LEFT;

        catIcon.setPadding(0, 3, 50, 3);
        catIcon.setLayoutParams(new TableRow.LayoutParams(1));
        catIcon.setLayoutParams(iconLayout);
        catIcon.setMinimumHeight(150);
        catIcon.setMinimumWidth(150);
        setIcon(catIcon, iconURL);
        catIcon.setScaleType(ImageView.ScaleType.FIT_XY);

        setResultsFav(favIcon, placeID, tableFor);

        // Place name
        setResultsPlaceName(placeName, name, vicinity, placeID, entryPoint);


        tr.addView(catIcon, new TableRow.LayoutParams(1));
        tr.addView(placeName, new TableRow.LayoutParams(2));
        tr.addView(favIcon, new TableRow.LayoutParams(3));
        tr.setPadding(0, 50, 20, 5);


        return tr;
    }

    private void setResultsPlaceName(TextView placeName, String name, String vicinity,
                                     final String placeID, final String entryPoint) {


        String nameNaddr = "<strong>" + name + "</strong>";
        nameNaddr += "<br>" + vicinity;
        placeName.setText(Html.fromHtml(nameNaddr));

        placeName.setMaxWidth(1000);
        placeName.setMinWidth(1000);
        placeName.setMinHeight(200);

        // Set a click listener. When clicked/touched, show a progress bar while fetching
        // the details page. When the results are ready, dismiss the progress bar and
        // load the details activity.
        placeName.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {

                SearchServices ss = new SearchServices(activity, view);
                ss.search(placeID, null, entryPoint);

            }
        });

    }

    private void setResultsFav(final ImageView favIcon, final String placeID, final String tableFor) {

        // Set the favorites icon based on whether the place is already in the favorites list

        int id = R.drawable.heart_outline_black;
        boolean isFavorited = false;

        final Database db = new Database(activity);
        if (db.checkState(placeID, "favorites")) {

            id = R.drawable.heart_fill_red;
            isFavorited = true;
        }

        favIcon.setPadding(50, 10, 50, 3);
        favIcon.setLayoutParams(new TableRow.LayoutParams(1));
        Drawable heart = activity.getResources().getDrawable(id);
        favIcon.setImageDrawable(heart);
        favIcon.setTag(isFavorited);

        // Set click listener
        favIcon.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {
                resultsFavClickHandler(favIcon, placeID, tableFor, true);

            }
        });

    }

    public void resultsFavClickHandler(final ImageView favIcon, final String placeID,
                                       String tableFor, boolean doShowToast) {

        // update the state of the favorites button. If favorited, change color to red. Otherwise,
        // change the color to plain

        Database db = new Database(activity);
        int id = R.drawable.heart_outline_black;
        if (tableFor.equals("Details")) {
            id = R.drawable.heart_outline_white;
        }
        boolean isFavorited = db.addToFav(placeID);

        String placeName = db.getPlaceName(placeID, "name");



        if (isFavorited) {

            id =  R.drawable.heart_fill_red;
            if (tableFor.equals("Details")) {
                id = R.drawable.heart_fill_white;
            }

            if (doShowToast) {showToast(placeName, false);};
        }
        else {
            if (doShowToast) {showToast(placeName, true);}
        }

        Drawable heart = activity.getResources().getDrawable(id);
        favIcon.setImageDrawable(heart);
        favIcon.setTag(isFavorited);

        // re-inflate the view if we're currently on the favorites page
        if (tableFor.equals("favorites")) {

            favInstance.populateFavorites(view, 1);

        }

    }

    private void showToast(String name, boolean removed) {

        String message = name + " was added to favorites";
        if (removed) {

            message = name + " was removed from favorites";
        }
        LayoutInflater inflater = activity.getLayoutInflater();
        View layout = inflater.inflate(R.layout.toast,
                (ViewGroup) activity.findViewById(R.id.custom_toast_container));


        TextView textView = layout.findViewById(R.id.toast);
        textView.setText(message);
        Toast toast = new Toast(activity);
        toast.setGravity(Gravity.BOTTOM, 0, 100);
        toast.setDuration(Toast.LENGTH_LONG);
        toast.setView(layout);
        toast.show();
    }

    private void setIcon(ImageView imageView, String url) {

        Picasso.get().load(url).resize(150, 150).into(imageView);
    }

    public int populateTable(String tableFor, int pageFromDB, int... optional) {

        TableLayout table = (TableLayout) activity.findViewById(R.id.main_table);

        if (table == null) {table = view.findViewById(R.id.main_table);}

        table.removeAllViews();
        table.setPadding(0,200, 0,50 );

        String name;
        String vicinity;
        String iconURL;
        String placeID;
        String entryPoint = "";
        JSONArray results = new JSONArray();

        try {


            if (tableFor.equals("results")) {

                if (pageFromDB > 0) {

                    Database db = new Database(activity);
                    results = db.getDBPage(pageFromDB, "results");

                }
                else {

                    JSONObject responseJSON = new JSONObject(response);
                    results = responseJSON.getJSONArray("results");
                }
                entryPoint = "searchResults";

            }
            else if (tableFor == "favorites") {

                Database db = new Database(activity);
                results = db.getDBPage(pageFromDB, "favorites");
                entryPoint = "favorites";
            }

            for (int i = 0; i < results.length(); i++) {

                JSONObject r = results.getJSONObject(i);
                name = r.getString("name");
                vicinity = r.getString("vicinity");
                iconURL = r.getString("icon");
                placeID = r.getString("place_id");


                if (pageFromDB < 0) { saveToDB(r, optional); }

                TableRow row = getTableRow(name, vicinity, iconURL, placeID, tableFor, entryPoint);
                table.addView(row);
            }
            if (results.length() == 0) {

                showEmpty("searchResults");
                return  0;
            }
            else {
                instanceTable = table;
            }

        }

        catch(Exception e){
            showEmpty("searchResults");
            Log.e("error", e.toString());
        }

        return results.length();
    }

    public TableLayout getTableObj() {

        return instanceTable;
    }

    private void saveToDB(JSONObject r, int...optional) {

        try {

            String name = r.optString("name");
            String vicinity = r.optString("vicinity");
            String iconURL = r.optString("icon");
            String place_id = r.optString("place_id");
            int favorited = 0;

            Database db = new Database(activity);

            db.addEntry(place_id, name, vicinity, favorited, iconURL, optional);
        }
        catch(Exception e){
            Log.e("error", e.toString());
        }


    }

    public TableLayout getDetailsInfoTable(TableLayout table, String placeID) {

        JSONObject results = null;
        Database db = new Database(activity);

        results = db.getDetailsInfo(placeID);

        String address, phoneNumber, priceLevel, googlePage, website, rating;

        try {

            table.removeAllViews();
            address = results.optString("formatted_address");
            phoneNumber = results.optString("formatted_phone_number");
            priceLevel = results.optString("price_level");
            rating = results.optString("rating");
            googlePage = results.optString("url");
            website = results.optString("website");

            int priceLevelInt = Integer.parseInt(priceLevel);
            int ratingInt = (int)Double.parseDouble(rating);

            /* Only add rows with values*/
            if (address != null || address != "") {

                table.addView(getDetailsRow(address, "Address", false, false));
            }
            if (phoneNumber != null || phoneNumber != "") {
                table.addView(getDetailsRow(phoneNumber, "Phone Number", false, true));
            }
            if (priceLevelInt > 0) {

                table.addView(getDetailsRow(priceLevel, "Price Level", false, false));
            }
            if (ratingInt > 0) {

                table.addView(getDetailsRow(rating, "Rating", false, false));
            }
            if (googlePage != null || googlePage != "") {

                table.addView(getDetailsRow(googlePage, "Google Page", true, false));
            }
            if (website != null || website != "") {

                table.addView(getDetailsRow(website, "Website", true, false));
            }
        }
        catch(Exception e){
            showEmpty("infoTab");
            Log.e("error", e.toString());
        }

        return table;

    }

    private void setRatingStars(RatingBar rating, float ratingF, int ratingI) {

        rating.setNumStars(5);

        if (ratingF > 0) {

            rating.setStepSize(0.1f);
            rating.setRating(ratingF);
        }
        else {

            rating.setStepSize(1);
            rating.setRating(ratingI);

        }
        rating.setScaleX(0.6f);
        rating.setScaleY(0.6f);

        // set the color of the stars
        LayerDrawable drawable = (LayerDrawable) rating.getProgressDrawable();
        drawable.getDrawable(2).setColorFilter((activity.getResources().getColor(R.color.webtech_pink)),
                PorterDuff.Mode.SRC_ATOP);
    }

    private TableRow getDetailsRow(String data, String rowFor, boolean isURL, boolean isPhone) {

        TableRow row = new TableRow(activity);
        TextView left = new TextView(activity);
        RatingBar rating = new RatingBar(activity);
        RelativeLayout relativeLayout = new RelativeLayout(activity);

        if (rowFor.equals("Price Level")) {

            data = getPriceLevel(data);
        }
        if (rowFor.equals("Rating")) {

            setRatingStars(rating, Float.parseFloat(data), -1);
            relativeLayout.addView(rating);
            relativeLayout.setPadding(-180, -50, 0, 0);

        }
        TextView right = new TextView(activity);

        String url = "";

        if (isURL) {

            url = "<a href=\"" + data + "\">" + data + "</a>";
            data = url;
        }

        String leftStr = "<strong>" + rowFor + "</strong>";


        left.setText(Html.fromHtml(leftStr));
        right.setText(Html.fromHtml(data));
        left.setPadding(0, 3, 50, 3);
        left.setTextSize(15);
        right.setMaxWidth(1000);
        right.setPadding(0,0, 50, 0);

        // make URLs clickable and phone numbers callable
        right.setMovementMethod(LinkMovementMethod.getInstance());
        right.setLinkTextColor(activity.getResources().getColor(R.color.webtech_pink));
        right.setTextSize(15);
        if (isPhone) {
            Linkify.addLinks(right, Linkify.PHONE_NUMBERS);
        }
        else if (isURL) {

            Linkify.addLinks(right, Linkify.WEB_URLS);
        }

        row.addView(left);
        if (rowFor.equals("Rating")) {

            row.addView(relativeLayout);
            row.setPadding(50, 10, 10, 0);
        }
        else {
            row.addView(right);
            row.setPadding(50, 10, 10, 50);
        }

        return row;
    }

    private String getPriceLevel(String data) {

        int count = Integer.parseInt(data);
        String dollarSigns = "";

        for (int i = 0; i < count; i++) { dollarSigns += "$"; }

        return dollarSigns;
    }

    public void populateReviews(TableLayout table, String placeID, String source, SortBy sortBy) {

        JSONArray reviews = new JSONArray();

        try {

                Database db = new Database(activity);
                reviews = db.getSortedReviews(placeID, source, sortBy);
                table.removeAllViews();

                for (int i = 0; i < reviews.length(); i++) {

                    JSONObject row = reviews.getJSONObject(i);

                    String author = row.getString("author");
                    String authorURL = row.getString("authorURL");
                    String avatar = row.getString("avatar");
                    String text = row.getString("text");
                    String date = row.getString("date");
                    Integer rating = row.getInt("rating");
                    text.replace('\n', ' ');
                    table.addView(getReviewRow(author, authorURL, avatar, text, date, rating));

                }
                if (reviews.length() == 0) {
                    showEmpty("reviews");
                }


            }
            catch(Exception e){
                showEmpty("reviews");
                Log.e("error", e.toString());
            }

    }


    private TableRow getReviewRow(String author, String authorURL, String avatar, String text,
                              String date, Integer rating) {

        TableRow mainRow = new TableRow(activity);
        TableLayout rightTable = new TableLayout(activity);
        TableLayout leftTable = new TableLayout(activity);
        TableRow authorRow = new TableRow(activity);
        TableRow ratingRow = new TableRow(activity);
        TableRow textRow = new TableRow(activity);
        TableRow dateRow = new TableRow(activity);
        TableRow imageRow = new TableRow(activity);
        RelativeLayout relativeLayout = new RelativeLayout(activity);

        TextView authorView = new TextView(activity);
        RatingBar ratingBar = new RatingBar(activity);
        TextView dateView = new TextView(activity);
        TextView textView = new TextView(activity);
        ImageView imageView = new ImageView(activity);



        setAuthorName(authorView, author, authorURL);

        setRatingStars(ratingBar, -1.0f, rating);
        relativeLayout.addView(ratingBar);
        relativeLayout.setPadding(-180, -50, 0, -50);

        setIcon(imageView, avatar);
        dateView.setText(date);
        textView.setText(text);
        textView.setMaxWidth(900);
        textView.setMinWidth(900);

        authorRow.addView(authorView);
        ratingRow.addView(relativeLayout);
        textRow.addView(textView);
        dateRow.addView(dateView);
        imageRow.addView(imageView);
        setImageListener(imageView, textView);

        rightTable.addView(authorRow, new TableRow.LayoutParams(1));
        rightTable.addView(ratingRow, new TableRow.LayoutParams(1));
        rightTable.addView(dateRow, new TableRow.LayoutParams(1));
        rightTable.addView(textRow, new TableRow.LayoutParams(1));
        rightTable.setPadding(0, 0, 200, 0);
        rightTable.setMinimumWidth(1000);

        leftTable.addView(imageRow);
        leftTable.setPadding(50, 0, -100, 0);


        mainRow.addView(leftTable, new TableRow.LayoutParams(1));
        mainRow.addView(rightTable, new TableRow.LayoutParams(2));

        mainRow.setPadding(50, 50, 50, 50);
        setReviewRowClickListener(mainRow, authorURL);
        return mainRow;

    }

    private void setReviewRowClickListener(TableRow row, String url) {


        row.setTag(url);
        row.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                DetailsActivity dActivity = (DetailsActivity) activity;
                dActivity.openBrowser(v);
            }
        });
    }

    public void showEmpty(String forTab) {

        String message = "";
        TableLayout table = new TableLayout(activity);
        LinearLayout layout = new LinearLayout(activity);
        boolean useLayout = false;


        if (forTab.equals("favorites")) {

            message = "No Favorites";
            table = view.findViewById(R.id.main_table);
        }
        else if (forTab.equals("searchResults")) {

            message = "No results";
            table = activity.findViewById(R.id.main_table);
        }
        else  if (forTab.equals("photos")) {
            message = "No Photos";
            layout = view.findViewById(R.id.photos_container);
            useLayout = true;
        }
        else if (forTab.equals("infoTab")) {

            message = "No info. API ERROR";
            table = view.findViewById(R.id.info_fragment_table);

        }
        else if (forTab.equals("reviews")) {

            message = "No reviews";
            table = view.findViewById(R.id.reviews_table);

        }


        table.removeAllViews();
        TextView textView = new TextView(activity);
        textView.setText(message);

        textView.setPadding(500, 1100, 0,0);
        if (useLayout) {layout.addView(textView);}
        else {  table.addView(textView); }

    }



    private void setAuthorName(TextView authorView, String author, String authorURL) {

        String authHTML = "<a href=\"" + authorURL + "\">" + author + "</a>";
        authorView.setText(Html.fromHtml(authHTML));
        Linkify.addLinks(authorView, Linkify.WEB_URLS);
        authorView.setMovementMethod(LinkMovementMethod.getInstance());
        authorView.setLinkTextColor(activity.getResources().getColor(R.color.colorPrimary));
        stripUnderlines(authorView);

        authorView.setTextSize(16);
        authorView.setPadding(0, 50, 50, 10);
    }


    private void stripUnderlines(TextView textView) {

        Spannable s = new SpannableString(textView.getText());
        URLSpan[] spans = s.getSpans(0, s.length(), URLSpan.class);
        for (URLSpan span: spans) {
            int start = s.getSpanStart(span);
            int end = s.getSpanEnd(span);
            s.removeSpan(span);
            span = new URLSpanNoUnderline(span.getURL());
            s.setSpan(span, start, end, 0);
        }
        textView.setText(s);
    }

    public void setImageListener(final ImageView imageView, final TextView textView) {

        // Dynamically set imageView top padding.

        imageView.getViewTreeObserver().addOnGlobalLayoutListener
                (new ViewTreeObserver.OnGlobalLayoutListener() {
            @Override
            public void onGlobalLayout() {

                int topPadding = 100;

                imageView.getViewTreeObserver();
                int textHeight = textView.getHeight();

                double scalar = 1.5;

                if (textHeight > 0 && textHeight > topPadding) {

                    topPadding = (int)((double)textHeight/scalar);

                }

                imageView.setPadding(50, topPadding, 50, 50);
            }
        });

    }

    private class URLSpanNoUnderline extends URLSpan {
        public URLSpanNoUnderline(String url) {
            super(url);
        }
        @Override public void updateDrawState(TextPaint ds) {
            super.updateDrawState(ds);
            ds.setUnderlineText(false);
        }
    }
}

