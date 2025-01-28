#!/usr/bin/env python

# This is a simple web server for a training record application.
# It's your job to extend it by adding the backend functionality to support
# recording training in an SQL database. You will also need to support
# user access/session control. You should only need to extend this file.
# The client side code (html, javascript and css) is complete and does not
# require editing or detailed understanding, it serves only as a
# debugging/development aid.

# import the various libraries needed
import http.cookies as Cookie   # some cookie handling support
from http.server import BaseHTTPRequestHandler, HTTPServer # the heavy lifting of the web server
import urllib # some url parsing support
import json   # support for json encoding
import sys    # needed for agument handling
import time   # time support

import base64 # some encoding support
import sqlite3 # sql database
import random # generate random numbers
import time # needed to record when stuff happened
import datetime
from datetime import datetime

def random_digits(n):
    """This function provides a random integer with the specfied number of digits and no leading zeros."""
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return random.randint(range_start, range_end)

# The following three functions  SQL queries to the database.

def do_database_execute(op, parameter):
    """Execute an sqlite3 SQL query to database.db that does not expect a response."""
    #Such as INSERT, UPDATE and DELETE

    if parameter:
        print(op+",", parameter)

        try:
            db = sqlite3.connect('database.db')
            cursor = db.cursor()
            cursor.execute(op, parameter)
            db.commit()
        except Exception as e:
            db.rollback()
        finally:
            db.close()

    else:
        print(op)
        try:
            db = sqlite3.connect('database.db')
            cursor = db.cursor()
            cursor.execute(op)
            db.commit()
        except Exception as e:
            db.rollback()
        finally:
            db.close()

def do_database_fetchone(op, parameter):
    """Execute an sqlite3 SQL query to database.db that expects to extract a single row result. Note, it may be a null result."""

    if parameter:
        print(op, ',', parameter)
        try:
            db = sqlite3.connect('database.db')
            cursor = db.cursor()
            cursor.execute(op, parameter)
            result = cursor.fetchone()
            print(result)
            db.close()
            return result
        except Exception as e:
            print(e)
            return None

    else:
        print(op)
        try:
            db = sqlite3.connect('database.db')
            cursor = db.cursor()
            cursor.execute(op)
            result = cursor.fetchone()
            print(result)
            db.close()
            return result
        except Exception as e:
            print(e)
            return None

def do_database_fetchall(op, parameter):
    """Execute an sqlite3 SQL query to database.db that expects to extract a multi-row result. Note, it may be a null result."""

    if parameter:
        print(op, ',', parameter)
        try:
            db = sqlite3.connect('database.db')
            cursor = db.cursor()
            cursor.execute(op, parameter)
            result = cursor.fetchall()
            print(result)
            db.close()
            return result
        except Exception as e:
            print(e)
            return None

    else:
        print(op)
        try:
            db = sqlite3.connect('database.db')
            cursor = db.cursor()
            cursor.execute(op)
            result = cursor.fetchall()
            print(result)
            db.close()
            return result
        except Exception as e:
            print(e)
            return None

# The following build_ functions return the responses that the front end client understands.
# You can return a list of these.

def build_response_message(code, text):
    """This function builds a message response that displays a message
       to the user on the web page. It also returns an error code."""
    return {"type":"message","code":code, "text":text}

def build_response_skill(id,name,gained,trainer,state):
    """This function builds a summary response that contains one summary table entry."""
    return {"type":"skill","id":id,"name":name, "gained":gained,"trainer":trainer,"state":state}

def build_response_class(id, name, trainer, when, notes, size, max, action):
    """This function builds an activity response that contains the id and name of an activity type,"""
    return {"type":"class", "id":id, "name":name, "trainer":trainer, "when":when, "notes":notes, "size":size, "max":max, "action":action}

def build_response_attendee(id, name, action):
    """This function builds an activity response that contains the id and name of an activity type,"""
    return {"type":"attendee", "id":id, "name":name, "action":action}

def build_response_redirect(where):
    """This function builds the page redirection response
       It indicates which page the client should fetch.
       If this action is used, it should be the only response provided."""
    return {"type":"redirect", "where":where}

# The following handle_..._request functions are invoked by the corresponding /action?command=.. request
def handle_login_request(iuser, imagic, content):
    """A user has supplied a username and password. Check if these are
       valid and if so, create a suitable session record in the database
       with a random magic identifier that is returned.
       Return the username, magic identifier and the response action set."""
    response = []
    
    if not content:
        response.append(build_response_message(100,
                                        "There is no content passed (username, password)"))
    else:
        username_input = content.get('username')
        pwd_input = content.get('password')

        # Checking missing parameters
        # 100: Username and Password missing
        # 101: Username is missing
        # 102: Password is missing
        if username_input is None and pwd_input is None:
            response.append(build_response_message(101, "Username and Password missing"))
        elif username_input is None and not pwd_input is None:
            response.append(build_response_message(102, "Username is missing"))
        elif not username_input is None and pwd_input is None:
            response.append(build_response_message(103, "Password is missing"))

        # If input username and password exists,
        else:
            user_account = do_database_fetchone("""
                                                SELECT userid, username, password
                                                FROM users 
                                                WHERE username = ?;
                                                """,(username_input,))

            # If the user is not recognisable
            if not user_account:
                response.append(build_response_message(200, 'Username not found'))
            # Found the user
            else:
                (_, username_db, pwd_db) = user_account

                #Error 201: Password does not match
                if pwd_input != pwd_db:
                    response.append(build_response_message(201, 'Password does not match'))
                # All existing session for this user should be ended
                # replaced with a new one
                else:
                    exist_session = do_database_fetchall("""
                                                            SELECT sessionid
                                                            FROM session
                                                            WHERE userid = ?;
                                                            """, (username_db,))

                    # Session_id is auto-increment primary-key
                    iuser = username_db
                    imagic = str(random_digits(10))

                    # magic cookie shouldn't be repetitive
                    magic_many = do_database_fetchone("""
                                                    SELECT magic
                                                        FROM session
                                                        WHERE magic = ?
                                                    """, (imagic,))

                    while magic_many is not None:
                        imagic = str(random_digits(1))
                        magic_many = do_database_fetchone("""
                                                    SELECT magic
                                                        FROM session
                                                        WHERE magic = ?
                                                    """, (imagic,))
                    if exist_session:
                        # All existing session ended and replaced with a new one
                        do_database_execute("""
                                            UPDATE session SET magic = ? 
                                            WHERE userid = ?;
                                            """, (imagic, iuser))
                    # In case the session's overmade for one user, delete others retain one only
                    elif len(exist_session) > 1:
                        do_database_execute('DELETE FROM session WHERE userid = ?;', (iuser,))
                        do_database_execute("""INSERT INTO session (userid, magic)
                                            VALUES (?, ?);
                                            """, (iuser, imagic))
                    else:
                        # New session for a user
                        do_database_execute("""INSERT INTO session (userid, magic)
                                            VALUES (?, ?);
                                            """, (iuser, imagic))
                    response.append(build_response_redirect('/index.html'))
    return [iuser, imagic, response]

