from flask import Flask, request, render_template, redirect, url_for,session,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_,or_
from flask_login import LoginManager, login_user, UserMixin, logout_user, login_required, current_user
from models import db, User, Service, ServiceRequest
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize the database
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template('index4.html')


@app.route('/customer-login', methods=['GET','POST'])
def customer_login():
    if request.method == 'POST':
        email=request.form['email']
        password=request.form['password']
        user = User.query.filter_by(username=email).first()
        if user and user.password == password:
            login_user(user)
            if user.role == "professional":
                user_services = Service.query.filter_by(proname=current_user.name).all()
                for service in user_services:
                    service_id=service.id
                return redirect(url_for("professional_dashboard",service_id=service_id))
            elif user.role == "customer":
                return redirect(url_for("customer_home"))
            
            elif user.role == "admin":
                return redirect(url_for("admin_dashboard"))
        else:
            return "Invalid credentials"        
    return render_template("customerlogin.html")


@app.route('/customer-register',methods=['GET','POST'])
def customer_register():
    if request.method == 'POST':
        fullname = request.form['name']
        emailid = request.form['email']
        password = request.form['password']
        address = request.form['address']
        pincode= request.form['pincode']
        phone=request.form['phone']

        new_user = User(username=emailid, password=password,name=fullname, pincode=pincode,phone=phone, address=address, role='customer')
        db.session.add(new_user)
        db.session.commit()
        return redirect ('/customer-login')
    return render_template('customerregister.html')


@app.route('/proregister',methods=['GET','POST'])
def proregister():
    if request.method == 'POST':
        fullname = request.form['name']
        emailid = request.form['email']
        password = request.form['password']
        servicename= request.form['Servicename']
        price=request.form['price']
        time=request.form['time']
        description=request.form['description']
        experience= request.form['experience']
        address = request.form['address']
        pincode= request.form['pincode']
        phone=request.form['phone']
        rating=4.5

        new_user = User(username=emailid, password=password, role='professional',name=fullname, phone=phone, rating=rating, experience=experience,address=address,pincode=pincode)
        new_service=Service(name=servicename,proname=fullname,prophone=phone,price=price,time_required=time,description=description)
        db.session.add(new_user)
        db.session.add(new_service)
        db.session.commit()
        return redirect(url_for('customer_login'))
    return render_template('proregister.html',)



#DASHBOARDS#
@app.route('/customer')
@login_required
def customer_home():
    if current_user.role != "customer":
        return redirect(url_for("customer_login"))
    service_requests = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
    return render_template("customer_home.html",service_requests=service_requests)

@app.route('/customer/dashboard')
@login_required
def customer_dashboard():

    if current_user.role != "customer":
        return redirect(url_for("customer_login"))
    userr=User.query.all()
    services = Service.query.all()
    service_requests = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
    return render_template("customer_dashboard.html", services=services, service_requests=service_requests, userr=userr, user=current_user)

@app.route("/customer/request_service/<int:service_id>")
@login_required
def request_service(service_id):
    if current_user.role != "customer":
        return redirect(url_for("customer_login"))

    new_request = ServiceRequest(
        service_id=service_id,
        customer_id=current_user.id,
        service_status="requested"
        )
    db.session.add(new_request)
    db.session.commit()
    return redirect(url_for("customer_dashboard"))


@app.route("/customer/rating/<int:request_id>/<int:service_id>", methods=["GET","POST"])
@login_required
def rating(request_id,service_id):
    # Ensure that only the customer who created the request can cancel it
    service_request = ServiceRequest.query.get_or_404(request_id)
    if service_request.customer_id != current_user.id:
        flash("You are not authorized to cancel this service request.", "error")
    if request.method == "POST":
        
        # rating = request.form["rating"]
        remarks = request.form["remarks"]
        # service_request.rating = int(rating)
        service_request.remarks = remarks
        service_request.service_status = "closed"
        # services = Service.query.all()
        db.session.commit()
        return redirect(url_for("customer_dashboard"))
    service=Service.query.filter_by(id=service_id).all()
    service_requests = ServiceRequest.query.filter_by(id = request_id).all()
    return render_template("rating.html", user=current_user, request_id=request_id,service_id=service_id,service_request=service_requests)

