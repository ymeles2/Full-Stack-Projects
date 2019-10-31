import java.lang.Math;

public class CashReg
{
   private static final int DOLLAR_VALUE = 100;
   private static final int QUARTER_VALUE = 25;
   private static final int DIME_VALUE = 10;
   private static final int NICKEL_VALUE = 5;
   private static final int PENNY_VALUE = 1;

   private int purchase;
   private int payment;

   /**
      Constructs a cash register with no money in it.
   */
   public CashReg()
   {
      purchase = 0;
      payment = 0;
   }

   /**
      Records the purchase price of an item.
      @param amount the price of the purchased item
   */
   public void recordPurchase(double amount)
   {  
      purchase = purchase + (int)(Math.round(amount * (double)DOLLAR_VALUE));
   }
   
   /**
      Gets total of all purchases made.
   */
    public double getTotal() {
       return purchase/(double)DOLLAR_VALUE;
    }; 

   /**
      Enters the payment received from the customer.
      @param dollars the number of dollars in the payment
      @param quarters the number of quarters in the payment
      @param dimes the number of dimes in the payment
      @param nickels the number of nickels in the payment
      @param pennies the number of pennies in the payment
   */
      public void receivePayment(Change money) {
        payment = money.totalValue();
    }
   
   /**
      Computes the change due and resets the machine for the next customer.
      @return the change due to the customer
   */
      public Change giveChange() {
         int change, dollars, quarters, dimes, nickels, pennies;
         change = payment - purchase;
         dollars = change/DOLLAR_VALUE;
         change = change-dollars*DOLLAR_VALUE;
         quarters = change/QUARTER_VALUE;
         change = change - quarters*QUARTER_VALUE;
         dimes = change/DIME_VALUE;
         change = change - dimes*DIME_VALUE;
         nickels = change/NICKEL_VALUE; 
         change = change - nickels*NICKEL_VALUE;
         pennies = change;
         purchase = 0;
         payment = 0;
        return new Change(dollars, quarters, dimes, nickels, pennies); 
    }

}
