package entertainment.search.placessearch;

import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Spinner;
import android.widget.TableLayout;

public class ReviewsFragment extends Fragment {

    private String placeID;
    String reviewsFrom;
    SortBy sortBy;
    View v;

    public ReviewsFragment() {
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        // Populate the dropdown list and inflate the layout fragment
        v = inflater.inflate(R.layout.reviews_fragment, container, false);

        DetailsActivity activity = (DetailsActivity) getActivity();
        placeID = activity.getDetailsPlaceID();

        populateDropdown(v, R.id.review_source, R.array.review_source);
        populateDropdown(v, R.id.review_sort_option, R.array.review_sort_method);

        setSpinnerListeners(v);

        reviewsFrom = "Google";
        sortBy = SortBy.DEFAULT_ORDER;
        populateReviews();



        return v;
    }

    private void populateDropdown(View v, int spinnerType, int arrayType) {

        String[] values = getResources().getStringArray(arrayType);
        Spinner spinner = (Spinner) v.findViewById(spinnerType);

        if (spinner == null) {
            spinner = getActivity().findViewById(spinnerType);
        }

        ArrayAdapter<String> adapter = new ArrayAdapter<String>(this.getActivity(),
                android.R.layout.simple_spinner_dropdown_item, values);
        adapter.setDropDownViewResource(android.R.layout.simple_dropdown_item_1line);
        spinner.setAdapter(adapter);

    }

    private void populateReviews() {

        TableLayout table = v.findViewById(R.id.reviews_table);
        table.removeAllViews();
        table.setPadding(0,20, 0,20 );

        Table tableObj = new Table(getActivity(), null, v, null);
        tableObj.populateReviews(table, placeID, reviewsFrom, sortBy);

    }


    /*
    * Set review dropdown click listeners. If review source is selected, get the current sort option
    * selected and vice versa since only one of them would fire a signal at a time.
    * */
    private void setSpinnerListeners(View v) {

        Spinner reviewSource = (Spinner) v.findViewById(R.id.review_source);
        Spinner sortingOption = (Spinner) v.findViewById(R.id.review_sort_option);

        reviewSource.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parentView, View selectedItemView, int position, long id) {
                // your code here
                Object item = parentView.getItemAtPosition(position);
                String value = item.toString();
                switch(value) {
                    case "Google reviews":
                        reviewsFrom = "Google";
                        break;
                    case "Yelp reviews":
                        reviewsFrom = "Yelp";
                        break;
                    default:
                        reviewsFrom = "Google";
                        break;
                }
                populateReviews();
            }

            @Override
            public void onNothingSelected(AdapterView<?> parentView) {
                // this doesn't really apply
                reviewsFrom = "Google";
            }

        });

        sortingOption.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parentView, View selectedItemView, int position, long id) {
                Object item = parentView.getItemAtPosition(position);
                String value = item.toString();
                switch (value) {

                    case "Default Order":
                        sortBy = SortBy.DEFAULT_ORDER;
                        break;
                    case "Highest Rating":
                        sortBy = SortBy.HIGHEST_RATING;
                        break;
                    case "Lowest Rating":
                        sortBy = SortBy.LOWEST_RATING;
                        break;
                    case "Most Recent":
                        sortBy = SortBy.MOST_RECENT;
                        break;
                    case "Least Recent":
                        sortBy = SortBy.LEAST_RECENT;
                        break;
                    default:
                        sortBy = SortBy.DEFAULT_ORDER;
                        break;
                    }
                populateReviews();
                }

            @Override
            public void onNothingSelected(AdapterView<?> parentView) {
                // this doesn't really apply
                sortBy = SortBy.DEFAULT_ORDER;
            }

        });
    }
}

//
