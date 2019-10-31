
import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Scanner;


/**
 * A dictionary of all anagram sets. 
 * Note: the processing is case-sensitive; so if the dictionary has all lower
 * case words, you will likely want any string you test to have all lower case
 * letters too, and likewise if the dictionary words are all upper case.
 */

public class AnagramDictionary {
   
   private static Scanner in;
   private static HashMap<CanonicalForm, ArrayList<String>> dictionary;


   /**
    * Create an anagram dictionary from the list of words given in the file
    * indicated by fileName.  
    * PRE: The strings in the file are unique.
    * @param fileName  the name of the file to read from
    * @throws FileNotFoundException  if the file is not found
    */
   public AnagramDictionary(String fileName) throws FileNotFoundException {
    
   File inputFile = new File(fileName);
    in = new Scanner(inputFile);
    dictionary = new HashMap<CanonicalForm, ArrayList<String>>();
    buildDictionary();

   }
   

   /**
    * Get all anagrams of the given string. This method is case-sensitive.
    * E.g. "CARE" and "race" would not be recognized as anagrams.
    * @param s string to process
    * @return a list of the anagrams of s
    * 
    */
   public ArrayList<String> getAnagramsOf(String s) {

      CanonicalForm cfKey = new CanonicalForm(s);

      if (dictionary.containsKey(cfKey)) {

        return new ArrayList<>(dictionary.get(cfKey));
      }
       return new ArrayList<String>();
   }

   /**
    *
    * Build a dictionary from the dictionary file provided. Use the canonicalized
    * form of the word, where character multiplicity and order is taken into 
    * account, as key. Build the anagram set by simply appending words with matching
    * keys into the same array. 
   */
   private static void buildDictionary() {

    while (in.hasNext()) {

      String word = in.next();
      CanonicalForm cfKey = new CanonicalForm(word);

      if (dictionary.containsKey(cfKey)) {

          dictionary.get(cfKey).add(word);
      }
      else {

          ArrayList<String> anagrams = new ArrayList<String>();
          anagrams.add(word);
          dictionary.put(cfKey, anagrams);
      }
    }
    
   }
   
}