def handle_logout_request(iuser, imagic, parameters):
    """This code handles the selection of the logout button.
       You will need to ensure the end of the session is recorded in the database
       And that the session magic is revoked."""
    response = []

    # Look for any session made by the user
    exist_session = do_database_fetchone("""SELECT sessionid
                                         FROM session
                                         WHERE userid = ? AND magic = ?;
                                         """, (iuser, imagic))

    # If there is one, delete the session record and log out the user as expected
    if exist_session:
        do_database_execute("DELETE FROM session WHERE userid = ?;", (iuser,))
        response.append(build_response_redirect('/logout.html'))
    # Otherwise, just redirect to the login page
    else:
        response.append(build_response_redirect('/login.html'))

    return [iuser, imagic, response]

#return a set of skill responses for the logged in user
def handle_get_my_skills_request(iuser, imagic):
    """This code handles a request for a list of a users skills.
       You must return a value for all vehicle types, even when it's zero."""

    response = []

    # Check cookies for the user first
    exist_session = do_database_fetchone("""SELECT sessionid
                                         FROM session
                                         WHERE userid = ? AND magic = ?;
                                         """, (iuser, imagic))

    if exist_session:
        # Join user, skill, class, attendee and trainer tables
        # We need skillid, skill_name, class_start, trainer_id, attendee_status
        skills_list = do_database_fetchall("""
                            SELECT skill.skillid, skill.name,
                                   class.start,
                                    class.trainerid,
                                   attendee.status
                            FROM attendee
                            INNER JOIN users ON attendee.userid = users.userid
                            INNER JOIN class ON attendee.classid = class.classid
                            INNER JOIN skill ON class.skillid = skill.skillid
                            WHERE users.username = ? AND attendee.status in (0,1,2)
                        """, (iuser,))
        # the skills have to be in trainer(passed), passed, enrolled(scheduled), pending and failed order.
        # Save the reponses in those list so that later we can concatenate in wanted order.
        trainer_s = []
        passed_s = []
        scheduled_s = []
        pending_s = []
        failed_s = []
        # list that will hold the skills that the user has already passed or enrolled in
        pass_check = []
        fail_check = []

        user_id = do_database_fetchone("SELECT userid FROM users WHERE username = ?", (iuser,))[0]

        if skills_list:
            for skill in skills_list:
                skill_id, skill_name, class_start, trainer_id, attendee_status = skill

                trainer_name = do_database_fetchall("""SELECT fullname
                                                    FROM users
                                                    WHERE userid = ?;
                                                    """, (trainer_id,))
                
                trainer_ids = do_database_fetchall("""SELECT trainerid
                                                   FROM trainer
                                                   WHERE skillid = ?
                                                   """, (skill_id,))
                trainer_ids = [x[0] for x in trainer_ids]

                # When the logged-in user is the trainer of the skill
                if user_id in trainer_ids:
                    trainer_s.append(build_response_skill(skill_id,
                                                               skill_name,
                                                               class_start,
                                                               trainer_name,
                                                               "trainer"))
                # 'passed' status: 1
                elif attendee_status == 1:
                    passed_s.append(build_response_skill(skill_id,
                                                              skill_name,
                                                              class_start,
                                                              trainer_name,
                                                              "passed"))
                    pass_check.append(skill_id)
                # 'enrolled' status: 0
                # 'pending' if the start time for the class has passed.
                elif attendee_status == 0:
                    time_now = int(time.time())

                    status = "scheduled"

                    # if the start time has already passed, mark it as pending.
                    # Add it to the pass check list,
                    # so that later if the user failed this skill, it still is shown as pass
                    if time_now > class_start:
                        status = "pending"
                        pending_s.append(build_response_skill(skill_id,
                                                                   skill_name,
                                                                   class_start,
                                                                   trainer_name,
                                                                   status))
                        pass_check.append(skill_id)
                    # otherwise, mark it as scheduleed
                    else:
                        scheduled_s.append(build_response_skill(skill_id,
                                                                     skill_name,
                                                                     class_start,
                                                                     trainer_name,
                                                                     status))
                # 'failed' status: 2
                # which does not have any pass or pending for the same skill
                # check this will the pass_check list whether it holds the current looking skillid
                elif attendee_status == 2:
                    failed_s.append(build_response_skill(skill_id,
                                                              skill_name,
                                                              class_start,
                                                              trainer_name,
                                                              "failed"))
                    fail_check.append(skill_id)
                # entries 'cancelled': 3 or 'removed': 4 shouldn't be included
            # Anything that the user has failed earlier but scheduled should be shown as failed.
            clean_scheduled = [x for x in scheduled_s if x['id'] not in fail_check]
            # Check whether the user has passed the skill eventually or pending again.
            clean_failed = [x for x in failed_s if x['id'] not in pass_check]

            # ADD all the responses in the right order
            response = trainer_s + passed_s + clean_scheduled + pending_s + clean_failed
            response.append(build_response_message(0, "Skill load successful"))

    else:
        response.append(build_response_redirect('/login.html'))

    return [iuser, imagic, response]

