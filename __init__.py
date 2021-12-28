from flask import Flask, render_template, request, redirect, url_for, session
import shelve
import os

import Forms
import User, Staff

app = Flask(__name__)

#Secret Key Required for sessions
app.secret_key = "session_key"

@app.route('/' , methods=["GET","POST"])
def home():
    return render_template('home.html')

@app.route('/login' , methods=["GET","POST"])
def login():
    if "user" not in session:
        login_form = Forms.CreateLoginForm(request.form)
        if request.method == 'POST' and login_form.validate():
            #.lower() for email because capitalisation is not important in emails.
            emailInput = login_form.email.data.lower()
            passwordInput = login_form.password.data
            userDict = {}
            db = shelve.open("user", "c")
            #Using Flagname = "C" because if DB doesn't exist a file will be created instead of showing an error

            try:
                if 'Users' in db:
                    userDict = db['Users']
                else:
                    db["Users"] = userDict
            except:
                print("Error in retrieving Users from user.db.")

            #Preset Variables for later codes
            #Prevents UnboundLocalError

            validemail = False #Set to True if email is in shelve
            validpassword = False #Set to True if password is matching to the one in the shelf
            validstaffemail = False #Set to True if email inputted is in the staff database
            #These will store the data that is taken out from the shelve, used for comparison with input
            passwordinshelve = ""
            emailinshelve = ""

            for key in userDict:
                #getting email stored in the shelve
                emailinshelve = userDict[key].get_email()
                #comparing the data and seeing if matched
                if emailInput == emailinshelve.lower():
                    email_key = userDict[key]
                    validemail = True #As previously mentioned, set to true if found in shelve
                    #Console Checking
                    print("Registered Email & Inputted Email: ", emailinshelve, emailInput)
                    break
                
                    #For Console
                    #Tries looking through the Staff Database to see if email inputted is inside
                
            print("Now Trying Staff Email")
            #Flagname = "c" to create if not present == Prevents any error
            staffdb = shelve.open("staff" , "c")
            try:
                if 'Users' in staffdb:
                        userDict = staffdb['Users']
                else:
                    staffdb["Users"] = userDict
            except:
                print("Error in retrieving Users from staff.db.")

            for key in userDict:
                print("Staff Email Retrieved")
                emailinshelve = userDict[key].get_email()
                if emailInput == emailinshelve.lower():
                    staff_email_key = userDict[key]
                    validstaffemail = True
                    print("STAFF -- Registered Email & Inputted Email: ", emailinshelve, emailInput)
                    staffdb.close()
                    break
                else:
                    print("Invalid Staff Email.")
                    
                
            if validemail == True:
                    passwordinshelve = email_key.get_password()
                    if passwordInput == passwordinshelve:
                        validpassword = True
                        #Console Checking
                        print("Registered Password & Inputted Password: ", passwordinshelve, passwordInput)
            
            if validstaffemail == True:
                print("Hello-New")
                passwordinshelve = staff_email_key.get_password()
                if passwordInput == passwordinshelve:
                    staffdb.close()
                    return redirect(url_for("staffapp"))
                        
            if validemail == True and validpassword == True:
                print("Successful Login")
                db.close()
                return redirect(url_for("user"))

            else:
                db.close()
                return render_template('user/guest/login.html', form=login_form, failedAttempt=True)

        else:
            return render_template('user/guest/login.html' , form=login_form)
    else:
        return redirect(url_for("home"))

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.route('/signup' , methods=["GET","POST"])
def signup():
    #if "userSession" not in session:
        signup_form = Forms.CreateSignUpForm(request.form)
        if request.method == 'POST' and signup_form.validate():
            print("Successful Running")
            #For duplicates
            #Pre determining Variables
            duplicated_email = False #Set to true if another email is already registered in the shelve
            duplicated_username = False #Set to true if another username is already registered in the shelve
            password_confirm = signup_form.password_confirm.data
            passwordInput = signup_form.password.data
            emailInput = signup_form.email.data.lower()
            usernameInput = signup_form.username.data
            
            #To determine if passwords are matched or not
            if password_confirm == passwordInput:
                    matched_pw = False
                    #Console
                    print("Matched Passwords")
            else:
                matched_pw = True
                #Console
                print("Password not matched")

            userDict = {}
            db = shelve.open("user", "c")

            try:
                if 'Users' in db:
                    userDict = db['Users']
                else:
                    db["Users"] = userDict
            except:
                print("Error in retrieving Users from user.db")
            
            for key in userDict:
                    emailinshelve = userDict[key].get_email()
                    if emailInput == emailinshelve.lower():
                        print("Registered email & inputted email:", emailinshelve, emailInput)
                        duplicated_email = True
                        print("Duplicate Email")
                        break
                    else:
                        print("Registered email & inputted email:", emailinshelve, emailInput)
                        email_duplicates = False
                        print("New Email")
            
            for key in userDict:
                    usernameinshelve = userDict[key].get_username()
                    if usernameInput == usernameinshelve:
                        print("Registered Username & inputted username:", usernameinshelve, usernameInput)
                        duplicated_username = True
                        print("Duplicated Username")
                        break
                    else:
                        print("Registered Username & inputted username:", usernameinshelve, usernameInput)
                        username_duplicates = False
                        print("New Username")
            
            if (matched_pw == False) and (duplicated_email == False) and (duplicated_username == False):
                print("Hello")
                user = User.User(usernameInput, emailInput, passwordInput)
                userDict[user.get_username()] = user
                db["Users"] = userDict
                db.close()

                session["Customer"] = emailInput
                session["userSession"] = usernameInput

                return redirect(url_for("signup2"))
            else:
                print("Hello2")
                db.close()
                return render_template('user/guest/signup.html', form=signup_form, duplicated_email=duplicated_email, duplicated_username=duplicated_username, matched_pw=matched_pw) 
        else:
            print("Hello3")
            return render_template('user/guest/signup.html',  form=signup_form)
    #else:
        #return redirect(url_for("home"))


