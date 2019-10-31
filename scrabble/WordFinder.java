
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Scanner;

/**
	* WordFinder takes user input to build racks and print all anagrams found 
	* in the rack and its subsets. It also handles IO-related errors. If no 
	* dictionary file is provided, it uses the default file, sowpods.txt. If
	* no file can be found, it notifies the user and terminates the program.
	* Otherwise, it will keep asking for a rack and outputting the resulting
	* anagrams, sorted by their scores, until the user chooses to exit.
	*
	* Usage: java WordFinder [dictionary]
	* dictionary is an optional argument
*/
public class WordFinder {

	private static final String DEFAULT_DICT = "sowpods.txt";

	public static void main(String[] args) {

		String fileName;

		if (args.length == 1 ) {
			fileName = args[0];
		}
		else {
			fileName = DEFAULT_DICT;
		}

		try {
			
			AnagramDictionary ad = new AnagramDictionary(fileName);
			findWords(ad);
		}
		
		catch (FileNotFoundException exception) {
			System.out.println("File not found: "+fileName);
		}

		
	}

	/**
		* Ask the user for a new rack and process the rack. Exit the program 
		* if the user indicates so by typing a period to quit.
		* @param ad the anagram dictionary to use 
		*
		* PRE: done = false if "." hasn't been typed yet
	*/
	private static void findWords(AnagramDictionary ad) {
		
		boolean done = false;
		String rackStr = "";
		Scanner in = new Scanner(System.in);

		System.out.println("Type . to quit.");
		
		while (!done) {

			
			try {

				System.out.print("Rack? ");
				rackStr = in.next();

				if (rackStr.equals(".")) {

					done = true;
				}

				else {

					if (rackStr.length() > 0) {

						Rack rack = new Rack(rackStr, ad);
						processRack(rack);
					}
				}
			}
			catch (NoSuchElementException exception) {

				// NoSuchElementException raised whenever testing is done 
				// with an empty file redirect; behavior is undefined since 
				// no quit instruction is given
				done = true;
			}
	
		}
	}

	/**
		* Process the rack by printing matching anagrams for each subset of the 
		* rack, sorted in decreasing order by score
		* @param rack the rack to process
	*/
	private static void processRack(Rack rack) {

		ArrayList<Map.Entry<String, Integer>> matches = rack.getSorted();

		String numFound = "We can make "+matches.size();
		String canonical = "\""+rack.getRawCanonical()+"\"";
		System.out.println(numFound+" words from "+canonical);

		if (matches.size() > 0) {

			String msg = "All of the words with their scores " +
							"(sorted by score):";

			System.out.println(msg);

			for (Map.Entry<String, Integer> entry: matches) {

				System.out.println(entry.getValue() + ": "+entry.getKey());

			}
		}
		

		}

}


