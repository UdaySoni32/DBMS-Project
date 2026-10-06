import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import sqlite3
from database import connect, initialize_database

NAVY = '#10233F'; BLUE = '#2563EB'; BG = '#F3F6FB'; CARD = '#FFFFFF'; TEXT = '#172B4D'; MUTED = '#66758B'; GREEN = '#16845B'; ORANGE = '#C76B16'

MODULES = {
 'Wardens': ('warden', ['warden_id','name','phone'], ['Name','Phone'], 'warden_id'),
 'Hostels': ('hostel', ['hostel_id','hostel_name','hostel_type','warden_id'], ['Hostel name','Type (Boys/Girls)','Warden ID'], 'hostel_id'),
 'Rooms': ('room', ['room_id','hostel_id','room_no','capacity','room_type','status'], ['Hostel ID','Room no.','Capacity','Room type','Status'], 'room_id'),
 'Students': ('student', ['student_id','roll_no','name','gender','phone','email','department','year'], ['Roll no.','Name','Gender','Phone','Email','Department','Year'], 'student_id'),
 'Allocations': ('allocation', ['allocation_id','student_id','room_id','allocation_date','vacate_date'], ['Student ID','Room ID','Allocation date','Vacate date'], 'allocation_id'),
 'Payments': ('payment', ['payment_id','student_id','amount','payment_date','mode','status'], ['Student ID','Amount (₹)','Payment date','Mode','Status'], 'payment_id'),
 'Service Requests': ('service_request', ['request_id','student_id','service_type','description','request_date','status'], ['Student ID','Service type','Description','Request date','Status'], 'request_id'),
}
QUERIES = [
 ('Students and rooms', """SELECT s.name AS Student, h.hostel_name AS Hostel, r.room_no AS Room
FROM student s JOIN allocation a ON s.student_id=a.student_id
JOIN room r ON a.room_id=r.room_id JOIN hostel h ON r.hostel_id=h.hostel_id
WHERE a.vacate_date IS NULL ORDER BY h.hostel_name,r.room_no"""),
 ('Hostel occupancy', """SELECT h.hostel_name AS Hostel, COUNT(a.allocation_id) AS Occupied,
SUM(r.capacity) AS Beds, ROUND(100.0*COUNT(a.allocation_id)/SUM(r.capacity),1) AS 'Occupancy %'
FROM hostel h JOIN room r ON h.hostel_id=r.hostel_id
LEFT JOIN allocation a ON r.room_id=a.room_id AND a.vacate_date IS NULL
GROUP BY h.hostel_id ORDER BY h.hostel_name"""),
 ('Payments by student', """SELECT s.name AS Student, COALESCE(SUM(CASE WHEN p.status='Paid' THEN p.amount ELSE 0 END),0) AS 'Paid (₹)'
FROM student s LEFT JOIN payment p ON s.student_id=p.student_id GROUP BY s.student_id ORDER BY s.name"""),
 ('Rooms with vacancy', """SELECT h.hostel_name AS Hostel,r.room_no AS Room,r.capacity AS Capacity,
COUNT(a.allocation_id) AS Occupied,r.capacity-COUNT(a.allocation_id) AS Vacant
FROM room r JOIN hostel h ON r.hostel_id=h.hostel_id
LEFT JOIN allocation a ON r.room_id=a.room_id AND a.vacate_date IS NULL
GROUP BY r.room_id HAVING COUNT(a.allocation_id)<r.capacity ORDER BY h.hostel_name,r.room_no"""),
 ('Open service requests', """SELECT s.name AS Student,sr.service_type AS Service,sr.description AS Details,
sr.request_date AS 'Opened',sr.status AS Status FROM service_request sr
JOIN student s ON sr.student_id=s.student_id WHERE sr.status<>'Resolved' ORDER BY sr.request_date"""),
 ('Payment summary', """SELECT ROUND(AVG(amount),2) AS Average,MAX(amount) AS Maximum,MIN(amount) AS Minimum,
SUM(CASE WHEN status='Paid' THEN amount ELSE 0 END) AS 'Collected (₹)' FROM payment"""),
]

