import os
import time

import numpy as np
import cv2

import getpass
import pyperclip

class Stego:
    def __init__(self):
        self.directory = os.path.dirname(os.path.abspath(__file__))
        self.fileTypes = ('.jpg', '.jpeg', '.png') #Add additional support if possible
                                                   #Would be interesting to work with gifs

    #==================================================================

    #Loops through functionality options and redirects to another function.
    #   ---Takes user input---

    #Improvements:
    #   Add further functionality
    def menuLoop(self):
        inp = 0

        while inp != 9:
            #Clear the terminal for better readability
            if os.name == 'nt':
                os.system('cls')

            print("(1) Retrieve a Password")
            print("(2) Embed a Password")
            print("(3) Edit a Password")
            print("(4) Remove a Password")
            print("(9) Exit")
            inp = input()
            print()
            
            #Prevent typecasting errors
            try:
                inp = int(inp)
            except:
                inp = 0

            #Redirect the user to different modules
            if inp == 1:
                f = self.chooseFile()
                if f:
                    self.getPass(f, True)
                    print("Password is now on clipboard! Press Enter to Return to Menu.")
                    a = input()
            elif inp == 2:
                plainPass = self.takePass()
                parts = self.getFile()
                if len(parts) == 3:
                    im, name, newName = parts
                    self.embed(plainPass, im, name, newName)
            elif inp == 3:
                f = self.chooseFile()
                self.editPassword(f)
            elif inp == 4:
                f = self.chooseFile()
                self.removePass(f)

            elif inp == 9:
                exit()

    #==================================================================

    #Allows the user to choose a file (Inside Images Folder)
    #   ---Takes user input---

    #RETURNS:   f <- The directory of the user's chosen file.
    def chooseFile(self):
        d = self.directory+"\\Images\\"#Escape the backslashes
        images = [f for f in os.listdir(d) if f.lower().endswith(self.fileTypes)]
        
        if len(images) < 1:
            print("No files found! Press Enter to Return to Menu")
            a = input()
            return

        #Print file options
        ans = -1
        f = None
        while not f:
            for i in range(len(images)):
                print("("+str(i+1)+") "+images[i])
            print("(x) Cancel")
            ans = input()
            print()

            if ans == "x":
                return
            else:
                try:
                    ans = int(ans)
                    f = images[ans-1]
                except:
                    ans = 0
            
        return f

    #Retrives the password associated with a file
    #   ---No user input---

    #INPUTS:    f <- The directory of the user's chosen file.
    #           mode <- 0 to return, 1 to copy to clipboard.
    #RETURNS:   recovered <- The password, either to clipboard or returned directly.
    def getPass(self, f, mode):
        d = self.directory+"\\Images\\"#Escape the backslashes

        #Read in image and convert
        im = cv2.imread(d+f)
        flatIm = im.flatten()
        
        #Retrieve Password length
        pLen = ""
        #for i in range(32):
        #    pLen += str(flatIm[i] & 1)

        lsb_values = flatIm[:32] & 1
        pLen += ''.join(map(str, lsb_values))

        #Retrieve the actual password
        binPass = [int(x) for x in flatIm[32:32+int(pLen, 2)]]
        plainPass = ""
        for val in binPass:
            plainPass += str(val & 1)

        #Convert String into bytes, then ints
        passBytes = [plainPass[i:i+8] for i in range(0, len(plainPass), 8)]
        passInts = [int(b, 2) for b in passBytes]

        #Decode back into ascii
        recovered = bytes(passInts).decode('utf-8')
        #print(recovered)

        if mode:
            #Add to clipboard so as not to display on screen
            pyperclip.copy(recovered)
        else:
            return recovered

    #==================================================================

    #Uses getpass to securely get the user's password, and confirms it.
    #   ---Takes user input---

    #RETURNS:    The user's password, in plaintext.
    def takePass(self):
        #Use getpass to take the user's password without it being output to the screen
        plainPass, pass2 = 0, 1
        while plainPass != pass2:
            plainPass = getpass.getpass("Enter your password")
            pass2 = getpass.getpass("Please confirm your password")
            print()
            if plainPass != pass2:
                print("Please try again, passwords did not match.")
                print()
        return plainPass

    #Get the user's chosen file (Outside Images Folder)
    #   ---Takes user input---

    #RETURNS:   im <- The image data, as an array.
    #           images[0] <- The chosen base Image.
    #           newName <- The name the new file should be created under.

    #Improvements:
    #   Add menu for user to choose image
    def getFile(self):
        #CHOICE: Do I want the user to prompt for an image, or use an image in the directory by assumption?
        #For now just take image from directory
        images = [f for f in os.listdir(self.directory) if f.lower().endswith(self.fileTypes)]
        
        #Check number of images found
        if len(images) < 1:
            print("No Image found")
            return []
        else:
            #Just open the first
            im = cv2.imread(images[0])

            newName = input("Please Enter A File Name (No Extension)")
            
            #Redirect to actually embed the password
            return [im, images[0], newName]
            
    #Helper function to find the binary data, from the password
    #   ---No user input---

    #INPUTS:    pas <- The user's chosen password, in plaintext.
    #RETURNS:   fullBits <- The binary data, with length
    def help_getBinary(self, pas):
        #Convert into binary, and left pad with 0s.
        binString = list(map(lambda x: f"{x:08b}", bytearray(pas, 'utf-8')))
        numBits = sum(len(x) for x in binString)

        #print("Contents of binString:", binString)
        
        #Create binary representation of data count, add it to data
        dataCount = f"{numBits:032b}"
        fullBits = [int(x) for x in dataCount + "".join(binString)]
        return fullBits
    
    #Perform the embedding
    #   ---No user input---

    #INPUTS:    pas <- The user's chosen password, in plaintext.
    #           im <- The image data, as an array.
    #           imName <- The chosen base Image.
    #           newName <- The name the new file should be created under.

    #Improvements:
    #   Add additional embedding algorithms
    def embed(self, pas, im, imName, newName):
        #Get binary data
        fullBits = self.help_getBinary(pas)

        #Flatten image data, and convert into binary strings
        shape = im.shape
        flatIm = im.flatten()

        #Embed
        fullBits = np.array(fullBits)

        # Perform the vectorized operation
        flatIm[:len(fullBits)] = (flatIm[:len(fullBits)] & 0xFE) | fullBits
        
        newIm = flatIm.reshape(shape)
        
        #Save image into image folder
        ext = "."+imName.split(".")[1]
        cv2.imwrite("Images\\"+newName+ext, newIm)

        print("Image Saved! Press Enter to Return To Menu")
        a = input()

    #==================================================================

    #Take a new password, to overwrite the old.
    #   ---Takes user input---

    #INPUTS:    f <- The user's chosen file.

    #Improvements:
    #   Remove old password data when writing
    def editPassword(self, f):
        pas = self.getPass(f, False)#Return password
        
        userPass = "one"
        while userPass != pas and userPass != "":
            userPass = getpass.getpass("Please enter the password, press Enter to exit.")
        if userPass == "":
            return

        #Take new password
        newPass = self.takePass()

        #Embed the new password in the same file, to replace it.
        im = cv2.imread(self.directory+"\\Images\\"+f)

        #Scramble the old password data
        oldBin = self.help_getBinary(pas)
        shape = im.shape
        flatIm = im.flatten()
        for i in range(len(oldBin)):
            flatIm[i] = (flatIm[i] & 0xFE) | oldBin[i]
        scrambledIm = flatIm.reshape(shape)

        self.embed(newPass, scrambledIm, f, f.split(".")[0])

    #==================================================================

    #Check the user knows the password, then delete
    #   ---Takes user input---

    #INPUTS:    f <- The user's chosen file.
    def removePass(self, f):
        pas = self.getPass(f, False)#Return password
        
        userPass = "one"
        while userPass != pas and userPass != "":
            userPass = getpass.getpass("Please enter the password, press Enter to exit.")
        if userPass == "":
            return
        
        #Delete file
        d = self.directory+"\\Images\\"
        os.remove(d+f)
        a = input("File removed, press Enter to return to menu.")

    #==================================================================

def __main__():
    s = Stego()
    s.menuLoop()

if __name__ == "__main__":
    __main__()