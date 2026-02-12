import random
import time

# Slot symbols
symbols = ["🍒", "🍋", "🍊", "⭐", "💎", "7️⃣"]

# Starting balance
balance = 100

def spin_reels():
    return [random.choice(symbols) for _ in range(3)]

def calculate_payout(reels, bet):
    # Three of a kind
    if reels[0] == reels[1] == reels[2]:
        if reels[0] == "7️⃣":
            return bet * 10
        elif reels[0] == "💎":
            return bet * 7
        else:
            return bet * 5

    # Two of a kind
    if reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
        return bet * 2

    return 0

def main():
    global balance
    print("🎰 Welcome to Python Slots! 🎰")
    
    while balance > 0:
        print(f"\nCurrent Balance: ${balance}")
        
        try:
            bet = int(input("Enter your bet (or 0 to quit): "))
        except ValueError:
            print("Please enter a valid number.")
            continue
        
        if bet == 0:
            print("Thanks for playing!")
            break
        
        if bet > balance or bet <= 0:
            print("Invalid bet amount.")
            continue
        
        balance -= bet
        
        print("Spinning...", end="", flush=True)
        time.sleep(1)
        
        reels = spin_reels()
        print("\r" + " | ".join(reels))
        
        winnings = calculate_payout(reels, bet)
        
        if winnings > 0:
            print(f"🎉 You won ${winnings}!")
            balance += winnings
        else:
            print("😢 No win this time.")
    
    if balance <= 0:
        print("💀 You're out of money!")

if __name__ == "__main__":
    main()