class HostelApp(tk.Tk):
    def __init__(self):
        super().__init__(); initialize_database()
        self.title('HostelFlow | Accommodation & Student Services'); self.geometry('1360x860'); self.minsize(1120,740); self.configure(bg=BG)
        self.current='Dashboard'; self.search_var=tk.StringVar(); self._style(); self._shell(); self.show_dashboard()
    def _style(self):
        s=ttk.Style(self); s.theme_use('clam'); s.configure('Treeview',background='white',fieldbackground='white',foreground=TEXT,rowheight=34,borderwidth=0,font=('Segoe UI',10)); s.configure('Treeview.Heading',background='#EAF0F8',foreground=TEXT,font=('Segoe UI Semibold',9),relief='flat'); s.map('Treeview',background=[('selected','#DBEAFE')],foreground=[('selected',TEXT)])
        s.configure('TCombobox',padding=7)
    def _shell(self):
        self.sidebar=tk.Frame(self,bg=NAVY,width=235); self.sidebar.pack(side='left',fill='y'); self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar,text='HOSTELFLOW',bg=NAVY,fg='white',font=('Segoe UI',18,'bold')).pack(anchor='w',padx=24,pady=(26,2)); tk.Label(self.sidebar,text='ACCOMMODATION & SERVICES',bg=NAVY,fg='#9FB2CC',font=('Segoe UI',8,'bold')).pack(anchor='w',padx=25,pady=(0,30))
        tk.Label(self.sidebar,text='WORKSPACE',bg=NAVY,fg='#8296B3',font=('Segoe UI',8,'bold')).pack(anchor='w',padx=24,pady=(0,8))
        self.nav={}; self._nav_button('Dashboard','⌂')
        for n in MODULES: self._nav_button(n,'•')
        self._nav_button('Reports','▤')
        tk.Frame(self.sidebar,bg='#31445F',height=1).pack(fill='x',padx=22,pady=18)
        tk.Label(self.sidebar,text='Warden workspace',bg=NAVY,fg='white',font=('Segoe UI',10,'bold')).pack(anchor='w',padx=24)
        tk.Label(self.sidebar,text='Woxsen University  ·  2026–27',bg=NAVY,fg='#9FB2CC',font=('Segoe UI',9)).pack(anchor='w',padx=24,pady=(5,18))
        self.main=tk.Frame(self,bg=BG); self.main.pack(side='left',fill='both',expand=True)
    def _nav_button(self,name,icon):
        b=tk.Button(self.sidebar,text=f'  {icon}   {name}',anchor='w',bg=NAVY,fg='#D5DFED',activebackground='#263A58',activeforeground='white',relief='flat',bd=0,font=('Segoe UI',10),padx=18,pady=11,command=lambda:self.navigate(name)); b.pack(fill='x',padx=10,pady=1); self.nav[name]=b
    def navigate(self,name):
        self.current=name
        for n,b in self.nav.items(): b.configure(bg='#263A58' if n==name else NAVY,fg='white' if n==name else '#D5DFED')
        if name=='Dashboard': self.show_dashboard()
        elif name=='Reports': self.show_reports()
        else: self.show_module(name)
    def clear(self):
        for w in self.main.winfo_children(): w.destroy()
    def heading(self,title,subtitle):
        bar=tk.Frame(self.main,bg=BG); bar.pack(fill='x',padx=34,pady=(27,18)); tk.Label(bar,text=title,bg=BG,fg=TEXT,font=('Segoe UI',23,'bold')).pack(anchor='w'); tk.Label(bar,text=subtitle,bg=BG,fg=MUTED,font=('Segoe UI',10)).pack(anchor='w',pady=(4,0))
    def card(self,parent,label,value,accent=BLUE,sub=''):
        f=tk.Frame(parent,bg=CARD,highlightbackground='#E2E9F2',highlightthickness=1); f.pack(side='left',fill='both',expand=True,padx=(0,14)); tk.Frame(f,bg=accent,height=4).pack(fill='x'); tk.Label(f,text=label.upper(),bg=CARD,fg=MUTED,font=('Segoe UI',9,'bold')).pack(anchor='w',padx=18,pady=(15,3)); tk.Label(f,text=value,bg=CARD,fg=TEXT,font=('Segoe UI',23,'bold')).pack(anchor='w',padx=18); tk.Label(f,text=sub,bg=CARD,fg=MUTED,font=('Segoe UI',9)).pack(anchor='w',padx=18,pady=(3,16)); return f
    def show_dashboard(self):
        self.clear(); self.heading('Good morning, Warden','Here is the current picture across your hostel community.')
        con=connect(); students=con.execute('select count(*) from student').fetchone()[0]; rooms=con.execute('select count(*) from room').fetchone()[0]; beds=con.execute('select sum(capacity) from room').fetchone()[0] or 0; occupied=con.execute('select count(*) from allocation where vacate_date is null').fetchone()[0]; due=con.execute("select count(*) from payment where status in ('Pending','Overdue')").fetchone()[0]; openreq=con.execute("select count(*) from service_request where status<>'Resolved'").fetchone()[0]; collect=con.execute("select coalesce(sum(amount),0) from payment where status='Paid'").fetchone()[0]; con.close()
        row=tk.Frame(self.main,bg=BG); row.pack(fill='x',padx=34,pady=(2,20)); self.card(row,'Students',str(students),BLUE,'Active student records'); self.card(row,'Bed occupancy',f'{occupied} / {beds}',GREEN,f'{round(occupied*100/beds) if beds else 0}% of total capacity'); self.card(row,'Fees collected',f'₹{collect:,.0f}',ORANGE,'Recorded payments marked paid'); self.card(row,'Needs attention',str(due+openreq),'#B95454',f'{due} payment dues · {openreq} open requests')
        lower=tk.Frame(self.main,bg=BG); lower.pack(fill='both',expand=True,padx=34,pady=(0,28)); left=tk.Frame(lower,bg=CARD,highlightbackground='#E2E9F2',highlightthickness=1); left.pack(side='left',fill='both',expand=True,padx=(0,14)); right=tk.Frame(lower,bg=CARD,highlightbackground='#E2E9F2',highlightthickness=1,width=275); right.pack(side='left',fill='y'); tk.Label(left,text='Recent service requests',bg=CARD,fg=TEXT,font=('Segoe UI',13,'bold')).pack(anchor='w',padx=20,pady=(18,10)); self.make_tree(['Student','Service','Request','Date','Status'],[130,120,300,100,100],pack=True,parent=left)
        tr=left.winfo_children()[-1].winfo_children()[0]; con=connect(); rows=con.execute("select s.name,sr.service_type,sr.description,sr.request_date,sr.status from service_request sr join student s on s.student_id=sr.student_id order by sr.request_date desc limit 6").fetchall(); con.close(); [tr.insert('','end',values=list(r)) for r in rows]
        tk.Label(right,text='Quick actions',bg=CARD,fg=TEXT,font=('Segoe UI',13,'bold')).pack(anchor='w',padx=18,pady=(18,6)); tk.Label(right,text='Jump to common tasks.',bg=CARD,fg=MUTED,font=('Segoe UI',9),wraplength=230,justify='left').pack(anchor='w',padx=18,pady=(0,12))
        for label,dest in [('Add a student','Students'),('Create allocation','Allocations'),('Record payment','Payments'),('Review requests','Service Requests'),('Open reports','Reports')]: tk.Button(right,text=label,anchor='w',bg='#F4F7FC',fg=TEXT,relief='flat',font=('Segoe UI',10),padx=12,pady=10,command=lambda d=dest:self.navigate(d)).pack(fill='x',padx=16,pady=4)
    def make_tree(self,cols,widths,pack=False,parent=None):
        parent=parent or self.main; wrap=tk.Frame(parent,bg=CARD); tv=ttk.Treeview(wrap,columns=cols,show='headings',selectmode='browse'); vs=ttk.Scrollbar(wrap,orient='vertical',command=tv.yview); hs=ttk.Scrollbar(wrap,orient='horizontal',command=tv.xview); tv.configure(yscrollcommand=vs.set,xscrollcommand=hs.set)
        for c,w in zip(cols,widths): tv.heading(c,text=c); tv.column(c,width=w,minwidth=75,anchor='w')
        tv.grid(row=0,column=0,sticky='nsew'); vs.grid(row=0,column=1,sticky='ns'); hs.grid(row=1,column=0,sticky='ew'); wrap.rowconfigure(0,weight=1); wrap.columnconfigure(0,weight=1)
        tv.wrap=wrap
        if pack: wrap.pack(fill='both',expand=True,padx=16,pady=(0,16))
        return tv
    def show_module(self,name):
        self.clear(); table,fields,labels,key=MODULES[name]; self.heading(name,f'Manage {name.lower()} records with live database updates.')
        toolbar=tk.Frame(self.main,bg=BG); toolbar.pack(fill='x',padx=34,pady=(0,14));
        tk.Label(toolbar,text='⌕',bg=BG,fg=MUTED,font=('Segoe UI',15)).pack(side='left'); ent=ttk.Entry(toolbar,textvariable=self.search_var,width=35); ent.pack(side='left',ipady=6,padx=(4,8)); ent.bind('<KeyRelease>',lambda e:self.load_table(table,fields,self.tree,self.search_var.get()))
        tk.Button(toolbar,text='+  Add record',bg=BLUE,fg='white',activebackground='#1D4ED8',relief='flat',font=('Segoe UI',10,'bold'),padx=15,pady=9,command=lambda:self.record_form(name)).pack(side='right',padx=(8,0)); tk.Button(toolbar,text='Edit selected',bg='white',fg=TEXT,relief='flat',font=('Segoe UI',10),padx=13,pady=9,command=lambda:self.edit_selected(name)).pack(side='right',padx=5); tk.Button(toolbar,text='Delete selected',bg='white',fg='#B23B3B',relief='flat',font=('Segoe UI',10),padx=13,pady=9,command=lambda:self.delete_selected(name)).pack(side='right',padx=5); tk.Button(toolbar,text='Refresh',bg='white',fg=TEXT,relief='flat',font=('Segoe UI',10),padx=13,pady=9,command=lambda:self.load_table(table,fields,self.tree)).pack(side='right',padx=5)
        width_map={'student_id':85,'roll_no':140,'name':180,'gender':90,'phone':130,'email':230,'department':140,'year':70,'description':350,'allocation_date':130,'vacate_date':130,'service_type':150,'request_date':130,'payment_date':130,'amount':130,'hostel_name':180,'room_no':110,'capacity':100,'room_type':140,'status':130,'warden_id':100,'hostel_id':100,'student_id':100,'room_id':100,'mode':130}
        widths=[width_map.get(f,125) for f in fields]
        self.tree=self.make_tree(fields,widths,pack=True,parent=self.main); self.tree.wrap.pack(fill='both',expand=True,padx=34,pady=(0,28)); self.tree.bind('<Double-1>',lambda e:self.edit_selected(name)); self.search_var.set(''); self.load_table(table,fields,self.tree)
    def load_table(self,table,fields,tree,search=''):
        tree.delete(*tree.get_children()); con=connect(); rows=con.execute(f"SELECT {','.join(fields)} FROM {table} ORDER BY {fields[0]} DESC").fetchall(); con.close()
        for r in rows:
            values=list(r)
            if search and not any(search.lower() in str(v).lower() for v in values): continue
            tree.insert('','end',values=values)
    def form_fields(self,name):
        _,fields,labels,key=MODULES[name]; return fields[1:],labels
    def record_form(self,name,existing=None):
        table,fields,labels,key=MODULES[name]; cols,labels=self.form_fields(name); win=tk.Toplevel(self); win.title(('Edit ' if existing else 'Add ')+name[:-1] if name.endswith('s') else name); win.configure(bg='white'); win.transient(self); win.grab_set(); win.resizable(False,False)
        tk.Label(win,text=('Edit ' if existing else 'New ')+name.rstrip('s'),bg='white',fg=TEXT,font=('Segoe UI',17,'bold')).grid(row=0,column=0,columnspan=2,sticky='w',padx=24,pady=(20,14)); widgets={}; con=connect()
        for i,(field,label) in enumerate(zip(cols,labels),1):
            tk.Label(win,text=label,bg='white',fg=MUTED,font=('Segoe UI',9,'bold')).grid(row=i,column=0,sticky='w',padx=24,pady=6)
            options={'gender':['Male','Female','Other'],'hostel_type':['Boys','Girls'],'status':(['Available','Maintenance'] if name=='Rooms' else ['Paid','Pending','Overdue'] if name=='Payments' else ['Pending','In Progress','Resolved'] if name=='Service Requests' else []),'mode':['UPI','Card','Cash','Bank Transfer'],'room_type':['Single','Double','Triple','Dormitory']}
            if field in ('warden_id','hostel_id','student_id','room_id'):
                parent={'warden_id':'warden','hostel_id':'hostel','student_id':'student','room_id':'room'}[field]; vals=[str(x[0]) for x in con.execute(f'SELECT {parent[:-1] if parent.endswith("s") else parent}_id FROM {parent}').fetchall()] if parent in ('warden','hostel','student','room') else []
                ent=ttk.Combobox(win,values=vals,width=34)
            elif field in options and options[field]: ent=ttk.Combobox(win,values=options[field],width=34)
            else: ent=ttk.Entry(win,width=37)
            ent.grid(row=i,column=1,padx=(5,24),pady=6,ipady=4); widgets[field]=ent
            if existing is not None:
                val=existing[fields.index(field)]
                if isinstance(ent,ttk.Combobox): ent.set('' if val is None else str(val))
                else: ent.insert(0,'' if val is None else str(val))
            elif field in ('allocation_date','payment_date','request_date'): ent.insert(0,date.today().isoformat())
            elif field=='vacate_date': ent.insert(0,'')
            elif field=='gender': ent.set('Male')
            elif field=='hostel_type': ent.set('Boys')
            elif field=='status': ent.set('Available' if name=='Rooms' else 'Paid' if name=='Payments' else 'Pending')
            elif field=='mode': ent.set('UPI')
            elif field=='room_type': ent.set('Double')
        con.close()
        def save():
            vals=[widgets[f].get().strip() for f in cols]
            if any(v=='' for f,v in zip(cols,vals) if f not in ('phone','email','vacate_date','warden_id')):
                messagebox.showerror('Missing information','Complete all required fields.',parent=win); return
            try:
                con=connect()
                if name=='Allocations' and existing is None:
                    con.close(); self.allocate(int(vals[0]),int(vals[1]),vals[2])
                else:
                    if name=='Allocations' and existing is not None and not vals[3]:
                        active=con.execute('SELECT 1 FROM allocation WHERE student_id=? AND vacate_date IS NULL AND allocation_id<>?',(vals[0],existing[0])).fetchone()
                        room=con.execute('SELECT capacity FROM room WHERE room_id=?',(vals[1],)).fetchone()
                        occupied=con.execute('SELECT COUNT(*) FROM allocation WHERE room_id=? AND vacate_date IS NULL AND allocation_id<>?',(vals[1],existing[0])).fetchone()[0]
                        if active: raise ValueError('Student already has an active allocation.')
                        if room is None: raise ValueError('Room does not exist.')
                        if occupied>=room[0]: raise ValueError('Room is at capacity.')
                    if existing is None:
                        con.execute(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})",vals)
                    else:
                        con.execute(f"UPDATE {table} SET {','.join(f'{f}=?' for f in cols)} WHERE {key}=?",vals+[existing[0]])
                    con.commit(); con.close()
                win.destroy(); self.load_table(table,fields,self.tree); messagebox.showinfo('Saved','Record saved successfully.',parent=self)
            except (sqlite3.IntegrityError,sqlite3.OperationalError,ValueError) as e:
                messagebox.showerror('Could not save',str(e),parent=win)
        tk.Button(win,text='Save changes' if existing else 'Add record',bg=BLUE,fg='white',relief='flat',font=('Segoe UI',10,'bold'),padx=16,pady=9,command=save).grid(row=len(cols)+1,column=1,sticky='e',padx=24,pady=(16,20)); tk.Button(win,text='Cancel',bg='white',fg=MUTED,relief='flat',command=win.destroy).grid(row=len(cols)+1,column=0,sticky='w',padx=24,pady=(16,20)); return win,widgets
    def selected_row(self,name):
        item=self.tree.focus()
        if not item: messagebox.showinfo('Select a record','Choose a row first.',parent=self); return None
        return self.tree.item(item,'values')
    def edit_selected(self,name):
        row=self.selected_row(name)
        if row: return self.record_form(name,row)
    def delete_selected(self,name):
        row=self.selected_row(name)
        if not row:return
        table,fields,labels,key=MODULES[name]
        if not messagebox.askyesno('Delete record',f"Delete {key} {row[0]}?",parent=self): return
        try:
            con=connect(); con.execute(f'DELETE FROM {table} WHERE {key}=?',(row[0],)); con.commit(); con.close(); self.load_table(table,fields,self.tree)
        except sqlite3.IntegrityError as e: messagebox.showerror('Delete blocked',str(e),parent=self)
    def allocate(self,student_id,room_id,when):
        con=connect(); active=con.execute('SELECT 1 FROM allocation WHERE student_id=? AND vacate_date IS NULL',(student_id,)).fetchone(); room=con.execute('SELECT capacity FROM room WHERE room_id=?',(room_id,)).fetchone(); occupied=con.execute('SELECT COUNT(*) FROM allocation WHERE room_id=? AND vacate_date IS NULL',(room_id,)).fetchone()[0]
        if not room: con.close(); raise ValueError('Room does not exist.')
        if active: con.close(); raise ValueError('Student already has an active allocation.')
        if occupied>=room[0]: con.close(); raise ValueError('Room is at capacity.')
        con.execute('INSERT INTO allocation(student_id,room_id,allocation_date) VALUES(?,?,?)',(student_id,room_id,when)); con.commit(); con.close()
    def show_reports(self):
        self.clear(); self.heading('Query reports','Six saved SQL views use joins, grouping, aggregates and vacancy filtering.')
        top=tk.Frame(self.main,bg=BG); top.pack(fill='x',padx=34,pady=(0,12)); self.report_var=tk.StringVar(value=QUERIES[0][0]); cb=ttk.Combobox(top,textvariable=self.report_var,values=[q[0] for q in QUERIES],state='readonly',width=32); cb.pack(side='left',ipady=5); cb.bind('<<ComboboxSelected>>',lambda e:self.run_report())
        tk.Button(top,text='Run query',bg=BLUE,fg='white',relief='flat',font=('Segoe UI',10,'bold'),padx=16,pady=9,command=self.run_report).pack(side='left',padx=9)
        panel=tk.Frame(self.main,bg=CARD,highlightbackground='#E2E9F2',highlightthickness=1); panel.pack(fill='both',expand=True,padx=34,pady=(0,24)); self.query_text=tk.Text(panel,height=5,bg='#F7F9FC',fg='#42536A',font=('Consolas',9),relief='flat',wrap='word',padx=15,pady=12); self.query_text.pack(fill='x',padx=14,pady=(14,8)); self.report_tree=self.make_tree([],[],pack=True,parent=panel); self.report_tree.wrap.pack(fill='both',expand=True,padx=14,pady=(0,14)); self.run_report()
    def run_report(self):
        title=self.report_var.get(); sql=next(q[1] for q in QUERIES if q[0]==title); self.query_text.delete('1.0','end'); self.query_text.insert('1.0',sql)
        con=connect(); rows=con.execute(sql).fetchall(); con.close(); cols=list(rows[0].keys()) if rows else []
        self.report_tree.wrap.destroy(); self.report_tree=self.make_tree(cols,[180]*len(cols),pack=True,parent=self.query_text.master); self.report_tree.wrap.pack(fill='both',expand=True,padx=14,pady=(0,14))
        for r in rows:self.report_tree.insert('','end',values=list(r))

if __name__=='__main__': HostelApp().mainloop()


