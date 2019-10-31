

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Random;

/*
   class SolitaireBoard
   The board for Bulgarian Solitaire.  You can change what the total number of 
   cards is for the game by changing NUM_FINAL_PILES, below.  Don't change 
   CARD_TOTAL directly, because there are only some values for CARD_TOTAL that 
   result in a game that terminates. (See comments below next to named constant 
   declarations for more details on this.)
 */


public class SolitaireBoard {
   
   public static final int NUM_FINAL_PILES = 9;
   // number of piles in a final configuration
   // (note: if NUM_FINAL_PILES is 9, then CARD_TOTAL below will be 45)
   
   public static final int CARD_TOTAL = NUM_FINAL_PILES * (NUM_FINAL_PILES + 1) / 2;
   // bulgarian solitaire only terminates if CARD_TOTAL is a triangular number.
   // see: http://en.wikipedia.org/wiki/Bulgarian_solitaire for more details
   // the above formula is the closed form for 1 + 2 + 3 + . . . + NUM_FINAL_PILES

     /**
      Representation invariant:

    1. There are always CARD_TOTAL number of cards on the board
        a. The sum of all elements in the array must always equal CARD_TOTAL
    2. There cannot be negative piles
        a. No negative array elements
    3. There's no 'hole' between piles
        a. All valid piles are consecutive without intervening piles
          of size 0
    NB: #3 is just a property of our particular solitaire board

    */
   
   // <add instance variables here>
    private int[] gameBoard;
    private int [] FINAL_CONFIG;
    private static final int COUNTER_START = 1;
    private static final int RANGE_OFFSET = 1;
    private static final int PILE_OFFSET = 1;
    private int currentSize;
  
 
     /**
     Creates a solitaire board with the configuration specified in piles.
     piles has the number of cards in the first pile, then the number of cards 
     in the second pile, etc.
     PRE: piles contains a sequence of positive numbers that sum to 
          SolitaireBoard.CARD_TOTAL
   */
   public SolitaireBoard(ArrayList<Integer> piles) {

      gameBoard = new int[CARD_TOTAL];
      FINAL_CONFIG = new int[NUM_FINAL_PILES];
      populateBoard(false, piles);

      assert isValidSolitaireBoard(); 
   }
 
   
   /**
      Creates a solitaire board with a random initial configuration.
   */
   public SolitaireBoard() {
  
      gameBoard = new int[CARD_TOTAL];
      FINAL_CONFIG = new int[NUM_FINAL_PILES];
      populateBoard(true, new ArrayList<Integer>());

      assert isValidSolitaireBoard();

   }
  
  /**

      Populate gameboard with initial values. If piles are provided, use them. 
      Otherwise if random gameboard is requested, generate random piles with 
      numbers between 1 and 45, inclusive.  
  */
   private void populateBoard(boolean random, ArrayList<Integer>piles) {

      if (random) {
        int sum = 0;
        int range, randPile;
        Random generator = new Random();

        for (int i = 0; i < CARD_TOTAL; i++) {
          range = CARD_TOTAL - sum;
          randPile = generator.nextInt(range) + RANGE_OFFSET;  
          gameBoard[i] = randPile;
          currentSize++;
          sum += randPile;

          if (sum == CARD_TOTAL) {
            break;
          }
        }
      }
      else {

        for (int i = 0; i < piles.size(); i++) {
              gameBoard[i] = piles.get(i);
              currentSize++;
          }
        }
      for (int i = PILE_OFFSET; i <= NUM_FINAL_PILES; i++) {
          FINAL_CONFIG[i-PILE_OFFSET] = i;
        }
  }

    /**
      Plays one round of Bulgarian solitaire.  Updates the configuration 
      according to the rules of Bulgarian solitaire: Takes one card from each 
      pile, and puts them all together in a new pile. The old piles that are 
      left will be in the same relative order as before, 
      and the new pile will be at the end.
    */
   public void playRound() {

      for (int i = 0; i < currentSize; i++) {
        gameBoard[i]--;
      }

      if (currentSize == CARD_TOTAL) {

        gameBoard[0] = CARD_TOTAL;
        currentSize = COUNTER_START;
      }
      else {
        gameBoard[currentSize] = currentSize;
        currentSize++;
      }
      shiftPiles();
      
      assert isValidSolitaireBoard();

   }

    
  /**
      Returns true iff the current board is at the end of the game.  That is, 
      there are NUM_FINAL_PILES 
      piles that are of sizes 1, 2, 3, . . . , NUM_FINAL_PILES, in any order.

      @return true  valid solitaire board

  */
  public boolean isDone() {

      if (currentSize == NUM_FINAL_PILES) {
          int sum = 0;
          for (int i = 0; i < currentSize; i++) {
            sum += gameBoard[i];
          }
          if (sum == CARD_TOTAL && isvalidFinalConfig()) {

            assert isValidSolitaireBoard();
            return true;

          }
      }
      assert isValidSolitaireBoard();
      return false;  
   }

   
   /**
      Returns current board configuration as a string with the format of
      a space-separated list of numbers with no leading or trailing spaces.
      The numbers represent the number of cards in each non-empty pile.

      @return cleaned   a space-separated list of numbers
    */
   public String configString() {

      int[] currentState = new int[currentSize];
      int j = 0;
      for (int i = 0; i < gameBoard.length; i++) {
        if (gameBoard[i] > 0) {
          if (j < currentSize) {
            currentState[j] = gameBoard[i];
          }
          
          j++;
        }
      }
      String pileState = Arrays.toString(currentState);
      String cleaned = pileState.replace("[", "").replace("]", "").replace(",", "");

      assert isValidSolitaireBoard();
      return cleaned;
   }
   
   
   /**
      Returns true iff the solitaire board data is in a valid state
      (See representation invariant comment for more details.)
    */
   private boolean isValidSolitaireBoard() {

      int sum = 0;
      for (int i = 0; i < currentSize; i++) {
        if (gameBoard[i] < 0) {
          return false;
        }
        sum += gameBoard[i];
      }
      if (sum == CARD_TOTAL) {
          return true;
      }
      return false; 

   }

    /**
      Remove any 'holes' in the piles, i.e. 0-size piles, by downshifting all 
      array elements. Update currentSize to reflect the shift. 
      NB: We 'shift' our piles by simply overwriting any downstream  0-size 
          piles with non-0-size upstream piles. As such, the upstream piles 
          are never overwritten. This is not a problem for us since anything 
          past currentSize-1 in the array is not part of our piles. 
   */
   private void shiftPiles() {

      int j = 0;
      for (int i = 0; i < currentSize; i++) {
        if (gameBoard[i] > 0) {
          gameBoard[j] = gameBoard[i];
          j++;
        }
      }
      currentSize = j;

    assert isValidSolitaireBoard();
   }

   /**
      Return true iff our computed pile configuration conforms to a known 
      final configuration. 
   */
   private boolean isvalidFinalConfig() {

      int[] validPiles = Arrays.copyOf(gameBoard, currentSize);

      Arrays.sort(validPiles);
      if (Arrays.equals(validPiles, FINAL_CONFIG)) {
          return true;
      }
      return false;
      
     }

}