# Return a class response for each class for which the start time and date has not passed
def handle_get_upcoming_request(iuser, imagic):
    """This code handles a request for the details of a class."""
    response = []

    # Check cookies for the user first
    exist_session = do_database_fetchone("""SELECT sessionid
                                         FROM session
                                         WHERE userid = ? AND magic = ?;
                                         """, (iuser, imagic))

    if exist_session:
        time_now = int(time.time())

        # Classes should be sent in timestamp order, start time and date has not passed
        classes_list = do_database_fetchall("""
                            SELECT class.classid,
                                    skill.name,
                                    skill.skillid,
                                    class.start,
                                    trainer.trainerid,
                                    class.max,
                                    class.note
                            FROM class
                            INNER JOIN skill ON class.skillid =  skill.skillid
                            INNER JOIN trainer ON class.trainerid = trainer.trainerid
                            WHERE class.start > ?
                            ORDER BY class.start ASC;
                        """, (time_now,))
        # If the query holds any record, that means there are classes up coming,
        if classes_list:
            user_id = do_database_fetchone("""SELECT userid
                                           FROM users
                                           WHERE username = ?
                                           """, (iuser,))[0]

            # Each class
            for class_item in classes_list:
                class_id, skill_name, skill_id, class_start, trainer_id, class_max, class_note = class_item

                # Get trainer fullname
                trainer_name = do_database_fetchone("""SELECT fullname
                                                    FROM users
                                                    WHERE userid = ?;
                                                    """, (trainer_id,))[0]

                # Get class size (number of attendees for this class)
                class_size = do_database_fetchone("""SELECT COUNT(*)
                                                  FROM attendee
                                                  WHERE classid = ? AND status = 0;
                                                  """, (class_id,))[0]

                # Get what is the status of the logged-in user for the current class
                user_class_status = do_database_fetchone("""
                                            SELECT status
                                            FROM attendee
                                            INNER JOIN users ON attendee.userid = users.userid
                                            WHERE attendee.classid = ? and users.username= ?;
                                                         """, (class_id, iuser))

                # Check whether the class has been already cancelled first.
                if class_max == 0:
                    response.append(build_response_class(class_id,
                                                        skill_name,
                                                        trainer_name,
                                                        class_start,
                                                        class_note,
                                                        class_size,
                                                        class_max, 'cancelled'))
                else:
                    # But if the user is the trainer of this class, return 'edit' option
                    if user_id == trainer_id:
                        response.append(build_response_class(class_id,
                                                            skill_name,
                                                            trainer_name,
                                                            class_start,
                                                            class_note,
                                                            class_size,
                                                            class_max, 'edit'))
                    # Otherwise,
                    else:
                        # Check whether the user has engaged any class with the same skillid,
                        # and returns their status.
                        attended_skill_class_check = do_database_fetchall("""
                        SELECT attendee.status
                        FROM attendee
                        INNER JOIN class ON attendee.classid = class.classid
                        INNER JOIN skill ON class.skillid = skill.skillid
                        INNER JOIN users ON attendee.userid = users.userid
                        WHERE users.username = ? AND skill.skillid = ? AND class.classid != ?;
                                                        """, (iuser, skill_id, class_id))
                        # Any interaction,
                        if user_class_status:
                            # If Enrolled,
                            if user_class_status[0] == 0:
                                response.append(build_response_class(class_id,
                                                                    skill_name,
                                                                    trainer_name,
                                                                    class_start,
                                                                    class_note,
                                                                    class_size,
                                                                    class_max, 'leave'))
                            # If others, removed or canceled
                            elif user_class_status[0] == 3:
                                response.append(build_response_class(class_id,
                                                                    skill_name,
                                                                    trainer_name,
                                                                    class_start,
                                                                    class_note,
                                                                    class_size,
                                                                    class_max, 'join'))
                            elif user_class_status[0] == 4:
                                response.append(build_response_class(class_id,
                                                                    skill_name,
                                                                    trainer_name,
                                                                    class_start,
                                                                    class_note,
                                                                    class_size,
                                                                    class_max, 'cancelled'))
                        # if not, never enrolled
                        else:
                            # if the user has engaged with another class with the same skillid
                            if attended_skill_class_check:
                                availability = []
                                # with another class with same skillid,
                                for attended_class in attended_skill_class_check:
                                    availability.append(attended_class[0])
                                # if the user has passed or enrolled a class with the same skillid
                                if 0 in availability or 1 in availability:
                                    response.append(build_response_class(class_id,
                                                                        skill_name,
                                                                        trainer_name,
                                                                        class_start,
                                                                        class_note,
                                                                        class_size,
                                                                        class_max, 'unavailable'))
                                # if the user has not passed or enrolled,
                                else:
                                    response.append(build_response_class(class_id,
                                                                        skill_name,
                                                                        trainer_name,
                                                                        class_start,
                                                                        class_note,
                                                                        class_size,
                                                                        class_max, 'join'))
                            # if it is the first time seeing a class with this skillid,
                            # just be allowed to join
                            else:
                                response.append(build_response_class(class_id,
                                                                    skill_name,
                                                                    trainer_name,
                                                                    class_start,
                                                                    class_note,
                                                                    class_size,
                                                                    class_max, 'join'))
        response.append(build_response_message(0, 'Upcoming classes loaded successfully'))
    else:
        response.append(build_response_redirect('/login.html'))

    return [iuser, imagic, response]

