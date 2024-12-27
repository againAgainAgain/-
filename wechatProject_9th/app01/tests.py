from django.test import TestCase

# Create your tests here.
import datetime

now = datetime.datetime.now()
formatted_date = now.strftime("%Y-%m-%d")
print(formatted_date)

datetime.datetime.date()

import datetime

date_str = "2021-03-15 09:15:30"
date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
print(date_obj)