@app.route("/customer/search" , methods = ["GET","POST"])
@login_required
def csearch():
    if request.method == 'POST':
        return redirect('request_service')
    
    return render_template("customer_search.html")

@app.route("/customer/summary" )
@login_required
def summary():
    requested=10
    closed=5
    signed=2
    return render_template("customer_summary.html",requested=requested, closed=closed, signed=signed)

@app.route('/professional/dashboard/<int:service_id>')
@login_required
def professional_dashboard(service_id):
    if current_user.role != "professional":
        return redirect(url_for("customer_login"))
    
    # View only requests assigned to this professional

    customer=User.query.filter_by().all()

    closed_request= ServiceRequest.query.filter(
    and_(
        ServiceRequest.service_id == service_id,
        or_(
        ServiceRequest.service_status == "rejected",
        ServiceRequest.service_status == "completed" 
        )
    )
).all()

    open_request= ServiceRequest.query.filter(
    and_(
        ServiceRequest.service_id == service_id,
        or_(
        ServiceRequest.service_status == "requested",
        ServiceRequest.service_status == "assigned" 
        )
    )
).all()

    service_requests = ServiceRequest.query.filter_by(service_id=service_id).all()
    return render_template("professional_dashboard.html",open_request=open_request,closed_request=closed_request, service_id=service_id, customer=customer, service_requests=service_requests)



@app.route("/professional/accept_request/<int:request_id>/<int:service_id>", methods=["POST"])
@login_required
def accept_request(request_id, service_id):
    if current_user.role != "professional":
        return redirect(url_for("customer_login"))
    
    service_request = ServiceRequest.query.get(request_id)
    if service_request and service_request.service_status == "requested":
        service_request.professional_id = current_user.id
        service_request.service_status = "assigned"
        db.session.commit()
    return redirect(url_for("professional_dashboard",service_id=service_id ))

@app.route("/professional/reject_request/<int:request_id>/<int:service_id>", methods=["POST"])
@login_required
def reject_request(request_id,service_id):
    if current_user.role != "professional":
        return redirect(url_for("customer_login"))
    
    service_request = ServiceRequest.query.get(request_id)
    if service_request and service_request.service_status == "requested":
        service_request.service_status = "rejected"
        db.session.commit()
    return redirect(url_for("professional_dashboard",service_id=service_id))

    
@app.route("/professional/complete_request/<int:request_id>/<int:service_id>", methods=["POST"])
@login_required
def complete_request(request_id,service_id):
    if current_user.role != "professional":
        return redirect(url_for("customer_login"))
    
    service_request = ServiceRequest.query.get(request_id)
    if service_request and service_request.service_status == "assigned" and service_request.professional_id == current_user.id:
        service_request.service_status = "completed"
        db.session.commit()
    return redirect(url_for("professional_dashboard",service_id=service_id))

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return redirect(url_for("customer_login"))
    users = User.query.all()
    services = Service.query.all()
    service_requests = ServiceRequest.query.all()
    return render_template("admin_dash.html", users=users, services=services, service_requests=service_requests)

@app.route("/admin/search")
@login_required
def adsearch():
    if current_user.role != "admin":
        return redirect(url_for("customer_login"))
    users = User.query.all()
    services = Service.query.all()
    return render_template("admin_search.html", users=users, services=services)

@app.route("/admin/summary")
@login_required
def adsummary():
    if current_user.role != "admin":
        return redirect(url_for("customer_login"))
    users = User.query.all()
    services = Service.query.all()
    return render_template("admin_summary.html", users=users, services=services)


@app.route("/admin/service/new", methods=["GET", "POST"])
@login_required
def new_service():
    if current_user.role != "admin":
        return redirect(url_for("customer_login"))
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        time_required = request.form["time_required"]
        description = request.form["description"]
        new_service = Service(name=name, price=price, time_required=time_required, description=description)
        db.session.add(new_service)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))
    return render_template("new_service.html")



@app.route('/profile', methods=['POST','GET'])
def profile():
        return render_template ('profile.html' , user=current_user)



if __name__ == '__main__':
    app.run(debug=True)