def handle_get_class_detail_request(iuser, imagic, content):
    """This code handles a request for a list of upcoming classes."""
    response = []

    # Check cookies for the user first
    exist_session = do_database_fetchone("""SELECT sessionid
                                         FROM session
                                         WHERE userid = ? AND magic = ?;
                                         """, (iuser, imagic))

    if exist_session:
        if not content:
            response.append(build_response_message(108,
                                            "There is no content passed (classid)"))
        else:
            current_class_id = content.get('id')

            current_class = do_database_fetchone("""
                                            SELECT *
                                            FROM class
                                            WHERE classid = ?
                                            """, (current_class_id,))

            if current_class_id is None:
                response.append(build_response_message(109,
                                                    'Class id is missing in the content'))
            elif not current_class:
                response.append(build_response_message(213,
                                            f"There is no such class with id:{current_class_id}"))
            else:
                trainer_id = current_class[1]
                user_id = do_database_fetchone("""SELECT userid
                                            FROM users
                                            WHERE username = ?
                                            """, (iuser,))[0]
                # If this user is not the trainer of the class,
                if trainer_id != user_id:
                    print(trainer_id, user_id)
                    response.append(build_response_message(214,
                                        'Current user is not the trainer of this class'))
                else:
                    # The componets needed to return class responses
                    class_detail = do_database_fetchone("""SELECT skill.name,
                                                            users.fullname,
                                                            class.start,
                                                            class.note,
                                                            class.max
                                                    FROM class
                                                    INNER JOIN skill ON class.skillid = skill.skillid
                                                    INNER JOIN users ON class.trainerid = users.userid
                                                    WHERE class.classid = ?;
                                                    """, (current_class_id,))
                    # No. of currently enrolled attendees in this classs
                    class_size = do_database_fetchone("""
                                                    SELECT COUNT(*)
                                                    FROM attendee
                                                    WHERE status != ? AND status != ? AND classid = ?
                                                        """, (3, 4, current_class_id))[0]
                    # If the class has been cancelled, the max will appear 0
                    if class_detail[4] == 0:
                        response.append(build_response_class(current_class_id,
                                                                class_detail[0],
                                                                class_detail[1],
                                                                class_detail[2],
                                                                class_detail[3],
                                                                class_size,
                                                                class_detail[4], 'cancelled'))
                    else:
                        response.append(build_response_class(current_class_id,
                                                                class_detail[0],
                                                                class_detail[1],
                                                                class_detail[2],
                                                                class_detail[3],
                                                                class_size,
                                                                class_detail[4], 'cancel'))
                    attendee_list = do_database_fetchall("""
                                                SELECT class.trainerid,
                                                class.start,
                                                attendee.attendeeid,
                                                users.fullname,
                                                attendee.status
                                                FROM attendee
                                                INNER JOIN class ON attendee.classid = class.classid
                                                INNER JOIN users ON attendee.userid = users.userid
                                                WHERE class.classid = ?;
                                                        """, (current_class_id,))
                    if attendee_list:
                        for attendee in attendee_list:
                            trainer_id, class_start, attendee_id, attendee_name, attendee_status = attendee

                            # If the attendee.status is 0: enrolled,
                            if attendee_status == 0:
                                # Class hasn't started yet,
                                if class_start < int(time.time()):
                                    # Trainer can remove the attendee
                                    response.append(build_response_attendee(attendee_id,
                                                                            attendee_name,
                                                                            'remove'))
                                else:
                                    # Otherwise can update (passed, failed)
                                    response.append(build_response_attendee(attendee_id,
                                                                            attendee_name,
                                                                            'update'))
                            # If the attendee.status is 1: passed,
                            elif attendee_status == 1:
                                response.append(build_response_attendee(attendee_id,
                                                                        attendee_name,
                                                                        'passed'))

                            # attendee.status is 2: failed,
                            elif attendee_status == 2:
                                response.append(build_response_attendee(attendee_id,
                                                                        attendee_name,
                                                                        'failed'))

                            # attendee.status is 3 or 4: cancelled or removed
                            elif attendee_status in [3,4]:
                                response.append(build_response_attendee(attendee_id,
                                                                        attendee_name,
                                                                        'cancelled'))   
                    response.append(build_response_message(0,
                                                "Successfully loaded class detail"))
    else:
        response.append(build_response_redirect('/login.html'))


    return [iuser, imagic, response]


