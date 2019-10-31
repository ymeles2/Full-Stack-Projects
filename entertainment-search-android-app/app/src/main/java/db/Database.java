package db;



import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Arrays;

import entertainment.search.placessearch.SortBy;


public class Database  extends SQLiteOpenHelper{


    private static final int DATABASE_VERSION = 2;

    private static final String DATABASE_NAME = "PlacesSearch.db";

    private static final String TABLE_NEARBY_PLACES = "nearby_places";
    private static final String TABLE_REVIEWS = "reviews";

    private static final String COLUMN_PRIMARY_KEY = "id";
    private static final String COLUMN_PLACE_ID = "place_id";
    private static final String COLUMN_NAME = "name";
    private static final String COLUMN_VICINITY = "vicinity";
    private static final String COLUMN_CATEGORY_ICON = "category_icon";
    private static final String COLUMN_FAVORITED = "favorited";
    private static final String COLUMN_PAGE_NUM = "page_num";
    private static final String COLUMN_INSERTION_ORDER = "insertion_order";
    private static final String COLUMN_FAV_INSERTION_ORDER = "fav_insertion_order";
    private static final String COLUMN_DETAILS_AVAILABLE = "details_available";

    //Applicable to Details
    private static final String COLUMN_PHONE_NUMBER = "phone_number";
    private static final String COLUMN_PRICE_LEVEL = "price_level";
    private static final String COLUMN_RATING = "rating";
    private static final String COLUMN_GOOGLE_PAGE = "google_page";
    private static final String COLUMN_WEBSITE = "website";
    private static final String COLUMN_PHOTOS = "photos";



    // Applicable to Reviews and Details
    private static final String COLUMN_FOREIGN_KEY = TABLE_NEARBY_PLACES + "_id";
    private static final String COLUMN_AUTHOR_NAME = "author_name";
    private static final String COLUMN_AUTHOR_URL = "author_url";
    private static final String COLUMN_LANGUAGE = "language";
    private static final String COLUMN_AVATAR = "profile_photo_url";
    //private static final String COLUMN_RATING = "rating";
    private static final String COLUMN_RELATIVE_TIME = "relative_time";
    private static final String COLUMN_TEXT = "text";
    private static final String COLUMN_EPOCH_TIME = "EPOCH_time";
    private static final String COLUMN_FORMATTED_TIME = "formatted_time";
    private static final String COLUMN_REVIEW_SOURCE = "review_source";
    private static final String COLUMN_DEFAULT_INDEX = "default_index";
    private static final String COLUMN_LATITUDE = "latitude";
    private static final String COLUMN_LONGITUDE = "longitude";

//    private static final String COLUMN_DETAILS_PLACE = "details_place";


    private String CREATE_TABLE = "CREATE TABLE " + TABLE_NEARBY_PLACES + "("
                            + COLUMN_PRIMARY_KEY + " INTEGER PRIMARY KEY AUTOINCREMENT,"
                            + COLUMN_PLACE_ID + " TEXT,"
                            + COLUMN_NAME + " TEXT,"
                            + COLUMN_CATEGORY_ICON + " TEXT,"
                            + COLUMN_FAVORITED + " INTEGER,"
                            + COLUMN_PAGE_NUM + " INTEGER,"
                            + COLUMN_PHONE_NUMBER + " TEXT,"
                            + COLUMN_PRICE_LEVEL + " INTEGER,"
                            + COLUMN_INSERTION_ORDER + " INTEGER,"
                            + COLUMN_FAV_INSERTION_ORDER + " INTEGER,"
                            + COLUMN_RATING + " REAL,"
                            + COLUMN_PHOTOS + " TEXT,"
                            + COLUMN_LATITUDE + " REAL,"
                            + COLUMN_LONGITUDE + " REAL,"
                            + COLUMN_GOOGLE_PAGE + " TEXT,"
                            + COLUMN_WEBSITE + " TEXT,"
                            + COLUMN_DETAILS_AVAILABLE + " INTEGER,"
                            + COLUMN_VICINITY + " TEXT" + ")";

