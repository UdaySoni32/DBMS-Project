"""Run the demo's local integration checks with the visible Tk interface hidden."""
import sys, sqlite3
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import app as ui
from app import HostelApp
from database import initialize_database, connect

results=[]
def check(label, condition):
    if not condition: raise AssertionError(label)
    results.append(f'PASS  {label}')

def main():
    initialize_database(reset=True)
    root=HostelApp(); root.withdraw()
    ui.messagebox.showinfo=lambda *a,**k: None
    errors=[]
    ui.messagebox.showerror=lambda title,msg,*a,**k: errors.append((title,str(msg)))
    ui.messagebox.askyesno=lambda *a,**k: True
    con=connect(); counts={t:con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ('warden','hostel','room','student','allocation','payment','service_request')}; con.close()
    check('seed contains five rows in each of the seven tables',all(n==5 for n in counts.values()))

    root.navigate('Students'); form,widgets=root.record_form('Students')
    values={'roll_no':'26DEMO0001','name':'Demo Test Student','gender':'Male','phone':'9000000099','email':'demo.student@woxsen.edu.in','department':'CSE','year':'1'}
    for field,val in values.items():
        if isinstance(widgets[field],ui.ttk.Combobox): widgets[field].set(val)
        else: widgets[field].insert(0,val)
    [w for w in form.winfo_children() if isinstance(w,ui.tk.Button) and w.cget('text')=='Add record'][0].invoke(); root.update()
    con=connect(); row=con.execute("SELECT student_id,name FROM student WHERE roll_no='26DEMO0001'").fetchone(); con.close()
    check('student form inserts and displays a new record',row is not None and any(v[2]=='Demo Test Student' for v in [root.tree.item(i,'values') for i in root.tree.get_children()]))
    iid=next(i for i in root.tree.get_children() if root.tree.item(i,'values')[0]==str(row[0])); root.tree.selection_set(iid); root.tree.focus(iid)
    edit,edit_widgets=root.edit_selected('Students'); edit_widgets['name'].delete(0,'end'); edit_widgets['name'].insert(0,'Demo Updated Student')
    [w for w in edit.winfo_children() if isinstance(w,ui.tk.Button) and w.cget('text')=='Save changes'][0].invoke(); root.update()
    con=connect(); edited=con.execute('SELECT name FROM student WHERE student_id=?',(row[0],)).fetchone()[0]; con.close()
    check('student edit form updates the database record',edited=='Demo Updated Student')
    iid=next(i for i in root.tree.get_children() if root.tree.item(i,'values')[0]==str(row[0])); root.tree.selection_set(iid); root.tree.focus(iid); root.delete_selected('Students'); root.update()
    con=connect(); deleted=con.execute('SELECT COUNT(*) FROM student WHERE student_id=?',(row[0],)).fetchone()[0]; con.close()
    check('delete action removes the selected student',deleted==0)

    con=connect()
    try: con.execute("INSERT INTO student(roll_no,name,gender,department,year) VALUES('25wu0101148','Duplicate','Male','CSE',1)")
    except sqlite3.IntegrityError: duplicate=True
    else: duplicate=False
    try: con.execute("INSERT INTO payment(student_id,amount,payment_date,mode) VALUES(999,100,'2026-10-07','Cash')")
    except sqlite3.IntegrityError: foreign_key=False
    else: foreign_key=True
    try: con.execute("INSERT INTO payment(student_id,amount,payment_date,mode) VALUES(1,-500,'2026-10-07','Cash')")
    except sqlite3.IntegrityError: negative=False
    else: negative=True
    con.rollback(); con.close()
    check('duplicate roll number is rejected by UNIQUE constraint',duplicate)
    check('payment with missing student is rejected by foreign key',not foreign_key)
    check('negative payment is rejected by CHECK constraint',not negative)

    con=connect(); cur=con.cursor()
    cur.execute("INSERT INTO student(roll_no,name,gender,department,year) VALUES('26DEMO0002','Demo Allocation A','Male','CSE',1)"); sid1=cur.lastrowid
    cur.execute("INSERT INTO student(roll_no,name,gender,department,year) VALUES('26DEMO0003','Demo Allocation B','Male','CSE',1)"); sid2=cur.lastrowid; con.commit(); con.close()
    root.allocate(sid1,4,'2026-10-07'); full=False
    try: root.allocate(sid2,4,'2026-10-07')
    except ValueError as e: full='capacity' in str(e).lower()
    duplicate_active=False
    try: root.allocate(sid1,5,'2026-10-07')
    except ValueError as e: duplicate_active='active allocation' in str(e).lower()
    check('allocation refuses a room beyond its capacity',full)
    check('allocation refuses a second active room for one student',duplicate_active)
    con=connect(); con.execute('DELETE FROM student WHERE student_id IN (?,?)',(sid1,sid2)); con.commit(); con.close()

    root.navigate('Reports'); root.report_var.set('Hostel occupancy'); root.run_report(); occupancy=len(root.report_tree.get_children())
    root.report_var.set('Open service requests'); root.run_report(); open_requests=len(root.report_tree.get_children())
    check('occupancy report returns all three hostels',occupancy==3)
    check('open request report returns four unresolved requests',open_requests==4)
    con=connect(); count_before=con.execute('SELECT COUNT(*) FROM student').fetchone()[0]; con.close()
    invalid_form,invalid_widgets=root.record_form('Students')
    [w for w in invalid_form.winfo_children() if isinstance(w,ui.tk.Button) and w.cget('text')=='Add record'][0].invoke()
    con=connect(); count_after=con.execute('SELECT COUNT(*) FROM student').fetchone()[0]; con.close()
    check('empty student form is blocked without changing row count',bool(errors) and count_before==count_after)
    invalid_form.destroy()
    root.destroy()
    for result in results: print(result)
    print(f'\n{len(results)} checks passed.')

if __name__=='__main__': main()

