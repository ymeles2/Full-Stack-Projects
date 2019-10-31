
import java.util.Comparator;
import java.util.Map;

/**
		* MatchSorter implements the Comparator interface to provide 
		* object comparison for sorting on a custom field, namely, the scrabble
		* score of an anagram 
*/
public class MatchSorter implements Comparator<Map.Entry<String, Integer>> {

	/**
		* Compares two objects and returns -1 if a should come before b, 1 if 
		* b should come before a. If both a and be have the same score, returns
		* -1 if a comes before b lexicographically, 1 if otherwise.
	*/
	public int compare(Map.Entry<String, Integer> a, Map.Entry<String, Integer> b) {

		if (a.getValue() > b.getValue()) {
			return -1;
		}
		else if (a.getValue() < b.getValue()) {
			return 1;
		}
		else {

			return a.getKey().compareTo(b.getKey());

		}
	}
}