from django.shortcuts import render,HttpResponse
from django.db import connection,transaction
from datetime import date
from django.utils import timezone

# Create your views here.

def home(request):
    return render(request, 'home.html')

def fromto(request):
    cursor = connection.cursor()

    cursor.execute(f"""select distinct(source) from airline_flights;""")
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    source = [dict(zip(columns, row)) for row in rows]

    cursor.execute(f"""select distinct(dest) from airline_flights;""")
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    dest = [dict(zip(columns, row)) for row in rows]

    context = {
        'source': source,
        'dest': dest
    }
    return render(request,'fromto.html',context)

def details(request):
    flight = request.POST['flightid']
    print(flight)
    context = {
        'flightid':flight
    }
    return render(request,'detailsform.html',context)



def about(request):
    return render(request,'about.html')


def services(request):
    cursor = connection.cursor()
    cursor.execute("""select count(id) from airline_flights;""")
    flights = cursor.fetchone()
    flights = flights[0]

    cursor.execute("""select count(id) from airline_passenger;""")
    passengers = cursor.fetchone()
    passengers = passengers[0]

    cursor.execute("""select count(distinct dest) from airline_flights;""")
    dests = cursor.fetchone()
    dests = dests[0]

    cursor.execute("""select min(airfare) from airline_flights;""")
    minfare = cursor.fetchone()
    minfare = minfare[0]

    cursor.execute("""select max(airfare) from airline_flights;""")
    maxfare = cursor.fetchone()
    maxfare = maxfare[0]

    cursor.execute("""select avg(airfare) from airline_flights;""")
    avgfare = cursor.fetchone()
    avgfare = avgfare[0]

    context = {
        'flights': flights,
        'passengers': passengers,
        'dests': dests,
        'minfare': minfare,
        'maxfare': maxfare,
        'avgfare': avgfare
    }
    return render(request,'services.html',context)


def contact(request):
    return render(request, 'contact.html')


def cancel(request):
    return render(request,'cancelform.html')

def cancelnext(request):

    flightid = request.POST['flightid']
    passid = request.POST['passid']
    paymentid = request.POST['paymentid']

    cursor = connection.cursor()
    cursor.execute(f"""select * from airline_makespayment where passenger_id_id = {passid} and payment_id_id = {paymentid};""")
    rowcount1 = cursor.rowcount

    if(rowcount1 == 0):
        message = 'Please enter matching paymentid and passengerid'
        context = {
            'message': message
        }
        return render(request,'error.html',context)
    
    cursor.execute(f"""select * from airline_books where passenger_id_id = {passid} and flight_id_id = {flightid};""")
    rowcount2 = cursor.rowcount

    if(rowcount2 == 0):
        message = 'Please enter matching flightid and passengerid'
        context = {
            'message': message
        }
        return render(request,'error.html',context)
    
    cursor.execute(f"""delete from airline_makespayment where payment_id_id = {paymentid} and passenger_id_id = {passid};""")
    cursor.execute(f"""delete from airline_payment where id = {paymentid};""")
    cursor.execute(f"""delete from airline_books where flight_id_id = {flightid} and passenger_id_id = {passid};""")
    cursor.execute(f"""delete from airline_passenger where id = {passid};""")
    cursor.execute(f"""update airline_flights set remaining_seats = (remaining_seats + 1) where id = {flightid};""")

    return render(request,'cancelnext.html')

def flightslist(request):
    try:
        src = request.POST['from']
        dest = request.POST['to']
        dept_date = request.POST['departure_date']

        if src == dest:
            context = {
                'message': "The destination cannot be same to where you already are!"
            }
            return render(request, 'error.html', context)
    
        print(src,dest)
        cursor = connection.cursor()
        # timediff(now(), departure_time) >= 0
        cursor.execute(f"""select * from airline_flights where source = '{src}' and dest = '{dest}' and date_of_departure = '{dept_date}' and timestamp(date_of_departure,departure_time) > now();""")
        rowcount = cursor.rowcount
        if(rowcount == 0):
            context = {
                'message': "Flights are not available!"
            }
            return render(request, 'error.html', context)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns,row)) for row in rows]

        cursor.execute(f"""select time_format(timediff(arrival_time,departure_time), '%H:%i') as time from airline_flights where id = (select id from airline_flights where source = '{src}' and dest = '{dest}' limit 1);""")
        time = cursor.fetchone()
        time = time[0]

        print(data)
        context = {
            'src': src,
            'dest': dest,
            'dept_date': dept_date,
            # 'rows':mylist,
            'time': time,
            'data':data
        }
        return render(request,'flightslist.html',context)
    except:
        context = {
            'message': "Please enter all the fields correctly!"
        }
        return render(request, 'error.html',context)



