package entertainment.search.placessearch;


import android.content.SharedPreferences;
import android.content.res.Resources;
import android.graphics.drawable.Drawable;
import android.preference.PreferenceManager;
import android.support.v4.app.Fragment;
import android.os.Bundle;
import android.text.InputType;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.RadioButton;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import com.seatgeek.placesautocomplete.PlacesAutocompleteTextView;

import org.json.JSONObject;



public class SearchFragment extends Fragment {

    private String category;
    private MainActivity activity;
    public SearchFragment() {
    }


    @Override
    public void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        // Populate the dropdown list and inflate the layout fragment
        View v = inflater.inflate(R.layout.search_form, container, false);

        // Set onclick listeners
        Button btnClear = (Button) v.findViewById(R.id.btn_clear);
        Button btnSearch = (Button) v.findViewById(R.id.btn_search);
        RadioButton otherLocBtn = (RadioButton) v.findViewById(R.id.radio_other_loc);
        RadioButton currLocBtn = (RadioButton) v.findViewById(R.id.radio_current_loc);
        final EditText keyword = (EditText) v.findViewById(R.id.keyword_input);
        final EditText distance = (EditText) v.findViewById(R.id.distance_input);
        final PlacesAutocompleteTextView otherLocInput = (PlacesAutocompleteTextView) v.findViewById(R.id.other_loc_input);

        activity = (MainActivity) getActivity();
        category = "Default";
        setSpinnerListeners(v);

