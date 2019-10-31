package entertainment.search.placessearch;

import android.app.Activity;
import android.support.v4.app.Fragment;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TableLayout;

import db.Database;


public class FavoritesFragment extends Fragment  {

    private Activity activity;
    public FavoritesFragment() {}

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {


        View v =  inflater.inflate(R.layout.favorites_fragment, container, false);
        activity = getActivity();
//        fragmentStackManager();

        populateFavorites(v, 1);
        return v;
    }

//    private void fragmentStackManager() {
//
//        FragmentManager fragmentManager = getFragmentManager();
//        FragmentTransaction fragmentTransaction = fragmentManager.beginTransaction();
//        fragmentTransaction.replace(R.id.fav_fragment_container, this);
//        fragmentTransaction.addToBackStack(null);
//        fragmentTransaction.commit();
//
//    }

    public void populateFavorites(View v, int pageFromDB) {


        Database db = new Database(activity);
        Table tableObj = new Table(activity, null, v, this);
//        boolean isPopulated = false;
        TableLayout table;

        if (db.getCount("favorites") > 0) {


            tableObj.populateTable("favorites", pageFromDB);
            table = tableObj.getTableObj();
            table.setPadding(0,50, 0,50 );


        }
        else {

            tableObj.showEmpty("favorites");
        }
    }

}