def summary(request):
    try:
        flightid = request.POST['flightid']
        name = request.POST['fullName']
        email = request.POST['emailAddress']
        phone = request.POST['PhNo']
        gender = request.POST['gender']
        dob = request.POST['DOB']
        print(name,email,phone,gender)
        print(flightid)
        if(len(name) > 110):
            context = {
                'message': "Name cannot exceed 110 characters!"
            }
            return render(request, 'error.html', context)
        
        if(len(phone) > 10):
            context = {
                'message': "Enter correct mobile number!"
            }
            return render(request, 'error.html', context)
        

        cursor = connection.cursor()

        cursor.execute(f"""select timestampdiff(Year, '{dob}', curdate()) as age_in_years from airline_flights limit 1;""")
        age = cursor.fetchone()
        age = age[0]

        if(age < 15):
            context = {
                'message': "You must be at least 15 years of age to book a flight on Swish Airlines!"
            }
            return render(request, 'error.html', context)

        cursor.execute(f"""insert into airline_passenger(name,sex,phno,email,flight_id_id,age) values ('{name}','{gender}','{phone}','{email}',{flightid},{age});""")

        cursor.execute(f"""update airline_flights set remaining_seats = (remaining_seats-1) where id = {flightid};""")

        cursor.execute("""select max(id) from airline_passenger;""")
        passid = cursor.fetchone()
        passid = passid[0]
        print(passid)
        print(type(passid))

        cursor.execute(f"""select * from airline_passenger where id = '{passid}' ;""")
        result = cursor.fetchone()
        columns = [col[0] for col in cursor.description]
        # data = [dict(zip(columns,row)) for row in result]
        passenger = [dict(zip(columns,result))]
        passenger = passenger[0]

        cursor.execute(f"""select * from airline_flights where id = '{flightid}'""")
        result=cursor.fetchone()
        print(result)
        columns = [col[0] for col in cursor.description]
        flight = [dict(zip(columns,result))]
        flight = flight[0]

        today = date.today()

        cursor.execute(f"""insert into airline_books(date_of_booking,flight_id_id,passenger_id_id) values('{today}',{flightid},{passid});""")

        context = {
            'flight': flight,
            'passenger': passenger,
            'today': today
        }

        print(passenger)
    
        return render(request,'summary.html',context)
    except:
        context = {
            'message': "Enter all the fields correctly!"
        }
        return render(request, 'error.html', context)


def confirmpay(request):
    flightid = request.POST['flightid']
    passid = request.POST['passid']
    context = {
        'flightid': flightid,
        'passid': passid
    }
    return render(request, 'confirmpay.html', context)


def receipt(request):
    flightid = request.POST['flightid']
    passid = request.POST['passid']
    mode_of_payment = request.POST['mode']

    cursor = connection.cursor()
    cursor.execute(f"""select airfare from airline_flights where id = {flightid};""")
    airfare = cursor.fetchone()
    airfare = airfare[0]

    cursor.execute(f"""insert into airline_payment(amount,mode,flight_id_id,passenger_id_id) values({airfare},'{mode_of_payment}',{flightid},{passid});""")

    cursor.execute("""select max(id) from airline_payment;""")
    paymentid = cursor.fetchone()
    paymentid = paymentid[0]

    cursor.execute(f"""insert into airline_makespayment(date_of_payment,payment_id_id,passenger_id_id) values(curdate(), {paymentid}, {passid});""")

    cursor.execute(f"""select date_of_payment from airline_makespayment where payment_id_id = {paymentid};""")
    date_of_payment = cursor.fetchone()
    date_of_payment = date_of_payment[0]

    cursor.execute(f"""select * from airline_passenger where id = '{passid}' ;""")
    result = cursor.fetchone()
    columns = [col[0] for col in cursor.description]
    # data = [dict(zip(columns,row)) for row in result]
    passenger = [dict(zip(columns,result))]
    passenger = passenger[0]

    cursor.execute(f"""select * from airline_flights where id = '{flightid}'""")
    result=cursor.fetchone()
    print(result)
    columns = [col[0] for col in cursor.description]
    flight = [dict(zip(columns,result))]
    flight = flight[0]

    context = {
        'flight': flight,
        'passenger': passenger,
        'paymentid': paymentid,
        'date_of_payment': date_of_payment
    }

    return render(request, 'receipt.html', context)