        btnClear.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                clearForm(v);
            }
        });

        btnSearch.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                search(v);
            }
        });

        currLocBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                updateRadioBtn(v);
            }
        });

        otherLocBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                updateRadioBtn(v);
            }
        });

        keyword.setOnFocusChangeListener(new View.OnFocusChangeListener() {
            @Override
            public void onFocusChange(View v, boolean hasFocus) {
                setOnFocusEvent(R.id.keyword_input, hasFocus);
            }
        });
        distance.setOnFocusChangeListener(new View.OnFocusChangeListener() {
            @Override
            public void onFocusChange(View v, boolean hasFocus) {
                setOnFocusEvent(R.id.distance_input, hasFocus);
            }
        });
        otherLocInput.setOnFocusChangeListener(new View.OnFocusChangeListener() {
            @Override
            public void onFocusChange(View v, boolean hasFocus) {
                setOnFocusEvent(R.id.other_loc_input, hasFocus);
            }
        });

        //clear any existing result cache
        SharedPreferences preferenceSettings = PreferenceManager.getDefaultSharedPreferences(getActivity());
        preferenceSettings.edit().clear().commit();

        return v;
    }


    public void populateDropdown(View v) {

        String[] values = getResources().getStringArray(R.array.categories);
        Spinner spinner = (Spinner) v.findViewById(R.id.spinner);

        if (spinner == null) {
            spinner = getActivity().findViewById(R.id.spinner);
        }

        ArrayAdapter<String> adapter = new ArrayAdapter<String>(this.getActivity(),
                android.R.layout.simple_spinner_dropdown_item, values);
        adapter.setDropDownViewResource(android.R.layout.simple_dropdown_item_1line);
        spinner.setAdapter(adapter);

    }

    private void setOnFocusEvent(int id, boolean hasFocus) {

        EditText textElem = (EditText) getActivity().findViewById(id);
        Resources res = getResources();
        Drawable background;

        if (hasFocus) {
            background = res.getDrawable(R.drawable.border_color_active);

        } else {
            background = res.getDrawable(R.drawable.border_color);
        }

        textElem.setBackground(background);
    }

    private void updateRadioBtn(View v) {

        // Toggle button coloration. If otherLocBtn is checked, enable the input box. Otherwise,
        // disable the box.

        RadioButton currLocBtn = (RadioButton) getActivity().findViewById(R.id.radio_current_loc);
        RadioButton otherLocBtn = (RadioButton) getActivity().findViewById(R.id.radio_other_loc);
        EditText otherLocInput = (EditText) getActivity().findViewById(R.id.other_loc_input);

        if (currLocBtn.isChecked()) {

            resetRadioBtn();
        } else if (otherLocBtn.isChecked()) {

            currLocBtn.setButtonTintList(getResources().getColorStateList(R.color.radioInactive));
            otherLocBtn.setButtonTintList(getResources().getColorStateList(R.color.webtech_pink));
            otherLocInput.setInputType(InputType.TYPE_CLASS_TEXT);
            otherLocInput.setFocusableInTouchMode(true);
            otherLocInput.setFocusable(true);

        }
    }

    private void resetRadioBtn() {

        // Reset radio buttons and disable custom location input

        RadioButton currLocBtn = (RadioButton) getActivity().findViewById(R.id.radio_current_loc);
        RadioButton otherLocBtn = (RadioButton) getActivity().findViewById(R.id.radio_other_loc);
        EditText otherLocInput = (EditText) getActivity().findViewById(R.id.other_loc_input);
        TextView errorMsg2 = (TextView) getActivity().findViewById(R.id.mandatory_msg_2);

        currLocBtn.setChecked(true);
        otherLocBtn.setChecked(false);
        currLocBtn.setButtonTintList(getResources().getColorStateList(R.color.webtech_pink));
        otherLocBtn.setButtonTintList(getResources().getColorStateList(R.color.radioInactive));
        otherLocInput.setInputType(InputType.TYPE_NULL);
        otherLocInput.setFocusableInTouchMode(false);
        otherLocInput.setFocusable(false);
        errorMsg2.setVisibility(View.INVISIBLE);

    }

    private boolean formIsValid() {


        boolean isValid = true;

        EditText keyword = (EditText) getActivity().findViewById(R.id.keyword_input);
        ;
        EditText distance = (EditText) getActivity().findViewById((R.id.distance_input));
        EditText otherLocInput = (EditText) getActivity().findViewById(R.id.other_loc_input);
        RadioButton otherLocBtn = (RadioButton) getActivity().findViewById(R.id.radio_other_loc);
        TextView textView;

        String keywordStr = keyword.getText().toString();
        keywordStr = keywordStr.replaceAll("\\s+", "");

        if (keywordStr.length() == 0) {
            isValid = false;
            textView = (TextView) getActivity().findViewById(R.id.mandatory_msg_1);
            textView.setVisibility(View.VISIBLE);

        }

        if (otherLocBtn.isChecked()) {
            String customLoc = otherLocInput.getText().toString();
            customLoc = customLoc.replaceAll("\\s+", "");
            if (customLoc.length() == 0) {
                isValid = false;
                textView = (TextView) getActivity().findViewById(R.id.mandatory_msg_2);
                textView.setVisibility(View.VISIBLE);
            }

        }


        if (!isValid) {
            showToast();
        }

        return isValid;
    }

    private void setSpinnerListeners(View v) {

        Spinner spinner = (Spinner) v.findViewById(R.id.spinner);
        
        spinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parentView, View selectedItemView, int position, long id) {
                // your code here
                Object item = parentView.getItemAtPosition(position);
                category = item.toString();
            }

            @Override
            public void onNothingSelected(AdapterView<?> parentView) {
               // this doesn't really apply
                category = "Default";
            }

        });

    }

    private void showToast() {

        LayoutInflater inflater = getLayoutInflater();
        View layout = inflater.inflate(R.layout.toast,
                (ViewGroup) getActivity().findViewById(R.id.custom_toast_container));

        Toast toast = new Toast(getContext());
        toast.setGravity(Gravity.BOTTOM, 0, 100);
        toast.setDuration(Toast.LENGTH_LONG);
        toast.setView(layout);
        toast.show();
    }

    private void search(View v) {

        if (formIsValid()) {

            SearchServices ss = new SearchServices(getActivity(), v);
            JSONObject formData = getFormData();
            ss.search(null, formData, "searchForm");
        }

    }

    private void clearForm(View v) {

        EditText keyword = (EditText) getActivity().findViewById(R.id.keyword_input);
        EditText distance = (EditText) getActivity().findViewById((R.id.distance_input));
        EditText otherLocInput = (EditText) getActivity().findViewById(R.id.other_loc_input);
        TextView errorMsg1 = (TextView) getActivity().findViewById(R.id.mandatory_msg_1);
        TextView errorMsg2 = (TextView) getActivity().findViewById(R.id.mandatory_msg_2);

        keyword.setText("");
        distance.setText("");
        otherLocInput.setText("");
        errorMsg1.setVisibility(View.INVISIBLE);
        errorMsg2.setVisibility(View.INVISIBLE);

        populateDropdown(v);
        resetRadioBtn();

    }

    public JSONObject getFormData() {

        EditText keyword = (EditText) getActivity().findViewById(R.id.keyword_input);
        EditText distance = (EditText) getActivity().findViewById((R.id.distance_input));
        PlacesAutocompleteTextView otherLocInput = (PlacesAutocompleteTextView) getActivity().findViewById(R.id.other_loc_input);
        RadioButton otherLocBtn = (RadioButton) getActivity().findViewById(R.id.radio_other_loc);

        String otherLocValue = otherLocInput.getText().toString();
        double centerLat = Double.parseDouble(activity.getCurrentLocation().split(",")[0]);
        double centerLon =  Double.parseDouble(activity.getCurrentLocation().split(",")[1]);

        String keywordValue = keyword.getText().toString();
        keywordValue = keywordValue.replace(' ', '+');

        if (otherLocBtn.isChecked()) {

            centerLat = -1;
            centerLon = -1;
            otherLocValue = otherLocValue.replace(' ', '+');

        }
        else {
            otherLocValue = "-1";
        }

        String distanceValue = distance.getText().toString();
        String categoryValue = category.toLowerCase().replace(' ', '_');
        if (distanceValue.equals("")) {distanceValue = "10";}


        JSONObject formData = new JSONObject();
        try {


            formData.put("keyword", keywordValue);
            formData.put("distance", distanceValue);
            formData.put("customLoc", otherLocValue);
            formData.put("category", categoryValue);
            formData.put("centerLat", centerLat);
            formData.put("centerLon", centerLon);
        }
        catch(Exception e){
            Log.e("error", e.toString());
        }
        return formData;
    }
}