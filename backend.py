# Step1: Import Database objects

from database import init_db, Appointment, get_db


init_db()

# Step3: Create Data Contracts using Pydantic Models
import datetime as dt
from pydantic import BaseModel

class AppointmentRequest(BaseModel):
    patient_name: str
    reason: str | None = None  # make it optional
    start_time: dt.datetime

class AppointmentResponse(BaseModel):
    id: int
    patient_name: str
    reason: str | None
    start_time: dt.datetime
    canceled: bool
    created_at: dt.datetime

class CancelAppointmentRequest(BaseModel):
    patient_name: str
    date: dt.date

class CancelAppointmentResponse(BaseModel):
    canceled_count: int

class ListAppointmentRequest(BaseModel):
    date: dt.date

# Step2: Create FastAPI application and endpoints pseudo code

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session


app = FastAPI()

# schedule appt
@app.post("/schedule_appointment/")
def schedule_appointment(request: AppointmentRequest, db: Session = Depends(get_db)):
    new_appointment = Appointment(
            patient_name=request.patient_name,
            reason=request.reason,
            start_time=request.start_time,
        )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    new_appointment_return_obj = AppointmentResponse(
        id = new_appointment.id,
        patient_name= new_appointment.patient_name,
        reason=new_appointment.reason,
        start_time=new_appointment.start_time,
        canceled=new_appointment.canceled,
        created_at=new_appointment.created_at
    )
    return new_appointment_return_obj


# cancel appt
from sqlalchemy import select
@app.post("/cancel_appointment/")
def cancel_appointment(request: CancelAppointmentRequest, db: Session = Depends(get_db)):   
    
    start_dt = dt.datetime.combine(request.date, dt.time.min)
    end_dt = start_dt + dt.timedelta(days=1)

    result = db.execute(
        select(Appointment)
        .where(Appointment.patient_name == request.patient_name)
        .where(Appointment.start_time >= start_dt)
        .where(Appointment.start_time < end_dt)
        .where(Appointment.canceled == False)
    )

    appointments = result.scalars().all()
    if not appointments:
        return HTTPException(status_code=404, detail="No matching appointment for the details found in our system")

    for appointment in appointments:
        appointment.canceled = True
    
    db.commit()
    
    return CancelAppointmentResponse(canceled_count=len(appointments))

# list appt
@app.post("/list_appointments/")
def list_appointments(request: ListAppointmentRequest, db: Session = Depends(get_db)):
    
    start_dt = dt.datetime.combine(request.date, dt.time.min)
    end_dt = start_dt + dt.timedelta(days=1)
    
    result = db.execute(
        select(Appointment)
        .where(Appointment.canceled == False)
        .where(Appointment.start_time >= start_dt)
        .where(Appointment.start_time < end_dt)
        .order_by(Appointment.start_time.asc())
    )
    booked_appointments = []
    for appointment in result.scalars().all():
        appointment_obj = AppointmentResponse(
        id=appointment.id,
        patient_name=appointment.patient_name,
        reason=appointment.reason,
        start_time=appointment.start_time,
        canceled=appointment.canceled,
        created_at=appointment.created_at
    )
        booked_appointments.append(appointment_obj)

    return booked_appointments

import uvicorn
if __name__ == "__main__":
    uvicorn.run("backend:app", host="127.0.0.1", port=4444, reload=True)