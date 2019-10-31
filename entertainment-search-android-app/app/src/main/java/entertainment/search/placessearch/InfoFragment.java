package entertainment.search.placessearch;

import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TableLayout;

public class InfoFragment extends Fragment {

    private String placeID;

    public InfoFragment() {}

    @Override
    public void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        // Populate the dropdown list and inflate the layout fragment
        View v = inflater.inflate(R.layout.info_fragment, container, false);

        DetailsActivity activity = (DetailsActivity) getActivity();
        placeID = activity.getDetailsPlaceID();

        populateInfoTab(v);

        return v;
    }

    private void populateInfoTab(View v) {


        TableLayout table = v.findViewById(R.id.info_fragment_table);

        table.removeAllViews();
        table.setPadding(0,40, 0,50 );

        Table tableObj = new Table(getActivity(), null, v, null);
        tableObj.getDetailsInfoTable(table, placeID);


    }
}