def handle_join_class_request(iuser, imagic, content):
    """This code handles a request by a user to join a class."""
    response = []
     # Check cookies for the user first
    exist_session = do_database_fetchone("""SELECT sessionid
                                         FROM session
                                         WHERE userid = ? AND magic = ?;
                                         """, (iuser, imagic))

    if exist_session:
        if not content:
            response.append(build_response_message(104, "There is no content passed (classid)"))
        
        else:            
            cur_class_id = content.get('id')
            cur_class = do_database_fetchone("""
                                            SELECT *
                                            FROM class
                                            WHERE classid = ?
                                            """, (cur_class_id,))
            user_id = do_database_fetchone("""SELECT userid
                                            FROM users
                                            WHERE username = ?
                                            """, (iuser,))[0]
            if cur_class_id is None:
                response.append(build_response_message(105,"Class id is missing in the content"))
            elif not cur_class:
                response.append(build_response_message(202, f"There is no such class with id: {cur_class_id}"))
            else:
                # skill name, trainer name, class note, class start, class skill id, max num of attendee
                # For the current trying-to-join class
                skill_name, trainer_name, class_note, class_start, class_skill_id, class_max = do_database_fetchone(
                    """
                    SELECT skill.name, users.fullname, class.note,
                    class.start, class.skillid, class.max
                    FROM class
                    INNER JOIN skill ON class.skillid = skill.skillid
                    INNER JOIN users ON class.trainerid = users.userid
                    WHERE class.classid = ?;
                    """, (cur_class_id,))

                #status of the user for the class
                user_status_for_class = do_database_fetchone("""
                                        SELECT attendee.status
                                        FROM class
                                        INNER JOIN attendee ON class.classid = attendee.classid
                                        INNER JOIN users ON attendee.userid = users.userid
                                        WHERE class.classid = ? AND users.username = ?;
                                                            """, (cur_class_id, iuser))
                # Number of currently enrolled attendees for this class
                attendee_no = do_database_fetchone("""
                                        SELECT COUNT(*)
                                        FROM class
                                        INNER JOIN attendee ON class.classid = attendee.classid
                                        WHERE class.classid = ? AND attendee.status = 0;
                                                """, (cur_class_id,))
                if not attendee_no:
                    attendee_num = 0
                else:
                    attendee_num = attendee_no[0]
                other_class_same_skill = do_database_fetchall("""
                                        SELECT attendee.status
                                        FROM class
                                        INNER JOIN attendee ON class.classid = attendee.classid
                                        INNER JOIN users ON attendee.userid = users.userid
                                        WHERE class.skillid = ? AND users.username = ?;
                                            """, (class_skill_id, iuser))
                # Check the user status for this class
                # 0, enrolled
                # 4 been removed from the class
                # more than 0 space,
                # No more space
                # Check whether the class has been cancelled by the trainer
                if class_max == 0:
                        response.append(build_response_message(206,
                                                        "Class has been cancelled"))
                else:
                    if attendee_num + 1 > class_max and class_max != 0:
                        response.append(build_response_message(203, "Class is already full"))
                    else:
                        # Other class with same skill
                        if other_class_same_skill:
                            old_status = [x[0] for x in other_class_same_skill]
                            print(old_status)
                            # enrolled or passed,
                            if 0 in old_status:
                                response.append(build_response_message(207,
                        "The user has already enrolled in different class with same skill"))
                            elif 1 in old_status:
                                response.append(build_response_message(208,
                                                    "The user has already passed this skill"))
                            # failed or cancelled or removed, allowed to join
                            else:
                                # Check whether the user has already enrolled or class is unavailable
                                if user_status_for_class:
                                    if user_status_for_class[0] == 0:
                                        response.append(build_response_message(204,
                                                                        "The user already enrolled in"))
                                    elif user_status_for_class[0] ==3:
                                        do_database_execute("""UPDATE attendee
                                                        SET status = 0
                                                        WHERE userid = ? AND classid = ?
                                                        """, (user_id, cur_class_id))
                                        response.append(build_response_class(cur_class_id,
                                                                            skill_name,
                                                                            trainer_name,
                                                                            class_start,
                                                                            class_note,
                                                                            attendee_num+1,
                                                                            class_max, "leave"))
                                        response.append(build_response_message(0, 'The user successfully join the class'))
                                    elif user_status_for_class[0] == 4:
                                        response.append(build_response_message(205,
                                                                    "The class is unavailable for this user"))
                                # If there is no Interaction with the class before
                                else:
                                    do_database_execute("""INSERT INTO attendee
                                                        (userid, classid, status)
                                                        VALUES (?, ?, 0)
                                                        """, (user_id, cur_class_id))
                                    response.append(build_response_class(cur_class_id,
                                                                            skill_name,
                                                                            trainer_name,
                                                                            class_start,
                                                                            class_note,
                                                                            attendee_num+1,
                                                                            class_max, "leave"))
                                    response.append(build_response_message(0,
                                                    'The user successfully join the class'))

                        # no other class, simply allowed to join
                        else:
                            do_database_execute("""INSERT INTO attendee
                                                (userid, classid, status)
                                                VALUES (?, ?, 0)
                                                """, (user_id, cur_class_id))
                            response.append(build_response_class(cur_class_id,
                                                                    skill_name,
                                                                    trainer_name,
                                                                    class_start,
                                                                    class_note,
                                                                    attendee_num+1,
                                                                    class_max, "leave"))
                            response.append(build_response_message(0,
                                                'The user successfully join the class'))
    else:
        response.append(build_response_redirect('/login.html'))

    return [iuser, imagic, response]

def handle_leave_class_request(iuser, imagic, content):
    """This code handles a request by a user to leave a class.
    """
    response = []

    ## Add code here
    # Check cookies for the user first
    exist_session = do_database_fetchone("""SELECT sessionid
                                         FROM session
                                         WHERE userid = ? AND magic = ?;
                                         """, (iuser, imagic))

    if exist_session:
        if not content:
            response.append(build_response_message(106, "There is no content passed (classid)"))
        else:
            cur_class_id = content.get('id')
            now_time = int(time.time())

            cur_class = do_database_fetchone("""
                                            SELECT *
                                            FROM class
                                            WHERE classid = ?
                                            """, (cur_class_id,))

            if cur_class_id is None:
                response.append(build_response_message(107,"Class id is missing in the content"))
            elif not cur_class:
                response.append(build_response_message(209,
                                            f"There is no such class with id: {cur_class_id}"))
            else:
                # skill name, trainer name, class note, class start datetime, max num of attendee
                # For the current trying-to-leave class
                skill_name, trainer_name, class_note, class_start, class_max = do_database_fetchone(
                                                    """
                                            SELECT skill.name,
                                            users.fullname,
                                            class.note,
                                            class.start,
                                            class.max
                                            FROM class
                                            INNER JOIN skill ON class.skillid = skill.skillid
                                            INNER JOIN users ON class.trainerid = users.userid
                                            WHERE classid = ?;
                                                    """, (cur_class_id,))

                # status of the user for the class
                attendee_no = do_database_fetchone("""
                                                SELECT COUNT(*)
                                                FROM class
                                                INNER JOIN attendee ON class.classid = attendee.classid
                                                WHERE class.classid = ? AND attendee.status = 0;
                                                """, (cur_class_id,))
                if not attendee_no:
                    attendee_num = 0
                else:
                    attendee_num = attendee_no[0]
                #status of the user for the class
                user_status_for_class = do_database_fetchone("""
                                        SELECT attendee.status, attendee.userid
                                        FROM class
                                        INNER JOIN attendee ON class.classid = attendee.classid
                                        INNER JOIN users ON attendee.userid = users.userid
                                        WHERE class.classid = ? AND users.username = ?;
                                                    """, (cur_class_id, iuser))
                
                if user_status_for_class:
                    # Check whether the user is truly enrolled before cancelling
                    if user_status_for_class[0] == 0:
                        # Class has not started yet.
                        if class_start > now_time:
                            do_database_execute("""UPDATE attendee
                                                SET status = 3
                                                WHERE classid = ? AND userid = ?;
                                                """, (cur_class_id, user_status_for_class[1]))
                            response.append(build_response_class(cur_class_id,
                                                                skill_name,
                                                                trainer_name,
                                                                class_start,
                                                                class_note,
                                                                attendee_num-1,
                                                                class_max, 'join'))
                            response.append(build_response_message(0,
                                                        'You left the class successfully'))
                        else:
                            response.append(build_response_message(212,
                                                "Class already started, not permitted to leave"))
                    # User already cancelled or been removed
                    elif user_status_for_class[0] == 4:
                        response.append(build_response_message(211, 
                                                    'Class is already unavailable for this user'))
                    elif user_status_for_class[0] == 3:
                        response.append(build_response_message(221,
                                                            'You already left class before'))
                else:
                    response.append(build_response_message(210,
                                                           'User has never enrolled this class'))
    else:
        response.append(build_response_redirect('/login.html'))

    return [iuser, imagic, response]