    private String CREATE_REVIEWS_TABLE = "CREATE TABLE " + TABLE_REVIEWS + "("
            + COLUMN_PRIMARY_KEY + " INTEGER PRIMARY KEY AUTOINCREMENT,"
            + COLUMN_FOREIGN_KEY + " INTEGER,"
            + COLUMN_AUTHOR_NAME + " TEXT,"
            + COLUMN_AUTHOR_URL + " TEXT,"
            + COLUMN_LANGUAGE + " TEXT,"
            + COLUMN_AVATAR + " TEXT,"
            + COLUMN_RATING + " INTEGER,"
            + COLUMN_RELATIVE_TIME + " TEXT,"
            + COLUMN_TEXT + " TEXT,"
            + COLUMN_EPOCH_TIME + " INTEGER,"
            + COLUMN_FORMATTED_TIME + " TEXT,"
            + COLUMN_REVIEW_SOURCE + " TEXT,"
            + COLUMN_DEFAULT_INDEX + " INTEGER,"
            + COLUMN_PLACE_ID + " TEXT" + ")";



    private String DROP_TABLE = "DROP TABLE IF EXISTS " + TABLE_NEARBY_PLACES;
    private String DROP_TABLE_REVIEWS = "DROP TABLE IF EXISTS " + TABLE_REVIEWS;

    private Context context;
    private String delim;
    private String placeName;
    private String placeID;


    public Database(Context context){
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
        this.context = context;
        this.delim = "::::::::";
        this.placeName = "?";
        this.placeID = "?";
    }

    @Override
    public void onCreate(SQLiteDatabase db){

        db.execSQL(CREATE_TABLE);
        db.execSQL(CREATE_REVIEWS_TABLE);

        Log.d("db", CREATE_TABLE);

    }

