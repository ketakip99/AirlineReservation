from django.contrib import admin
from django.urls import path,include
from airline import views

urlpatterns = [
    path("", views.home, name='homepage'),
    # path("fromto/", views.fromto, name='fromto'),
    path("fromto/",include([
        path("",views.fromto, name="fromto"),
        path("flightslist/",include([
            path("",views.flightslist,name="flightslist"),
            path("details/",include([
                path("",views.details, name="details"),
                path("summary/",include([
                    path("",views.summary, name="summary"),
                    path("confirmpay/",include([
                        path("",views.confirmpay, name = "confirmpay"),
                        path("receipt/", views.receipt, name="receipt"),
                    ]))
                ])),
            ])),
        ]))
    ])),
    
    path("about/", views.about, name='about'),
    path("services/", views.services, name='services'),
    path("contact/", views.contact, name='contact'),

    
    path("cancel/", include([
        path("",views.cancel, name="cancel"),
        path("cancelnext/", views.cancelnext, name ="cancelnext")
    ])),
]