def handle_cancel_class_request(iuser, imagic, content):
    """This code handles a request to cancel an entire class."""
    response = []

    exist_session = do_database_fetchone("""SELECT sessionid
                                         FROM session
                                         WHERE userid = ? AND magic = ?;
                                         """, (iuser, imagic))

    if exist_session:
        if not content:
            response.append(build_response_message(110, "There is no content passed (classid)"))
        else:
            cur_class_id = content.get('id')
            cur_class = do_database_fetchone("""
                                            SELECT *
                                            FROM class
                                            WHERE classid = ?
                                            """, (cur_class_id,))
        
            if cur_class_id is None:
                response.append(build_response_message(111, "Class id is missing in the content"))
            elif not cur_class:
                response.append(build_response_message(215,
                                            f"There is no such class with id:{cur_class_id}"))
            else: 
                class_pack = do_database_fetchone("""
                        SELECT class.trainerid, skill.name, users.fullname, class.note, class.start
                        FROM class
                        INNER JOIN users on class.trainerid = users.userid
                        INNER JOIN skill on class.skillid = skill.skillid
                        WHERE class.classid = ?;
                                        """, (cur_class_id,))
                user_id = do_database_fetchone("""SELECT userid
                                            FROM users
                                            WHERE username = ?""", (iuser,))[0]

                trainer_id, skill_name, trainer_name, class_note, class_start = class_pack
                # Check the logged-in user is the trainer
                if user_id == trainer_id:
                    now_time = int(time.time())

                    # Check the start time/date has not passed
                    if class_start > now_time:
                        attendee_list = do_database_fetchall("""
                        SELECT attendee.attendeeid, attendee.userid, users.fullname
                        FROM attendee
                        INNER JOIN users ON attendee.userid = users.userid
                        WHERE classid = ? AND status = 0
                                                            """, (cur_class_id,))

                        for attendee in attendee_list:
                            attendee_id = attendee[0]
                            user_fullname = attendee[2]

                            do_database_execute("""UPDATE attendee SET status = 3
                                                WHERE attendeeid = ?
                                                """, (attendee_id,))
                            response.append(build_response_attendee(attendee_id,
                                                                    user_fullname, 'cancelled'))
                        response.append(build_response_class(cur_class_id,
                                                                skill_name,
                                                                trainer_name,
                                                                class_start,
                                                                class_note,
                                                                0,
                                                                0, 'cancelled'))
                        do_database_execute("""UPDATE class SET max = 0
                                                WHERE classid = ?
                                                """, (cur_class_id,))
                        response.append(build_response_message(0, "Cancelled class successfully"))
                    else:
                        response.append(build_response_message(217,
                                                    'Class has already started, no can cancel'))
                else:
                    response.append(build_response_message(216,
                                                    'User is not a trainer for this class'))
    else:
        response.append(build_response_redirect('/login.html'))

    return [iuser, imagic, response]

# If the user is the trainer for the class indicated by the attendeeid
# The state should be updated to ‘passed’ or ‘failed’ respectively
# An attendee response will be required to reflect the new state
def handle_update_attendee_request(iuser, imagic, content):
    """This code handles a request to cancel a user attendance at a class by a trainer"""
    response = []

    # Check cookies for the user first
    exist_session = do_database_fetchone("""SELECT sessionid
                                         FROM session
                                         WHERE userid = ? AND magic = ?;
                                         """, (iuser, imagic))

    if exist_session:
        if not content:
            response.append(build_response_message(112,
                                    "There is no content passed (attendeeid, state)"))
        else:
            attendee_id = content.get('id')
            new_state = content.get('state')

            now_time = int(time.time())
            if attendee_id is None and new_state is None:
                response.append(build_response_message(113,
                                            "attendeeid and state aree missing in the content"))
            elif attendee_id is None:
                response.append(build_response_message(114,
                                            "attendeeid is missing in the content"))
            elif new_state is None:
                response.append(build_response_message(115,
                                            "state is missing in the content"))
            else:
                class_pack = do_database_fetchone("""
                            SELECT class.classid, class.trainerid, attendee.userid,
                                    skill.name, users.fullname,
                                    class.note, class.start, class.max
                            FROM attendee
                            INNER JOIN class on attendee.classid = class.classid
                            INNER JOIN users on class.trainerid = users.userid
                            INNER JOIN skill on class.skillid = skill.skillid
                            WHERE attendee.attendeeid = ?
                                        """, (attendee_id,))
                # If the given attendeeid is a legit attendee for this class,
                if class_pack:
                    class_id, trainer_id, attendee_userid, skill_name, trainer_name, class_note, class_start, class_max = class_pack

                    # Get the size of the class
                    attendee_no = do_database_fetchone("""
                                    SELECT COUNT(*)
                                    FROM class
                                    INNER JOIN attendee ON class.classid = attendee.classid
                                    WHERE class.classid = ?;
                                            """, (class_id,))
                    if not attendee_no:
                        attendee_num = 0
                    else:
                        attendee_num = attendee_no[0]
                    
                    user_id = do_database_fetchone("""SELECT userid
                                                FROM users
                                                WHERE username = ?
                                                """, (iuser,))[0]
                    # Check if the user is the trainer
                    if user_id == trainer_id:
                        # Check if the class has started yet
                        attendee_fullname = do_database_fetchone("""
                                            SELECT users.fullname
                                            FROM attendee
                                            INNER JOIN users ON attendee.userid = users.userid
                                            WHERE attendee.attendeeid = ?
                                                                     """, (attendee_id,))
                        if class_start > now_time:
                            # If the state is pass,
                            if new_state == 'pass':
                                do_database_execute("""UPDATE attendee SET status = 1
                                                    WHERE attendeeid = ?
                                                    """, (attendee_id,))
                                response.append(build_response_attendee(attendee_id,
                                                                        attendee_fullname,
                                                                        'passed'))
                                response.append(build_response_message(0,
                                                    f"User state successfully changed:passed"))
                            # If the state is fail,
                            elif new_state == 'fail':
                                do_database_execute("""UPDATE attendee SET status = 2
                                                    WHERE attendeeid = ?
                                                    """, (attendee_id,))
                                response.append(build_response_attendee(attendee_id,
                                                                        attendee_fullname,
                                                                        'failed'))
                                response.append(build_response_message(0,
                                                    "User state successfully changed: failed"))
                            elif new_state == 'remove':
                                response.append(build_response_message(220,
                                                            'Class has already started'))
                            
                            else:
                                response.append(build_response_message(222,
                                            f'There is no such state called:{new_state}'))
                        else:
                            # If the state is remove,
                            if new_state == 'remove': 
                                do_database_execute("""UPDATE attendee SET status = 4
                                                    WHERE attendeeid = ?
                                                    """, (attendee_id,))
                                response.append(build_response_attendee(attendee_id,
                                                                        attendee_fullname,
                                                                        'canlcelled'))
                                response.append(build_response_class(class_id,
                                                                     skill_name,
                                                                     trainer_name,
                                                                     class_start,
                                                                     class_note,
                                                                     attendee_num-1,
                                                                     class_max,
                                                                     'cancel'
                                                                     ))
                                response.append(build_response_message(0,
                                                    "User state successfully changed: removed"))
                            elif new_state in ['pass', 'fail']:
                                response.append(build_response_message(228,
                                                            'Class has not started'))
                            else:
                                response.append(build_response_message(222,
                                            f'There is no such state called:{new_state}'))
                    else:
                        response.append(build_response_message(219,
                                    'User is not the trainer for this class'))
                else:
                    response.append(build_response_message(218,
                                                    'No such attendee found'))
    else:
        response.append(build_response_redirect('/login.html'))

    return [iuser, imagic, response]

