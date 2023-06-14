from django.db import models

class Flights(models.Model):

    dest = models.CharField(max_length=20)
    source = models.CharField(max_length=20)
    date_of_arrival = models.DateField()
    date_of_departure = models.DateField()
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    # is_departed = models.BooleanField()
    remaining_seats = models.IntegerField(default=100)
    airfare = models.DecimalField(max_digits=7, decimal_places=2)


class Passenger(models.Model):

    name = models.CharField(max_length=110)
    age = models.IntegerField()
    sex = models.CharField(max_length=20)
    phno = models.CharField(max_length=10)
    email = models.EmailField(max_length=100)
    flight_id = models.ForeignKey(Flights, on_delete=models.CASCADE)


class Payment(models.Model):

    amount = models.DecimalField(max_digits=7, decimal_places=2)
    mode = models.CharField(max_length=25)
    flight_id = models.ForeignKey(Flights, on_delete=models.CASCADE)
    passenger_id = models.ForeignKey(Passenger, on_delete=models.CASCADE)


class Books(models.Model):

    date_of_booking = models.DateField()
    flight_id = models.ForeignKey(Flights, on_delete=models.CASCADE)
    passenger_id = models.ForeignKey(Passenger, on_delete=models.CASCADE)


class MakesPayment(models.Model):

    date_of_payment = models.DateField()
    payment_id = models.ForeignKey(Payment, on_delete=models.CASCADE)
    passenger_id = models.ForeignKey(Passenger, on_delete=models.CASCADE)