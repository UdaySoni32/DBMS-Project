"""Capture the actual Tk interface for the report and leave the sample DB clean."""
import subprocess
from pathlib import Path
from app import HostelApp
from database import connect

ROOT=Path(__file__).parent
SHOTS=ROOT/'screenshots'
TITLE='HostelFlow | Accommodation & Student Services'
app=HostelApp(); app.state('zoomed')
SHOTS.mkdir(exist_ok=True)
steps=[]

def add_step(filename, prepare): steps.append((filename,prepare))
def no_op(): pass
def show_students_before(): app.navigate('Students')
def insert_demo_student():
    con=connect(); con.execute("INSERT INTO student(roll_no,name,gender,phone,email,department,year) VALUES(?,?,?,?,?,?,?)",('26DEMO0001','Demo Test Student','Male','9000000099','demo.student@woxsen.edu.in','CSE',1)); con.commit(); con.close()
    app.load_table('student',['student_id','roll_no','name','gender','phone','email','department','year'],app.tree)
def remove_demo_student():
    con=connect(); con.execute("DELETE FROM student WHERE roll_no='26DEMO0001'"); con.commit(); con.close()
def show_query(title):
    app.navigate('Reports'); app.report_var.set(title); app.run_report()

add_step('dashboard.png',app.show_dashboard)
add_step('students_before_add.png',show_students_before)
add_step('students_after_add.png',insert_demo_student)
add_step('rooms.png',lambda:app.navigate('Rooms'))
add_step('allocations.png',lambda:app.navigate('Allocations'))
add_step('payments.png',lambda:app.navigate('Payments'))
add_step('service_requests.png',lambda:app.navigate('Service Requests'))
add_step('query_occupancy.png',lambda:show_query('Hostel occupancy'))
add_step('query_open_requests.png',lambda:show_query('Open service requests'))

def start_step(index=0):
    if index>=len(steps):
        remove_demo_student(); app.destroy(); return
    filename,prepare=steps[index]
    prepare(); app.update_idletasks()
    out=SHOTS/filename
    command=['powershell','-NoProfile','-WindowStyle','Hidden','-ExecutionPolicy','Bypass','-File',str(ROOT/'capture_window.ps1'),'-Title',TITLE,'-OutFile',str(out)]
    process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    def poll():
        result=process.poll()
        if result is None:
            app.after(100,poll); return
        if result:
            error=process.stderr.read().decode(errors='replace')
            (ROOT/'capture_error.txt').write_text(error,encoding='utf-8')
            app.destroy(); raise RuntimeError(error)
        print(f'Captured {filename}: {out.stat().st_size} bytes',flush=True)
        app.after(180,start_step,index+1)
    app.after(150,poll)

app.after(800,start_step)
app.mainloop()