@app.route('/signup2' , methods=["GET","POST"])
def signup2():
    if "userSession" in session:
        if "Customer" in session:
            CustEmail = session["Customer"]
        
            print(CustEmail)
            payment_form = Forms.CreateAddPaymentForm(request.form)
            if request.method == 'POST' and payment_form.validate():
                print("Running")
                CustFound = False

                card_name = payment_form.card_name.data
                card_num = payment_form.card_no.data
                card_expiry = str(payment_form.card_expiry.data)
                card_cvv = payment_form.card_CVV.data

                #Splitting because card expiry dont have days
                year = card_expiry[:4]
                print(year)
                month = card_expiry[5:7] # to get the month from the date format "YYYY-MM-DD"
                card_expiry = "%s / %s " %(month, year)

                users_dict = {}
                db = shelve.open("user", "c")
                try:
                    if 'Users' in db:
                        users_dict = db['Users']
                    else:
                        session.clear()
                        return redirect(url_for("home"))
                except:
                    print("Error in retrieving Users from user.db")
                
                for key in users_dict:
                    print("retrieving")
                    emailinshelve = users_dict[key].get_email()
                    if CustEmail == emailinshelve:
                        customerkey = users_dict[key]
                        CustFound = True
                        break

                if CustFound == False:
                    session.clear()
                    return redirect(url_for("home"))

                customerkey.set_card_name(card_name)
                customerkey.set_card_no(card_num)
                customerkey.set_card_expiry(card_expiry)
                customerkey.set_card_cvv(card_cvv)

                db['Users'] = users_dict
                print("Payment added")

                db.close()
                return redirect(url_for("signup3"))
            else:
                return render_template('user/guest/signup2.html', form=payment_form)
        else:
            return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))


@app.route('/signup3' , methods=["GET","POST"])
def signup3():
    return render_template('user/guest/signup3.html')

@app.route('/signupC' , methods=["GET","POST"])
def signupC():
    return render_template('user/guest/signupcomplete.html')

@app.route('/user' , methods=["GET","POST"])
def user():
    return render_template('user/loggedin/useraccount.html')

@app.route('/infoedit' , methods=["GET","POST"])
def userinfo():
    return render_template('user/loggedin/user_info_edit.html')

@app.route('/pwedit' , methods=["GET","POST"])
def userpw():
    return render_template('user/loggedin/user_password_edit.html')

@app.route('/useraddress' , methods=["GET","POST"])
def useraddress():
    return render_template('user/loggedin/user_address.html')

@app.route('/usercard' , methods=["GET","POST"])
def usercard():
    return render_template('user/loggedin/user_cardinfo.html')

@app.route('/staffapp' , methods=["GET","POST"])
def staffapp():
    return render_template('user/staff/staffappoint.html')

@app.route('/stafffeed' , methods=["GET","POST"])
def stafffeed():
    return render_template('user/staff/stafffeedback.html')

@app.route('/staffinvent' , methods=["GET","POST"])
def staffinvent():
    return render_template('user/staff/staffinventory.html')

@app.route('/stafflist' , methods=["GET","POST"])
def stafflist():
    staff_dict = {}
    db = shelve.open('staff', 'c')
    try:
        if 'Users' in db:
            staff_dict = db['Users']
        else:
            db["Users"] = staff_dict
    except:
        print("Error in retrieving User from staff.db")

    db.close()

    #Displaying the appending data into the stafflist so that it can be used to display data on the site
    staff_list = []
    for key in staff_dict:
        staff = staff_dict.get(key)
        staff_list.append(staff)


    return render_template('user/staff/stafflist.html', count=len(staff_list), staff_list=staff_list)