def handle_create_class_request(iuser, imagic, content):
    """This code handles a request to create a class."""

    response = []

    # Check cookies for the user first
    exist_session = do_database_fetchone("""SELECT sessionid
                                         FROM session
                                         WHERE userid = ? AND magic = ?;
                                         """, (iuser, imagic))

    if exist_session:
        if not content:
            response.append(build_response_message(116,
                            'There is no content passed (id, note, max, day, etc...)'))
        else:
            
            c_id = content.get('id')
            c_note = content.get('note')
            c_max = content.get('max')
            c_day = content.get('day')
            c_month = content.get('month')
            c_year = content.get('year')
            c_hour = content.get('hour')
            c_min = content.get('minute')

            parameter_check = [c_id, c_max, c_day, c_month, c_year, c_hour, c_min]
            if None not in parameter_check:
                # Check whether the content input is missing any input
            
                skill_check = do_database_fetchone("""SELECT name
                                                FROM skill
                                                WHERE skillid = ?
                                                """, (c_id,))
                # See whether the skill to creat does exist in advance,
                if skill_check:
                    trainer_check = do_database_fetchall("""SELECT trainerid
                                                        FROM trainer
                                                        WHERE skillid = ?
                                                        """, (c_id,))
                    trainer_check = [x[0] for x in trainer_check]
                    user_id = do_database_fetchone("""SELECT userid
                                                FROM users
                                                WHERE username = ?
                                                """, (iuser,))[0]
                    print(user_id)

                    # See if trainer is the logged in user
                    if trainer_check:
                        if user_id in trainer_check:
                            datetime_format = str(c_year) + '-' + str(c_month) + '-' + str(c_day) + ' ' + str(c_hour) + ':' + str(c_min) + ':00'
                            
                            try:
                                date_check = datetime.strptime(datetime_format,
                                                            "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                response.append(build_response_message(216,
                                                                'Not a valid date time passed'))
                            
                            else:
                                date_time_in_unix = int(date_check.timestamp())

                                if date_time_in_unix > int(time.time()):
                                    if 0 < c_max <= 10:
                                        do_database_execute("""
                                INSERT INTO class (trainerid, skillid, start, max, note)
                                VALUES (?, ?, ?, ?, ?);""",
                                                (user_id,
                                                    c_id,
                                                    date_time_in_unix,
                                                    c_max,
                                                    c_note))
                                        new_class_id = do_database_fetchone("""SELECT classid
                                                                            FROM class
                                                                            WHERE trainerid = ?
                                                                            AND skillid = ?
                                                                            AND start = ?
                                                                            AND max = ?
                                                                            AND note = ?;"""
                                                                            , (user_id,
                                                                            c_id,
                                                                            date_time_in_unix,
                                                                            c_max,
                                                                            c_note))
                                        response.append(
                                            build_response_redirect(f'/class/{new_class_id[0]}'))
                                    else:
                                        response.append(build_response_message(227,
                                                    'Class max size has to be betwwen 1 to 10'))
                                else:
                                    response.append(build_response_message(226,
                                    'Setup datetimes is in the past, give an appropriate date'))
                        else:
                            response.append(build_response_message(225,
                                                    'This user is not the trainer of this skill'))
                    else:
                        response.append(build_response_message(224,
                                            'There is no trainer for this skill'))
                
                else:
                    response.append(build_response_message(223, f'No such skill identified{c_id}'))
            else:
                response.append(build_response_message(117, 'Missing a parameter/paramters'))
    else:
        response.append(build_response_redirect('/login.html'))
    
    return [iuser, imagic, response]

