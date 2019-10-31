
import java.util.ArrayList;
import java.util.Collections;
import java.util.Map;
import java.util.HashMap;
import java.util.regex.Pattern;
import java.util.regex.Matcher;

/**
 * A Rack of Scrabble tiles. Implements additional behavior to provide a complete
  * list of all the anagrams that can be obtained from the rack and all of its
  * subsets.
  * PRE: 
  *   1. rawRack.length() >= 2
  *   2. ad (AnagramDictionary) must be a valid dictionary object, i.e. contains 
  *       a dictionary
  * Rep. Inv.:
  *   1. rawRack is an anagram of rawCanonical
  *   2. !cleanRack.equals(rawRack) or cleanRack.equals(rawRack) [either is valid, 
  *     depending on the characters of rawRack]
  *   
  *   
  *  
 */

public class Rack {

  // Rack processing happens only once in the constructor (except for sorting
  // the resulting matches) so we'll make our data final since some of them
  // are passed to the client

  private final String rawRack;
  private final String cleanRack;
  private final AnagramDictionary dictionary;
  private final CanonicalForm canonicalRack; // canonical object of the clean rack
  private final String rawCanonical; // canonical string of the raw rack
  private final ArrayList<String> subsets;
  private final HashMap<String, Integer> matches;
  private ArrayList<Map.Entry<String, Integer>> sortedMatches;

  /**
    * Create a new Rack object. 
    * @param rawString a user-provided, unprocessed string representing a rack
    * @param ad   the anagram dictionary to use for this rack
  */
  public Rack(String rawString, AnagramDictionary ad) {

    rawRack = rawString;
    rawCanonical =  new CanonicalForm(rawRack).getCanonical();
    dictionary = ad;
    cleanRack = parseRack();
    canonicalRack = new CanonicalForm(cleanRack);
    matches = new HashMap<String, Integer>();
    subsets = allSubsets(canonicalRack.getUnique(), canonicalRack.getMult(), 0);
    findMatches();
    sortMatches();

  }

  /**
      * Parses a raw rack input and returns a string consisting of characters 
      * [a-zA-Z]. For example, if rack = aapPl&4@me, returns aapPlme. If raw rack 
      * only consists of alphabetical characters, returns equivalent string.
      * @return matches a string composed of letters between a-z, upper- and or 
      *                 lower-case
  */
  private String parseRack() {
    

    Pattern p = Pattern.compile("[a-zA-Z]");
    Matcher m = p.matcher(rawRack);
    String matches = "";
    while (m.find()) {
      matches += m.group();

    }
    return matches;

  }

  /**
    * Query the anagram dictionary and find all the anagrams for every subset
    * of the rack with two or more characters.
    *
    * Note: findMatches will match anything in the dictionary in a case-senstive
    * manner. That means if a rack consists of "aAppPPlLeE", it will have the 
    * following subsets (out of many more): "apple", "APPLE", "Apple", etc. If the 
    * the dictionary file contains all three words, it will match them all. 
    * However, if the file only contains lower-case or upper-case words, then it 
    * will match "apple" or "APPLE", respectively. Our implementation is based 
    * on the assumption that we should have zero knowledge of what kind of 
    * dictionary file we have, i.e. whether it's upper-case, lower-case, a mix, 
    * etc., and instead simply match a rack and its subsets to any word in the 
    * dictionary that meets the definition of an anagram while at the same time 
    * doing so in a case-senstive manner. This means "apple" and "APPLE" would 
    * not be considered anagrams of each other but definitely anagrams of the 
    * rack.     
  */
  private void findMatches() {

    ArrayList<String> anagrams;

    for (String subset: subsets) {
      if (subset.length() > 1) {
        CanonicalForm subsetCF = new CanonicalForm(subset);
        anagrams = dictionary.getAnagramsOf(subset);
      
        if (anagrams.size() > 0) {
            Integer score = ScoreTable.subsetScore(subsetCF);
            for (String anagram: anagrams) {
              matches.put(anagram, score);
            }
        }
    }

    }
  }

  /**
    * Sort anagrams by score. 
  */ 
  private void sortMatches() {

    sortedMatches = new ArrayList<>(matches.entrySet());
    Collections.sort(sortedMatches, new MatchSorter());
    
  }


   /**
    * Finds all subsets of the multiset starting at position k in unique and mult.
    * unique and mult describe a multiset such that mult[i] is the multiplicity of the char
    *      unique.charAt(i).
    * PRE: mult.length must be at least as big as unique.length()
    *      0 <= k <= unique.length()
    * @param unique a string of unique letters
    * @param mult the multiplicity of each letter from unique.  
    * @param k the smallest index of unique and mult to consider.
    * @return all subsets of the indicated multiset
    * @author Claire Bono
    */
   private static ArrayList<String> allSubsets(String unique, int[] mult, int k) {
    
      ArrayList<String> allCombos = new ArrayList<>();
      
      if (k == unique.length()) {  // multiset is empty
         allCombos.add("");
         return allCombos;
      }
      
      // get all subsets of the multiset without the first unique char
      ArrayList<String> restCombos = allSubsets(unique, mult, k+1);
      
      // prepend all possible numbers of the first char (i.e., the one at position k) 
      // to the front of each string in restCombos.  Suppose that char is 'a'...
      
      String firstPart = "";          // in outer loop firstPart takes on the values: "", "a", "aa", ...
      for (int n = 0; n <= mult[k]; n++) {   
         for (int i = 0; i < restCombos.size(); i++) {  // for each of the subsets 
                                                        // we found in the recursive call
            // create and add a new string with n 'a's in front of that subset
            allCombos.add(firstPart + restCombos.get(i));  
         }
         firstPart += unique.charAt(k);  // append another instance of 'a' to the first part
      }
      
      return allCombos;
   }


  /**
    * Return a list of anagrams discovered for a rack, sorted in decreasing 
    * order of points.
    * @return sortedMatches a sorted list of map entries of anagrams
  */ 
  public ArrayList<Map.Entry<String, Integer>> getSorted() {

    return new ArrayList<>(sortedMatches);
  }

  /**
    * Return the canonical rack in its raw form.
    * @return rawCanonical the rack
  */

  public String getRawCanonical() {

    return new String(rawCanonical);
  }

   
}
