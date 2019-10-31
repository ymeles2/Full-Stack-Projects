import java.util.Calendar;
import java.util.Scanner;
import java.util.GregorianCalendar;
public class Birthday3 {
    public static void main(String[] args) {
	Scanner in = new Scanner(System.in);
	System.out.println("Enter your birth month [1..12]: ");
	int birthMonth =  in.nextInt();
	System.out.println("Enter your birth day of month: ");
	int birthDate = in.nextInt();
	System.out.println("Enter your birth year [4-digit year]: ");
	int birthYear = in.nextInt();
	birthMonth -= 1;
	Calendar birthCal = new GregorianCalendar(birthYear, birthMonth, birthDate);
	Calendar currCal = new GregorianCalendar();
	int currMonth = currCal.get(Calendar.MONTH);
	int currDate = currCal.get(Calendar.DATE);
	int currYear = currCal.get(Calendar.YEAR);
	int bMonth = birthCal.get(Calendar.MONTH);
	int bDate = birthCal.get(Calendar.DATE);
	if (currMonth == bMonth) {
		if (currDate == bDate){
            System.out.println("Your birthday is today!");
	    }
	    else if (currDate > bDate){
	    	System.out.println("Your birthday has already happened this year.");

	    }
	    else {
	    	System.out.println("Your birthday has not happend this year.");

	    }

	}
	else if (currMonth > bMonth){
		System.out.println("Your birthday has already happened this year.");
	}
	else {
		System.out.println("Your birthday has not happend this year.");
	}
	int age = currYear - birthYear;
	System.out.println("You're "+age+" years old.");
	

	
}
}
