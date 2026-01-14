from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from auth.routes import auth_bp
from models import User, Vehicle

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = "supersecretkey"  # Needed for sessions

    db.init_app(app)
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.drop_all()  # reset DB for development
        db.create_all()

    # ---------- PAGES ----------

    # Login page
    @app.route("/")
    def login_page():
        return render_template("login.html")

    # Register page
    @app.route("/register")
    def register_page():
        return render_template("register.html")

    # ---------- FORM LOGIN ----------
    @app.route("/login", methods=["POST"])
    def login_form():
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password", "danger")
            return redirect("/")

        # Store info in session
        session["user_id"] = user.id
        session["role"] = user.role

        if user.role == "admin":
            return redirect("/admin")
        else:
            return redirect("/user")

    # ---------- LOGOUT ----------
    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/")

    # ---------- ADMIN DASHBOARD ----------
    @app.route("/admin")
    def admin_dashboard():
        if session.get("role") != "admin":
            return redirect("/")
        users = User.query.filter_by(role="user").all()
        vehicles = Vehicle.query.all()
        return render_template("admin_dashboard.html", users=users, vehicles=vehicles)

    # Add vehicle
    @app.route("/admin/add_vehicle", methods=["POST"])
    def add_vehicle():
        if session.get("role") != "admin":
            return redirect("/")

        name = request.form["name"]
        number = request.form["number"]
        vehicle = Vehicle(name=name, number=number)
        db.session.add(vehicle)
        db.session.commit()
        flash("Vehicle created successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    # Edit vehicle
    @app.route("/admin/edit_vehicle/<int:vehicle_id>", methods=["POST"])
    def edit_vehicle(vehicle_id):
        if session.get("role") != "admin":
            return redirect("/")
        vehicle = Vehicle.query.get(vehicle_id)
        vehicle.name = request.form["name"]
        vehicle.number = request.form["number"]
        db.session.commit()
        flash("Vehicle updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    # Delete vehicle
    @app.route("/admin/delete_vehicle/<int:vehicle_id>", methods=["POST"])
    def delete_vehicle(vehicle_id):
        if session.get("role") != "admin":
            return redirect("/")
        vehicle = Vehicle.query.get(vehicle_id)
        db.session.delete(vehicle)
        db.session.commit()
        flash("Vehicle deleted successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    # Assign vehicle
    @app.route("/admin/assign_vehicle", methods=["POST"])
    def assign_vehicle():
        if session.get("role") != "admin":
            return redirect("/")
        vehicle_id = request.form["vehicle_id"]
        user_id = request.form["user_id"]
        vehicle = Vehicle.query.get(vehicle_id)
        vehicle.user_id = user_id
        db.session.commit()
        flash("Vehicle assigned successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    # ---------- USER DASHBOARD ----------
    @app.route("/user")
    def user_dashboard():
        user_id = session.get("user_id")
        if not user_id or session.get("role") != "user":
            return redirect("/")
        user = User.query.get(user_id)
        vehicles = user.vehicles  # only assigned vehicles
        return render_template("user_dashboard.html", vehicles=vehicles)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
