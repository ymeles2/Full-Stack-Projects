
import java.util.Arrays;
import java.lang.Math;

/**
	* The CanonicalForm class provides string canonicalization so that we 
	* respect the case-sensitivity and uniqueness of a string when grouping 
	* anagrams and doing word search. 
	* PRE:
	*	1. anyString == any string containing ASCII characters
	* Rep. Inv.
	* 	1. unique.length() == mult.length
	*	2. canonical.length() == raw.length()
	*	3. canonical is an anagram of raw
**/

public class CanonicalForm {

	// setting them to be final since they're all created once and are passed 
	// along to the client
	private final String raw;
	private final String canonical;
	private final String unique;
	private final int[] mult;

	/**	
		* Create a canonical string object from a given string. Parse out 
		* unique characters from the string and compute the multiplicity. 
		* @param anyString a string consisting of any ASCII characters
		* PRE: anyString = [a-zA-Z]
	*/
	public CanonicalForm(String anyString) {

		raw = anyString;
		canonical = canonicalize(raw);
		
		if (canonical.length() == 0) {
			// calls to unique() will fail if canonical is empty. This happens
			// when the rack doesn't contain any letters. 
			unique = raw;
		}
		else {
			unique = unique();
		}
		mult = multiplicity();

	}


	/**
		* Canonicalize a raw string by splitting it into characters and rebuilding
		* a new string sorted by the ascii values of the characters.
		* @param raw the string to canonicalize
		* @return sorted canonicalized string
	*/
	private String canonicalize(String raw) {
		
		String sorted = "";
		char[] chars = new char[raw.length()];
		for (int i = 0; i < raw.length(); i++) {
			chars[i] = raw.charAt(i);
		}
		Arrays.sort(chars);

		for (int i = 0; i < raw.length(); i++) {
			sorted += chars[i];
		}
		return sorted;
	}

	/**
		* Build a string consisting of only the unique characters in a string 
		* while maining the order of the characters in the original string.
		* @return str the unique string 
	*/
	private String unique() {

		
		String str  = "" + canonical.charAt(0);
		for (int i = 1; i < canonical.length(); i++) {
		
			if (canonical.charAt(i) != str.charAt(str.length()-1)) {
				str += canonical.charAt(i);
			}

		}

		return str;

	}

	/**
		* Compute the multiplicity of a string by counting the frequency of its
		* characters. 
		* @return mult 	an array of multiplicity, where each index corresponds 
		* 				to the position of the chracter in the unique string
	*/
	private int[] multiplicity() {

		int [] mult = new int[unique.length()];
		int k = 0;
		for (int i = 0; i < unique.length(); i++) {

			for (int j = k; j < canonical.length(); j++) {

				if (canonical.charAt(j) == unique.charAt(i)) {
					mult[i]++;
				}
				else {
					k = j;
					break;
				}
			}

		}

		return mult;
	}


	
	/**
		* Return the canonical string
		* @return canonical the canonical string
	*/
	public String getCanonical() {

		return new String(canonical);
	}

	/**
		* Return the unique string
		* @return unique the unique string
	*/
	public String getUnique() {

		return new String(unique);
	}

	/**
		* Return string multiplicity
		* @return mult integer array of multiplicity
	*/
	public int[] getMult() {

		return Arrays.copyOf(mult, mult.length);
	}


	/**
		* Override Object's equals() method to determine the equality of 
		* CanonicalForm objects. Return true if the input object has the same
		* canonical and unique strings as well as the same multiplicity.
		* Note: we're checking to see if two strings are anagrams of each other
		* @return whether or not the input object is the same as an instance of 
		* 			CanonicalForm
	*/
	@Override
	public boolean equals(Object obj) {

		if (obj instanceof CanonicalForm) {

			CanonicalForm newObj = (CanonicalForm) obj;

			if (canonical.equals(newObj.canonical) && unique.equals(newObj.unique) &&
				Arrays.equals(mult, newObj.mult)) {
				return true;
			}

		}
		return false;


	}
	
	/**
		* Override Object's hashCode() and compute the hashcode for an instance
		* of CanonicalForm. 
		* @return hash the hash code
		* PRE: if a.equals(b), then a.hashCode() == b.hashCode();
		* Note: All anagrams of a given CanonicalForm hash to the same bucket
	*/
	@Override
	public int hashCode() {

		int hash = canonical.hashCode() + unique.hashCode();
		int p = 1;
		for (int i = 0; i < mult.length; i++) {
			p *= mult[i];
		}

		hash =  Math.abs(hash + new Integer(p).hashCode());
		return hash;

	}
}