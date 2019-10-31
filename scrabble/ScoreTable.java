

import java.lang.Character;

/**
    * Holds Scrabble letter points.
    * PRE: 
    * 	requested character score must be for an ASCII character in range 
    * 	[a-zA-Z]; 
    * Rep. Inv.:
    * 	getScore(a) == getScore(A)
 */
public class ScoreTable {

	/**
		* Creates an enumeration of scores, grouped by letters and their 
		* respective points. Constant names are made of letters whose Scrabble
		* point is equal to the initialization value.	
	*/
	private enum Scores {
		
		
		AEIOULNSTR(1), 
		DG(2), 
		BCMP(3), 
		FHVWY(4), 
		K(5), 
		JX(8), 
		QZ(10);

		private final int score;

		
		/**
			* Create an enum object with its score.
		*/
		Scores(int score) {
			this.score = score;
		}

		
		/**
			* Return the numerical value of an enum constant.
			* @return score the score
		*/
		private int getScore() {
			return score;
		}
		
	}

	/**
		* Returns the scrabble score/point for a given character. First, 
		* standardize the input character and enum constant names by 
		* lower-casing them. Then determine the character score by iterating 
		* over all enum values and checking if the character is in the name of 
		* one of the enum constants.  
	*/
	private static int getScore(char c) {
		
		int charScore = 0;
		for (Scores group: Scores.values()) {
			String groupName = group.toString().toLowerCase();
			if (groupName.indexOf(Character.toLowerCase(c)) >= 0)
				charScore = group.getScore();
		}
		return charScore;
	}

	/**
		* Return a subset score for a given canonical form.
		* @return total total subset/anagram score
	*/
	public static int subsetScore(CanonicalForm cf) {

		int total = 0;
		for (int i = 0; i < cf.getUnique().length(); i++) {
			total += getScore(cf.getUnique().charAt(i)) * cf.getMult()[i];
		}

		return total;
	}


}