@app.route('/staffprod' , methods=["GET","POST"])
def staffprod():
    return render_template('user/staff/staffproduct.html')


@app.route('/staffupdate/<int:id>/', methods=['GET', 'POST'])
def staffupdate(id):
    update_staff = Forms.CreateStaffMemberForm(request.form)
    if request.method == 'POST' and update_staff.validate():
        users_dict = {}
        db = shelve.open('staff', 'c')
        try:
            if 'Users' in db:
                users_dict = db['Users']
            else:
                db["Users"] = users_dict
        except:
            print("Error in retrieving Users from staff.db")

        #key is the id, so it will edit the data of the staff member and its corresponding key
        user = users_dict.get(id)
        #using accessor methods to update data
        user.set_username(update_staff.staff_name.data)
        user.set_email(update_staff.staff_email.data)

        db['Users'] = users_dict
        db.close()

        return redirect(url_for('stafflist'))

    else:
        users_dict = {}
        db = shelve.open('staff', 'r')
        try:
            if 'Users' in db:
                users_dict = db['Users']
            else:
                db["Users"] = users_dict
        except:
            print("Error in retrieving Users from staff.db")
        db.close()

        user = users_dict.get(id)
        update_staff.staff_name.data = user.get_username()
        update_staff.staff_email.data = user.get_email()

        return render_template('user/staff/staffupdate.html', form=update_staff)


@app.route('/staffadd' , methods=["GET","POST"])
def staffadd():
    staff_form = Forms.CreateStaffMemberForm(request.form)
    if request.method == 'POST' and staff_form.validate():
        print("Successful Running")
        duplicated_email = False
        duplicated_username = False
        emailInput = staff_form.staff_email.data.lower()
        nameInput = staff_form.staff_name.data
        userDict = {}
        db = shelve.open("staff", "c")
        
        try:
            if 'Users' in db:
                userDict = db['Users']
            else:
                db["Users"] = userDict
        except:
            print("Error in retrieving Users from staff.db")

        for key in userDict:
            emailinshelve = userDict[key].get_email()
            if emailInput == emailinshelve.lower():
                print("Registered email & inputted email:", emailinshelve, emailInput)
                duplicated_email = True
                print("Duplicate Email")
                break
            else:
                print("Registered email & inputted email:", emailinshelve, emailInput)
                email_duplicates = False
                print("New Email")
        
        for key in userDict:
            usernameinshelve = userDict[key].get_username()
            if nameInput == usernameinshelve:
                print("Registered Username & inputted username:", usernameinshelve, nameInput)
                duplicated_username = True
                print("Duplicated Username")
                break
            else:
                print("Registered Username & inputted username:", usernameinshelve, nameInput)
                username_duplicates = False
                print("New Username")

        if(duplicated_email == False) and (duplicated_username == False):
            print("Hello")
            user = Staff.Staff(nameInput, emailInput, 'Staff1234')
            for key in userDict:
                #To assign Staff ID, ensure that it is persistent and is accurate to the list
                staffidshelve = userDict[key].get_staff_id()
                if user.get_staff_id() == staffidshelve or user.get_staff_id() < staffidshelve:
                    print(str(user.get_staff_id()), str(userDict[key].get_staff_id()))
                    user.set_staff_id(user.get_staff_id() + 1)
                    print(str(user.get_staff_id()) + "Hello1")
                else:
                    print("Hello-olleH")
                    
            userDict[user.get_staff_id()] = user
            db["Users"] = userDict
            db.close()
            return redirect(url_for("stafflist"))
        else:
            print("Hello2")
            db.close()
            return render_template('user/staff/staffadd.html', form=staff_form, duplicated_email=duplicated_email, duplicated_username=duplicated_username) 
    else:
        print("Hello3")
        return render_template('user/staff/staffadd.html',  form=staff_form)


@app.route('/deleteUser/<int:id>', methods=["GET", 'POST'])
def deleteStaff(id):
    users_dict = {}
    db = shelve.open('staff', 'w')
    try:
        if 'Users' in db:
            users_dict = db['Users']
        else:
            db["Users"] = users_dict
    except:
        print("Error in retrieving Users from staff.db")

    users_dict.pop(id)

    db['Users'] = users_dict
    db.close()

    return redirect(url_for('stafflist'))


@app.route('/staffaccountlist' , methods=["GET","POST"])
def staffaccountlist():
    return render_template('user/staff/staffaccountlist.html')

if __name__ == '__main__':
    app.run(debug=True)
