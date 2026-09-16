import frappe
from frappe import init, connect

init(site="site1.localhost") # Or whatever the site name is. I need to know the site name. Wait, the docker container uses what site?
