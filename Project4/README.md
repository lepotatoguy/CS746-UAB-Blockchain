CS6/746 - Blockchain

Project 4 Readme. 

Group Members:

1. Soomin Im - soomin@uab.edu
2. Kaine Alexander Hines - kaine@uab.edu
3. Rajendra Mohan Navuluri - rnavulur@uab.edu
4. Joyanta Jyoti Mondal - jmondal@uab.edu
5. Alexus Brown - abrown43@uab.edu

Instructions:

1. Initially, you need to run wallet.py.
2. You will sign-in with your name and password.
3. You will see these options from below. 
   0. Delete all directories
   1. Create a new wallet
   2. Check a balance
   3. Create a transaction
   4. Send transations to a Miner
   5. Create a block
   6. Exit
4. Option 1, 2, 3, 4, 5, and 6 are self explanatory. Please just provide what it is asking. 
5. Just before making a block, please make sure there are atleast 4 pending transaction(s).

To test, first of all, copy this folder into 2-3, to act as 2-3 different peers. 
Then from node.py, change the port numbers and update the peers accordingly (line 7-8). 
Then run all of the wallet.py from different terminals. Then option 4 and then option 2, to work as a listener (for all the peers expect one). 
The sender one will go for Option 4 and then option 1. And then option 5. These will work to send the transactions and the block. 
To test, from the sender part, first do some tx (option 3), then option 4 and lastly option 5. 