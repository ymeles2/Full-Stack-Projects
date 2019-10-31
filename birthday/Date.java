import java.util.Calendar;
import java.util.GregorianCalendar;
public class Date {
    public static void main(String[] args) {
	Calendar gregCal = new GregorianCalendar(1995, 0, 20);
	int month = gregCal.get(Calendar.MONTH);
	int date = gregCal.get(Calendar.DATE);
	int year = gregCal.get(Calendar.YEAR);
	month += 1;
	System.out.println(month+"/"+date+"/"+year);
	gregCal.add(Calendar.DATE, 20);
	month = gregCal.get(Calendar.MONTH);
	date = gregCal.get(Calendar.DATE);
	year = gregCal.get(Calendar.YEAR);
	month += 1;
	System.out.println(month+"/"+date+"/"+year);
}
}
