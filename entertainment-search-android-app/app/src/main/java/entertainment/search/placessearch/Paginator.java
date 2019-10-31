package entertainment.search.placessearch;

import android.app.Activity;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.RelativeLayout;

import org.json.JSONObject;

public class Paginator {

    private Activity activity;
    private String response;
    private ResultsActivity resultsInstace;
    private FavoritesFragment fragActivity;

    public Paginator(Activity activity, String response, ResultsActivity resultsInstace, FavoritesFragment
                     fragActivity) {

        this.activity = activity;
        this.response = response;
        this.resultsInstace = resultsInstace;
        this.fragActivity = fragActivity;

    }

    public void showPagination(int pageNum) {

        RelativeLayout paginator = activity.findViewById(R.id.pagination_container);
        paginator.removeAllViews();
        activity.getLayoutInflater().inflate(R.layout.pagination, paginator, true);

        // handle prev button
        //TODO: set listener if previous page available and make it clickable
        final Button prevBtn = (Button) activity.findViewById(R.id.btn_prev);
        final Button nextBtn = (Button) activity.findViewById(R.id.btn_next);

        nextBtn.setEnabled(false);
        nextBtn.setClickable(false);

        if (pageNum == 1) {

            prevBtn.setEnabled(false);
            prevBtn.setClickable(false);
        } else {
            setPrevBtnListener(prevBtn, pageNum);
        }

        if (pageNum < 3) {
            try {
                String next_page_token = null;
                if (response != null) {
                    JSONObject r = new JSONObject(response);

                    if (r.has("next_page_token")) {
                        next_page_token = r.getString("next_page_token");
                    }
                }
                Log.d("token", "next page token-------------------------------token----------: " + next_page_token);
                setNextBtnListener(nextBtn, next_page_token, pageNum);
            }
            catch(Exception e){
                // TODO: output no results/failed to get results error here
                Log.d("error", e.toString());
            }
        }

    }

    private void setNextBtnListener(final Button nextBtn, String next_page_token, int currentPage) {


        nextBtn.setEnabled(true);
        nextBtn.setClickable(true);

        if (next_page_token == null) {

            next_page_token = currentPage + "";
        }

        nextBtn.setTag(next_page_token);
        nextBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                resultsInstace.loadPaginatedPage(null, nextBtn);
            }
        });

    }

    private void setPrevBtnListener(final Button prevBtn, int currentPage) {


        prevBtn.setTag(currentPage);
        prevBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                resultsInstace.loadPaginatedPage(prevBtn, null);
            }
        });

        if (currentPage < 3) {

            final Button nextBtn = (Button) activity.findViewById(R.id.btn_next);
            setNextBtnListener(nextBtn, null, currentPage);
        }


    }
}
