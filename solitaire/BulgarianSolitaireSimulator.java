

import java.util.ArrayList;
import java.util.Scanner;

/**
   BulgarianSolitaireSimulator simulates Bulgarian Solitaire by taking an input
   of numbers that sum to some triangular number and computing the first 
   n natural numbers that sum to the said triangular number. Users can 
   specify mode of execution as follows:

   java BulgarianSolitaireSimulator -s -u
   or 
   java BulgarianSolitaireSimulator


   u: user input provided for pile sizes
   s: allow for step-by-step game-play upon user input

   If no flags are enabled, random pile sizes are generated. Any combination 
   of flags is allowed. 

 */

public class BulgarianSolitaireSimulator {


    /**

      Simulate the game. If the u flag is provided, take user input of integers.
      If the s flag is provided, allow for step-by-step game-play. Otherwise,
      simulate a random game.

      @param args    command-line arguments containing optional flags
   */

   private static final int CARD_TOTAL = 45;
   private static final int POST_INITIALIZATION = 1;

   public static void main(String[] args) {
     
      boolean singleStep = false;
      boolean userConfig = false;
      SolitaireBoard board;

      for (int i = 0; i < args.length; i++) {
         if (args[i].equals("-u")) {
            userConfig = true;
         }
         else if (args[i].equals("-s")) {
            singleStep = true;
         }
      } 
     
      if (userConfig) {

         String prompt = new String("Please enter a space-separated list of" +
                              " positive integers followed by newline:");
         String error = new String("ERROR: Each pile must have at least one card" +
                                 " and the total number of cards must be 45");

         System.out.println("Number of total cards is 45");
         System.out.print("You will be entering the initial configuration of");
         System.out.println(" the cards (i.e., how many in each pile).");

         ArrayList<Integer> numList = getNumSeq(prompt, error);
         board = new SolitaireBoard(numList);
      }

      else {

         board = new SolitaireBoard();
      }

       simulate(board, singleStep);
         
   }      

     /**

      Simulate the game by playing rounds until we have successfully arrived 
      at the final configuration.
   */
   private static void simulate(SolitaireBoard board, boolean singleStep) {

      int i = 1;
      Scanner in = new Scanner(System.in);

      System.out.println("Initial configuration: "+board.configString());
      while (!board.isDone()) {

         if (i == POST_INITIALIZATION) {
            board.playRound();
            System.out.println("["+i+"] Current configuration: "+board.configString());
         }
         else {
            if (singleStep && i > POST_INITIALIZATION) {
               System.out.print("<Type return to continue>");
               in.nextLine();
               board.playRound();
            }
            else {
               board.playRound();
            }
            System.out.println("["+i+"] Current configuration: "+board.configString());
            
         }
         i++;
      }
      System.out.println("Done!");     
   }

   /**

      Return a sequence of integers provided by the user to be used as the initial 
      configuration of piles.
   */
   private static ArrayList<Integer> getNumSeq(String prompt, String error) {

      Scanner in = new Scanner(System.in);
      ArrayList<Integer> numList = new ArrayList<Integer>();
      
      while (true) {
         System.out.println(prompt);
         String line = in.nextLine();
         Scanner lineScanner = new Scanner(line);
         
         int newInt;
         int sum = 0;
         while (lineScanner.hasNextInt()) {
               newInt = lineScanner.nextInt();
               numList.add(newInt);
               sum += newInt;
            }

         boolean mixedInput = isMixedInput(line);
         boolean validRange = isValidRange(numList, CARD_TOTAL);
         if (sum == CARD_TOTAL && validRange && !mixedInput) {
            break;
         }
         else {
            System.out.println(error);
            numList.clear();
         }
      }
      return numList;
    }


   /**

      Return true iff user input contains a mix of integers and non-integers. 

      NB: checking for mixed input allows us to detect input types of the 
         following: 45 b; 10 10 10 10 5 a b c d; If we only consider the first 
         n consecutive integers, then the inputs is valid. However, if we consider
         the whole sequence, it's obviously not a valid configuration. 

         All other types of mixed input are handled automatically.

   */
   private static boolean isMixedInput(String line) {

      Scanner lineScanner = new Scanner(line);
      boolean mixed = false;
      int intCount = 0;
      int tokenCount = 0;

      while (lineScanner.hasNext()) {
         if (lineScanner.hasNextInt()) {
            lineScanner.nextInt();
            intCount++;
         }
         else {
            lineScanner.next();
         }
         tokenCount++; 

      }
      if (intCount != tokenCount) {

         mixed = true;
      }
         return mixed;
   }


   /**
      Return true iff user-provided sequence of numbers are within an acceptable
      range, i.e. 1 - CARD_TOTAL, inclusive.
   */
   private static boolean isValidRange(ArrayList<Integer> numList, int CARD_TOTAL) {

      for (int i = 0; i < numList.size(); i++) {

         int num = numList.get(i);
         if (num <= 0 || num > CARD_TOTAL) {
            return false;
         }

      }
      return true;
       
   }

}