    @Override
    public  void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion){
        db.execSQL(DROP_TABLE);
        db.execSQL(DROP_TABLE_REVIEWS);
        onCreate(db);

    }

    public void dropRows(String dropFor, String placeID, String reviewSource) {

        // remove all existing entries from the db except for the ones that have been
        // favorited
        // TODO: does this do cascade deletion?

        SQLiteDatabase db = this.getWritableDatabase();
        if (dropFor.equals("favorites")) {

            String whereClause = COLUMN_FAVORITED + "=?";
            db.delete(TABLE_NEARBY_PLACES, whereClause, new String[]{"0"});
        }

        else if (dropFor.equals("reviews")) {

            String whereClause = COLUMN_PLACE_ID + "=? AND " + COLUMN_REVIEW_SOURCE + "=?";
            db.delete(TABLE_REVIEWS, whereClause, new String[]{placeID, reviewSource});

        }


    }

    /* Return a row cursor
    *
    * */
    private CursorContainer getCursor(String placeID, String cursorFor) {

        SQLiteDatabase db = this.getReadableDatabase();
        String selection = COLUMN_PLACE_ID + "=?";
        String[] selectionArgs = {placeID};

        String col = COLUMN_PRIMARY_KEY;

        if (cursorFor.equals("favorites")) {
            col = COLUMN_FAVORITED;
        }
        else if (cursorFor.equals(("insertionOrder"))) {

            col = COLUMN_INSERTION_ORDER;
        }
        else if (cursorFor.equals("name")) {

            col = COLUMN_NAME;
        }
        else if (cursorFor.equals("photos")) {

            col = COLUMN_PHOTOS;
        }
        else if (cursorFor.equals("address")) {

            col = COLUMN_VICINITY;
        }
        else if (cursorFor.equals("website")) {

            col = COLUMN_WEBSITE;
        }
        else if (cursorFor.equals("latitude")) {

            col = COLUMN_LATITUDE;
        }
        else if (cursorFor.equals("longitude")) {

            col = COLUMN_LONGITUDE;
        }
        String[] columns = {
                col
        };

        Cursor cursor = db.query(TABLE_NEARBY_PLACES,
                columns,
                selection,
                selectionArgs,
                null,
                null,
                null);

        CursorContainer container = new CursorContainer(db, cursor);

        return container;

    }



    private void  saveReviewsToDB(JSONArray reviews, String placeID, String reviewsFrom) {


        // drop existing reviews for this place and reviewSource
        dropRows("reviews", placeID, reviewsFrom);

        SQLiteDatabase db = this.getWritableDatabase();
        try {

            for (int i = 0; i < reviews.length(); i++) {

                JSONArray row = reviews.getJSONArray(i);

                String authorName = row.getString(0);
                String authorURL = row.getString(1);
                String language = row.getString(2);
                String avatar = row.getString(3);
                int rating = row.getInt(4);
                String relativeTime = row.getString(5);
                String text = row.getString(6);
                int epoch = row.getInt(7);
                String formattedTime = row.getString(8);
                int defaultIndex = row.getInt(10);


                ContentValues values = new ContentValues();
                values.put(COLUMN_AUTHOR_NAME, authorName);
                values.put(COLUMN_AUTHOR_URL, authorURL);
                values.put(COLUMN_LANGUAGE, language);
                values.put(COLUMN_AVATAR, avatar);
                values.put(COLUMN_RATING, rating);
                values.put(COLUMN_RELATIVE_TIME, relativeTime);
                values.put(COLUMN_TEXT, text);
                values.put(COLUMN_EPOCH_TIME, epoch);
                values.put(COLUMN_FORMATTED_TIME, formattedTime);
                values.put(COLUMN_REVIEW_SOURCE, reviewsFrom);
                values.put(COLUMN_DEFAULT_INDEX, defaultIndex);
                values.put(COLUMN_PLACE_ID, placeID);

                db.insert(TABLE_REVIEWS, null, values);


            }

        }
        catch(Exception e){
            // TODO: output no results/failed to get results error here
            Log.e("error", e.toString());
        }

        finally {
            db.close();
        }


    }

    public void saveYelpReviews(String response) {

        JSONObject result = new JSONObject();
        try {

            JSONObject responseJSON = new JSONObject(response);
            result = responseJSON.getJSONObject("result");
            String  place_id = result.optString("place_id");
            String yelpKey = "yelp_reviews_" + place_id;
            JSONArray yelpReviews = responseJSON.getJSONArray(yelpKey);
            saveReviewsToDB(yelpReviews, place_id, "Yelp");
        }

        catch(Exception e){
            Log.e("error", e.toString());
        }

    }

    public void savePhotos(String response, String placeID) {

        JSONObject result = new JSONObject();
        SQLiteDatabase db = this.getWritableDatabase();
        try {

            JSONArray photosArray;
            String photosStr;

            JSONObject responseJSON = new JSONObject(response);
            photosArray = responseJSON.getJSONArray("photosArray");
            photosStr = mergePhotoURLs(photosArray);

            ContentValues values = new ContentValues();
            values.put(COLUMN_PHOTOS, photosStr);

            db.update(TABLE_NEARBY_PLACES, values, COLUMN_PLACE_ID + "= ?",
                    new String[] {placeID});

        }

        catch(Exception e){

            Log.e("error", e.toString());
        }
        finally {
            db.close();
        }

    }


    /*
    * Save details info to the database. Note: this routine is executed during the transition from
    * ResultsActivity to DetailsActivity. The information for details is incomplete at this stage.
    * Later, we populate the missing yelp reviews asynchronously.
    *
    * PRE: place already exists in the database
    * */
    public void saveDetailsToDB(String response) {

        double latitude;
        double longitude;
        double rating;
        int price_level;
        String formatted_address;
        String formatted_phone_number;
        String name;
        String google_page;
        String website;
        JSONArray googleReviews;
        String place_id;

        JSONObject result = new JSONObject();
        SQLiteDatabase db = this.getWritableDatabase();
        try {

            JSONObject responseJSON = new JSONObject(response);
            result = responseJSON.getJSONObject("result");


            // todo: centerlat and centerLon refer to the search origin, not the place lat/lng
            latitude = responseJSON.optDouble("centerLat");
            longitude = responseJSON.optDouble("centerLon");
            rating = result.optDouble("rating");
            price_level = result.optInt("price_level", -1);
            formatted_address = result.optString("formatted_address");
            formatted_phone_number = result.optString("formatted_phone_number");
            name = result.optString("name");
            google_page = result.optString("url");
            place_id = result.optString("place_id");
            website = result.optString("website");

            String googleKey = "google_reviews_" + place_id;
            googleReviews = responseJSON.getJSONArray(googleKey);

            ContentValues values = new ContentValues();

            this.placeName = name;
            this.placeID = place_id;

            values.put(COLUMN_LATITUDE, latitude);
            values.put(COLUMN_LONGITUDE, longitude);
            values.put(COLUMN_RATING, rating);
            values.put(COLUMN_PRICE_LEVEL, price_level);
            values.put(COLUMN_VICINITY, formatted_address);
            values.put(COLUMN_PHONE_NUMBER, formatted_phone_number);
            values.put(COLUMN_NAME, name);
            values.put(COLUMN_GOOGLE_PAGE, google_page);
            values.put(COLUMN_WEBSITE, website);
            values.put(COLUMN_DETAILS_AVAILABLE, 1);

            db.update(TABLE_NEARBY_PLACES, values, COLUMN_PLACE_ID + "= ?",
                    new String[] {place_id});

            saveReviewsToDB(googleReviews, place_id, "Google");

    }
     catch(Exception e){
        // TODO: output no results/failed to get results error here
        Log.e("error", e.toString());
    }

    finally {
            db.close();
        }

    }

    /*
    * Merge all photo URLs into a single string with a common delimiter.
    * */
    private String mergePhotoURLs(JSONArray photosArray) {

        String photos = "";

        try {

            for (int i = 0; i < photosArray.length(); i++) {

                if (i == photosArray.length() - 1) {

                    photos += photosArray.getString(i);
                }
                else {
                    photos += photosArray.getString(i) + delim;
                }

            }

        }
        catch(Exception e){
            // TODO: output no results/failed to get results error here
            Log.e("error", e.toString());
        }

        return photos;
    }


    /*
    *  If placeID is already favorited, set it to false and return false.
    *  Otherwise, the place is being favorited for the first time so set the
    *  field to true and return true. Display a toast to indicate the addition or removal of the
    *  place from the list.
    *
    * */

    public boolean addToFav(String placeID) {

        boolean isFavorited = false;
        int state;
        int favInsertionOrder = getCount("favorites");


        CursorContainer container = getCursor(placeID, "favorites");
        SQLiteDatabase db = container.db();
        Cursor cursor = container.cursor();

        ContentValues values = new ContentValues();
        try {

            while(cursor.moveToNext()) {

                int index = cursor.getColumnIndex(COLUMN_FAVORITED);
                state = cursor.getInt(index);

                if (state == 0) {

                    favInsertionOrder++;
                    values.put(COLUMN_FAVORITED, 1);
                    values.put(COLUMN_FAV_INSERTION_ORDER, favInsertionOrder);
                    isFavorited = true;
                }
                else {
                    values.put(COLUMN_FAVORITED, 0);
                }
                db.update(TABLE_NEARBY_PLACES, values, COLUMN_PLACE_ID + "= ?",
                        new String[] {placeID});
            }

        }
        finally {
            cursor.close();
            db.close();
        }

        return isFavorited;

    }

    public boolean checkState(String placeID, String checkFor) {

        boolean state = false;
        CursorContainer container = getCursor(placeID, checkFor);
        SQLiteDatabase db = container.db();
        Cursor cursor = container.cursor();

        try {
            if (checkFor.equals("rowExistence")) {

                int cursorCount = cursor.getCount();
                if (cursorCount > 0) {
                    state = true;
                }
            } else if (checkFor.equals("favorites")) {


                while (cursor.moveToNext()) {

                    state = cursor.getInt(cursor.getColumnIndex(COLUMN_FAVORITED)) == 1;

                }
            }
        }
        finally {
            cursor.close();
            db.close();
        }

        return state;

    }

    public void addEntry(String place_id, String name, String vicinity,
                         int favorited, String category_icon, int...optional) {

        int insertionOrder = getCount();
        int pageNum = getPageNum();
        boolean rowExists = checkState(place_id, "rowExistence");
        if (optional.length > 0) {
            insertionOrder -= optional[0]; // offset
        }

        SQLiteDatabase db = this.getWritableDatabase();
        if (!rowExists) {



            ContentValues values = new ContentValues();
            values.put(COLUMN_PLACE_ID, place_id);
            values.put(COLUMN_NAME, name);
            values.put(COLUMN_FAVORITED, favorited); // initially they're all set to false
            values.put(COLUMN_PAGE_NUM, pageNum);
            values.put(COLUMN_CATEGORY_ICON, category_icon);
            values.put(COLUMN_VICINITY, vicinity);
            values.put(COLUMN_INSERTION_ORDER, insertionOrder);
            values.put(COLUMN_DETAILS_AVAILABLE, 0);
            db.insert(TABLE_NEARBY_PLACES, null, values);



        }
        else {
            // the row exists so update its insertion order
            ContentValues values = new ContentValues();

                values.put(COLUMN_INSERTION_ORDER, insertionOrder);
                db.update(TABLE_NEARBY_PLACES, values, COLUMN_PLACE_ID + "= ?",
                        new String[] {place_id});


        }
        db.close();
    }



    public JSONArray getDBPage(int pageNum, String pageFor) {

        JSONArray results = new JSONArray();

        String query = "SELECT  * FROM " + TABLE_NEARBY_PLACES + " ORDER BY " + COLUMN_INSERTION_ORDER;
        if (pageFor.equals("favorites")) {

            query = "SELECT  * FROM " + TABLE_NEARBY_PLACES + " WHERE " + COLUMN_FAVORITED + " =1" + " ORDER BY " + COLUMN_FAV_INSERTION_ORDER;

        }

        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = db.rawQuery(query, null);
        final int PAGE_SIZE = 20;
        int i = 0;
        int start = (pageNum - 1) * PAGE_SIZE;
        int end = pageNum * PAGE_SIZE;




        try {
            while (cursor.moveToNext()) {
               if (i >= start) {

                    //TODO: are these sorted by the primary key or are we just assuming?

                    JSONObject row = new JSONObject();


                    String name = cursor.getString(cursor.getColumnIndex(COLUMN_NAME));
                    String vicinity = cursor.getString(cursor.getColumnIndex(COLUMN_VICINITY));
                    String iconURL = cursor.getString(cursor.getColumnIndex(COLUMN_CATEGORY_ICON));
                    String place_id = cursor.getString(cursor.getColumnIndex(COLUMN_PLACE_ID));

                    try {
                        row.put("name", name);
                        row.put("vicinity", vicinity);
                        row.put("icon", iconURL);
                        row.put("place_id", place_id);
                        results.put(row);
                    }
                    catch(Exception e){
                        // TODO: output no results/failed to get results error here
                        Log.e("error", e.toString());
                    }
               }
               if (i >= end) {break;}
                i++;
            }
        }
        finally {
            cursor.close();
            db.close();
        }



        return results;
    }

    private String getSortingColumn(SortBy sortBy) {

        String column = COLUMN_DEFAULT_INDEX;

        switch(sortBy) {

            case HIGHEST_RATING:
                column = "-" + COLUMN_RATING;
                break;
            case LOWEST_RATING:
                column = COLUMN_RATING;
                break;
            case MOST_RECENT:
                column = "-" + COLUMN_EPOCH_TIME;
                break;
            case LEAST_RECENT:
                column = COLUMN_EPOCH_TIME;
                break;
            default:
                column = COLUMN_DEFAULT_INDEX;
                break;
        }

        return column;
    }

    public JSONArray getSortedReviews(String placeID, String reviewsFrom, SortBy sortBy) {


        JSONArray reviews = new JSONArray();

        String query = "SELECT  * FROM " + TABLE_REVIEWS + " WHERE " + COLUMN_PLACE_ID + "=? AND " + COLUMN_REVIEW_SOURCE + "=?";
        query += " ORDER BY " + getSortingColumn(sortBy);

        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = db.rawQuery(query, new String[] {placeID, reviewsFrom});

        try {


            while (cursor.moveToNext()) {

                JSONObject row = new JSONObject();
                String author = cursor.getString(cursor.getColumnIndex(COLUMN_AUTHOR_NAME));
                String authorURL = cursor.getString(cursor.getColumnIndex(COLUMN_AUTHOR_URL));
                String avatar = cursor.getString(cursor.getColumnIndex(COLUMN_AVATAR));
                String text = cursor.getString(cursor.getColumnIndex(COLUMN_TEXT));
                String date = cursor.getString(cursor.getColumnIndex(COLUMN_FORMATTED_TIME));
                Integer rating = cursor.getInt(cursor.getColumnIndex(COLUMN_RATING));

                row.put("author", author);
                row.put("authorURL", authorURL);
                row.put("avatar", avatar);
                row.put("text", text);
                row.put("date", date);
                row.put("rating", rating);

                reviews.put(row);

            }

        }
        catch(Exception e){
            Log.d("error", e.toString());
        }
        finally {
            cursor.close();
            db.close();
        }

        return reviews;

    }

    public JSONObject getDetailsInfo(String place_id) {

        JSONObject row = new JSONObject();


        String query = "SELECT  * FROM " + TABLE_NEARBY_PLACES + " WHERE " + COLUMN_PLACE_ID + "=?";
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = db.rawQuery(query, new String[] {place_id});

        try {
            while (cursor.moveToNext()) {

                String name = cursor.getString(cursor.getColumnIndex(COLUMN_NAME));
                String vicinity = cursor.getString(cursor.getColumnIndex(COLUMN_VICINITY));
                String phoneNumber = cursor.getString(cursor.getColumnIndex(COLUMN_PHONE_NUMBER));
                String priceLevel = cursor.getInt(cursor.getColumnIndex(COLUMN_PRICE_LEVEL)) + "";
                String rating = cursor.getString(cursor.getColumnIndex(COLUMN_RATING)) + "";
                String googlePage = cursor.getString(cursor.getColumnIndex(COLUMN_GOOGLE_PAGE));
                String website = cursor.getString(cursor.getColumnIndex(COLUMN_WEBSITE));

                row.put("name", name);
                row.put("formatted_address", vicinity);
                row.put("formatted_phone_number", phoneNumber);
                row.put("price_level", priceLevel);
                row.put("rating", rating);
                row.put("url", googlePage);
                row.put("website", website);
            }

        }
        catch(Exception e){
            Log.d("error", e.toString());
        }
        finally {
            cursor.close();
            db.close();
        }

        return row;
    }

    public ArrayList<String> getDetailsPhotos(String placeID) {

        ArrayList<String> arr = null;
        CursorContainer container = getCursor(placeID, "photos");
        SQLiteDatabase db = container.db();
        Cursor cursor = container.cursor();


        try {

            while (cursor.moveToNext()) {

                String URLs = cursor.getString(0);
                String [] photosArray = URLs != null ? URLs.split(delim) : null;

                arr = photosArray != null ?  new ArrayList<>(Arrays.asList(photosArray)) : null;

            }
        }

        catch(Exception e){
            // TODO: output no results/failed to get results error here
            Log.e("error", e.toString());
        }
        finally {
            cursor.close();
            db.close();
            }
        return arr;
    }

    public String getPlaceName(String placeID, String requestFor) {


        String value = "?";
        double d;

        CursorContainer container = getCursor(placeID, requestFor);
        SQLiteDatabase db = container.db();
        Cursor cursor = container.cursor();

        while (cursor.moveToNext()) {

            if (requestFor.equals("latitude") || requestFor.equals("longitude")) {

                d = cursor.getDouble(0);
                value = d + "";
            }
            else {
                value = cursor.getString(0);
            }

        }

        cursor.close();
        db.close();
        return value;

    }