# HTTPRequestHandler class
class myHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    # POST This function responds to GET requests to the web server.
    def do_POST(self):

        # The set_cookies function adds/updates two cookies returned with a webpage.
        # These identify the user who is logged in. The first parameter identifies the user
        # and the second should be used to verify the login session.
        def set_cookies(x, user, magic):
            ucookie = Cookie.SimpleCookie()
            ucookie['u_cookie'] = user
            x.send_header("Set-Cookie", ucookie.output(header='', sep=''))
            mcookie = Cookie.SimpleCookie()
            mcookie['m_cookie'] = magic
            x.send_header("Set-Cookie", mcookie.output(header='', sep=''))

        # The get_cookies function returns the values of the user and magic cookies if they exist
        # it returns empty strings if they do not.
        def get_cookies(source):
            rcookies = Cookie.SimpleCookie(source.headers.get('Cookie'))
            user = ''
            magic = ''
            for keyc, valuec in rcookies.items():
                if keyc == 'u_cookie':
                    user = valuec.value
                if keyc == 'm_cookie':
                    magic = valuec.value
            return [user, magic]

        # Fetch the cookies that arrived with the GET request
        # The identify the user session.
        user_magic = get_cookies(self)

        print(user_magic)

        # Parse the GET request to identify the file requested and the parameters
        parsed_path = urllib.parse.urlparse(self.path)

        # Decided what to do based on the file requested.

        # The special file 'action' is not a real file, it indicates an action
        # we wish the server to execute.
        if parsed_path.path == '/action':
            self.send_response(200) #respond that this is a valid page request

            # extract the content from the POST request.
            # This are passed to the handlers.
            length =  int(self.headers.get('Content-Length'))
            scontent = self.rfile.read(length).decode('ascii')
            print(scontent)
            if length > 0 :
              content = json.loads(scontent)
            else:
              content = []

            # deal with get parameters
            parameters = urllib.parse.parse_qs(parsed_path.query)

            if 'command' in parameters:
                # check if one of the parameters was 'command'
                # If it is, identify which command and call the appropriate handler function.
                # You should not need to change this code.
                if parameters['command'][0] == 'login':
                    [user, magic, response] = handle_login_request(user_magic[0], user_magic[1], content)
                    #The result of a login attempt will be to set the cookies to identify the session.
                    set_cookies(self, user, magic)
                elif parameters['command'][0] == 'logout':
                    [user, magic, response] = handle_logout_request(user_magic[0], user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'get_my_skills':
                    [user, magic, response] = handle_get_my_skills_request(user_magic[0], user_magic[1])
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')

                elif parameters['command'][0] == 'get_upcoming':
                    [user, magic, response] = handle_get_upcoming_request(user_magic[0], user_magic[1])
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'join_class':
                    [user, magic, response] = handle_join_class_request(user_magic[0], user_magic[1],content)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'leave_class':
                    [user, magic, response] = handle_leave_class_request(user_magic[0], user_magic[1],content)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')

                elif parameters['command'][0] == 'get_class':
                    [user, magic, response] = handle_get_class_detail_request(user_magic[0], user_magic[1],content)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')

                elif parameters['command'][0] == 'update_attendee':
                    [user, magic, response] = handle_update_attendee_request(user_magic[0], user_magic[1],content)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')

                elif parameters['command'][0] == 'cancel_class':
                    [user, magic, response] = handle_cancel_class_request(user_magic[0], user_magic[1],content)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')

                elif parameters['command'][0] == 'create_class':
                    [user, magic, response] = handle_create_class_request(user_magic[0], user_magic[1],content)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                else:
                    # The command was not recognised, report that to the user. This uses a special error code that is not part of the codes you will use.
                    response = []
                    response.append(build_response_message(901, 'Internal Error: Command not recognised.'))

            else:
                # There was no command present, report that to the user. This uses a special error code that is not part of the codes you will use.
                response = []
                response.append(build_response_message(902,'Internal Error: Command not found.'))

            text = json.dumps(response)
            print(text)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(text, 'utf-8'))

        else:
            # A file that does n't fit one of the patterns above was requested.
            self.send_response(404) # a file not found html response
            self.end_headers()
        return

   # GET This function responds to GET requests to the web server.
   # You should not need to change this function.
    def do_GET(self):

        # Parse the GET request to identify the file requested and the parameters
        parsed_path = urllib.parse.urlparse(self.path)

        # Decided what to do based on the file requested.

        # Return a CSS (Cascading Style Sheet) file.
        # These tell the web client how the page should appear.
        if self.path.startswith('/css'):
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('.'+self.path, 'rb') as file:
                self.wfile.write(file.read())

        # Return a Javascript file.
        # These contain code that the web client can execute.
        elif self.path.startswith('/js'):
            self.send_response(200)
            self.send_header('Content-type', 'text/js')
            self.end_headers()
            with open('.'+self.path, 'rb') as file:
                self.wfile.write(file.read())

        # A special case of '/' means return the index.html (homepage)
        # of a website
        elif parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('./pages/index.html', 'rb') as file:
                self.wfile.write(file.read())

        # Pages of the form /create/... will return the file create.html as content
        # The ... will be a class id
        elif parsed_path.path.startswith('/class/'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('./pages/class.html', 'rb') as file:
                self.wfile.write(file.read())

        # Pages of the form /create/... will return the file create.html as content
        # The ... will be a skill id
        elif parsed_path.path.startswith('/create/'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('./pages/create.html', 'rb') as file:
                self.wfile.write(file.read())

        # Return html pages.
        elif parsed_path.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('./pages'+parsed_path.path, 'rb') as file:
                self.wfile.write(file.read())
        else:
            # A file that does n't fit one of the patterns above was requested.
            self.send_response(404)
            self.end_headers()

        return

def run():
    """This is the entry point function to this code."""
    print('starting server...')
    ## You can add any extra start up code here
    # Server settings
    # When testing you should supply a command line argument in the 8081+ range

    # Changing code below this line may break the test environment. There is no good reason to do so.
    if(len(sys.argv)<2): # Check we were given both the script name and a port number
        print("Port argument not provided.")
        return
    server_address = ('127.0.0.1', int(sys.argv[1]))
    httpd = HTTPServer(server_address, myHTTPServer_RequestHandler)
    print('running server on port =',sys.argv[1],'...')
    httpd.serve_forever() # This function will not return till the server is aborted.

run()