//
    private int getPageNum() {

        // Determine the page number of a new entry based on the number of entries
        // already in the database
        // maximum pageNum is 3 for Google NearbyPlaces search

        final int PAGE_SIZE = 20;
        int pageNum;

        String countQuery = "SELECT  * FROM " + TABLE_NEARBY_PLACES;
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = db.rawQuery(countQuery, null);
        int count = cursor.getCount();


        if (count <= PAGE_SIZE) { pageNum = 1; }
        else if (count <= PAGE_SIZE * 2) { pageNum = 2; }
        else {pageNum = 3; }


        cursor.close();
        db.close();
        return pageNum;

    }

    public int getCount(String...optional) {

        int count;
        boolean checkForDetails = false;
        String query = "SELECT  * FROM " + TABLE_NEARBY_PLACES;
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = null;

        if (optional.length > 0) {

            if (optional[0].equals("favorites")) {
                query = "SELECT  * FROM " + TABLE_NEARBY_PLACES + " WHERE " + COLUMN_FAVORITED + " =1";
            } else if (optional[0].equals("detailsAvailability")) {
                String placeID = optional[1];
                query = "SELECT  * FROM " + TABLE_NEARBY_PLACES + " WHERE " + COLUMN_DETAILS_AVAILABLE + "=?";
                query += " AND " + COLUMN_PLACE_ID + "=?";
                cursor = db.rawQuery(query, new String[]{"1", placeID});
                checkForDetails = true;
            } else if (optional[0].equals("yelp")) {
                String placeID = optional[1];
                query = "SELECT  * FROM " + TABLE_REVIEWS + " WHERE " + COLUMN_REVIEW_SOURCE + "=?";
                query += " AND " + COLUMN_PLACE_ID + "=?";
                cursor = db.rawQuery(query, new String[]{"Yelp", placeID});
                checkForDetails = true;
            }
        }
        if (!checkForDetails) { cursor = db.rawQuery(query, null);}

        count = cursor.getCount();

        cursor.close();
        db.close();
        return count;

    }

    /*
    * For place details, both the Google API results and Yelp reviews need to be in the
    * database. Because we decouple the request for Yelp reviews, we want to be sure that
    * the place details is complete before we return true. Otherwise, we'll need to make a new
    * request.
    * */
    public boolean detailsInDB(String placeID) {

        int yelpCount = getCount("yelp", placeID);
        int other =  getCount("detailsAvailability", placeID);

        return yelpCount > 0 && other > 0;
    }

    /* A wrapper class to hold a cursor and db file descriptors so that the client can close
     *  both connections.
     */
    class CursorContainer {

        private SQLiteDatabase db;
        private Cursor cursor;

        public CursorContainer(SQLiteDatabase db,  Cursor cursor) {

            this.db = db;
            this.cursor = cursor;

        }

        public SQLiteDatabase db() { return db; }

        public Cursor cursor() { return cursor;}

    }


}
