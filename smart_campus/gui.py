# gui.py
# Tkinter interface (class-based, as in the study guide).
# Page 1: Login / Register   Page 2: Campus selection   Page 3: Role dashboard

import tkinter
import tkinter.messagebox
import database
import models
import rules
import booking

HEADER_COLOUR = '#1f3a5f'


class SmartCampusApp:
    def __init__(self):
        self.main_window = tkinter.Tk()
        self.main_window.title('Smart Campus Resource Booking System')
        self.main_window.geometry('1050x760')

        self.screen = None            # the Frame holding the current page
        self.user = None              # the logged-in User object
        self.active_campus = None     # None means "NONE selected yet"

        self.show_login_page()
        tkinter.mainloop()

    # ------------------------------------------------------------ utilities
    def new_screen(self):
        """Throw away the current page and start an empty one."""
        if self.screen is not None:
            self.screen.destroy()
        self.screen = tkinter.Frame(self.main_window)
        self.screen.pack(fill='both', expand=True)

    def logout(self):
        self.user = None
        self.active_campus = None
        self.show_login_page()

    def selected_index(self, listbox):
        """Index of the selected Listbox row, or -1 if nothing is selected."""
        chosen = listbox.curselection()
        if len(chosen) == 0:
            return -1
        return chosen[0]

    def booking_line(self, row):
        """Turn a booking row into one line of text for a Listbox."""
        (booking_id, resource_id, campus, lecturer, date_text, start_min, duration, status) = row
        return (campus + ' | ' + resource_id + ' | ' + lecturer + ' | ' + date_text + ' '
                + rules.format_slot(start_min, duration) + ' | ' + str(duration) + ' min | ' + status)

    # ------------------------------------------------------- Page 1: login
    def show_login_page(self):
        self.new_screen()
        tkinter.Label(self.screen, text='Smart Campus Resource Booking System',
                      font=('Helvetica', 20, 'bold')).pack(pady=(40, 5))
        tkinter.Label(self.screen, text='Richfield Graduate Institution').pack()
        tkinter.Label(self.screen, text='Currently Active Campus: NONE', fg='gray').pack(pady=10)

        form = tkinter.Frame(self.screen)
        form.pack(pady=15)
        tkinter.Label(form, text='Username:').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.username_entry = tkinter.Entry(form, width=28)
        self.username_entry.grid(row=0, column=1, pady=5)
        tkinter.Label(form, text='Password:').grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.password_entry = tkinter.Entry(form, width=28, show='*')
        self.password_entry.grid(row=1, column=1, pady=5)

        buttons = tkinter.Frame(self.screen)
        buttons.pack(pady=10)
        tkinter.Button(buttons, text='Login', width=12, command=self.login).pack(side='left', padx=5)
        tkinter.Button(buttons, text='Register (Lecturer)', width=18,
                       command=self.show_register_page).pack(side='left', padx=5)
        tkinter.Button(buttons, text='Exit', width=8,
                       command=self.main_window.destroy).pack(side='left', padx=5)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if username == '' or password == '':
            tkinter.messagebox.showerror('Login', 'Please enter your username and password.')
            return
        row = database.get_user_row(username)
        if row is None:
            tkinter.messagebox.showerror('Login Failed', 'Wrong username or password.')
            return
        user = models.make_user(row)
        if not user.check_password(password):
            tkinter.messagebox.showerror('Login Failed', 'Wrong username or password.')
            return
        self.user = user
        self.show_campus_page()

    def show_register_page(self):
        self.new_screen()
        tkinter.Label(self.screen, text='Register a Lecturer Account',
                      font=('Helvetica', 18, 'bold')).pack(pady=(40, 15))
        form = tkinter.Frame(self.screen)
        form.pack()
        tkinter.Label(form, text='Username:').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.reg_username = tkinter.Entry(form, width=28)
        self.reg_username.grid(row=0, column=1, pady=5)
        tkinter.Label(form, text='Password:').grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.reg_password = tkinter.Entry(form, width=28, show='*')
        self.reg_password.grid(row=1, column=1, pady=5)
        tkinter.Label(form, text='Confirm password:').grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.reg_confirm = tkinter.Entry(form, width=28, show='*')
        self.reg_confirm.grid(row=2, column=1, pady=5)
        tkinter.Label(self.screen, text='Username: at least 4 characters, no spaces. Password: at least 6 characters.',
                      fg='gray').pack(pady=5)
        buttons = tkinter.Frame(self.screen)
        buttons.pack(pady=10)
        tkinter.Button(buttons, text='Create Account', command=self.register).pack(side='left', padx=5)
        tkinter.Button(buttons, text='Back to Login', command=self.show_login_page).pack(side='left', padx=5)

    def register(self):
        username = self.reg_username.get().strip()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()
        if len(username) < 4 or ' ' in username:
            tkinter.messagebox.showerror('Register', 'Username must be at least 4 characters with no spaces.')
            return
        if len(password) < 6:
            tkinter.messagebox.showerror('Register', 'Password must be at least 6 characters.')
            return
        if password != confirm:
            tkinter.messagebox.showerror('Register', 'The two passwords do not match.')
            return
        if database.get_user_row(username) is not None:
            tkinter.messagebox.showerror('Register', 'That username is already taken.')
            return
        if database.add_user(username, password, 'Lecturer', ''):
            tkinter.messagebox.showinfo('Register', 'Account created. You can now log in.')
            self.show_login_page()
        else:
            tkinter.messagebox.showerror('Register', 'The account could not be created.')

    # ------------------------------------------------ Page 2: campus select
    def show_campus_page(self):
        self.new_screen()
        self.active_campus = None
        tkinter.Label(self.screen, text=self.user.get_welcome(),
                      font=('Helvetica', 14, 'bold')).pack(pady=(30, 5))
        tkinter.Label(self.screen, text='Select a campus to work with',
                      font=('Helvetica', 18, 'bold')).pack(pady=5)
        self.campus_status = tkinter.Label(self.screen, text='Currently Active Campus: NONE',
                                           font=('Helvetica', 13, 'bold'), fg='darkred')
        self.campus_status.pack(pady=5)
        self.campus_policy = tkinter.Label(self.screen, text='Policy: select a campus to see its rules')
        self.campus_policy.pack(pady=5)

        # build the list of campus choices (a list of strings)
        if self.user.get_role() == 'CampusAdmin':
            self.campus_choices = [self.user.get_campus()]
        elif self.user.get_role() == 'SystemOperator':
            self.campus_choices = [rules.ALL_CAMPUSES] + database.get_campus_names()
        else:
            self.campus_choices = database.get_campus_names()

        self.campus_listbox = tkinter.Listbox(self.screen, height=6, width=36, exportselection=0)
        for name in self.campus_choices:
            self.campus_listbox.insert(tkinter.END, name)
        self.campus_listbox.pack(pady=10)

        if self.user.can_choose_campus():
            self.campus_listbox.bind('<<ListboxSelect>>', self.preview_campus)
        else:
            # Campus administrators are locked to their own campus.
            self.campus_listbox.selection_set(0)
            self.preview_campus(None)
            self.campus_status.configure(text='Active Campus: ' + self.campus_choices[0] + ' (Locked)')
            self.campus_listbox.configure(state='disabled')

        buttons = tkinter.Frame(self.screen)
        buttons.pack(pady=10)
        tkinter.Button(buttons, text='Continue', width=14, command=self.confirm_campus).pack(side='left', padx=5)
        tkinter.Button(buttons, text='Logout', width=10, command=self.logout).pack(side='left', padx=5)

    def preview_campus(self, event):
        """Event handler: show the policy of the campus clicked in the list."""
        index = self.selected_index(self.campus_listbox)
        if index == -1:
            return
        name = self.campus_choices[index]
        if name == rules.ALL_CAMPUSES:
            self.campus_status.configure(text='Active Campus: ALL CAMPUSES - System Wide')
            self.campus_policy.configure(text='Policy: each campus applies its own rules (see reports)')
        else:
            self.campus_status.configure(text='Active Campus: ' + name)
            self.campus_policy.configure(text=rules.policy_text(name))

    def confirm_campus(self):
        if self.user.can_choose_campus():
            index = self.selected_index(self.campus_listbox)
            if index == -1:
                tkinter.messagebox.showwarning('Campus', 'Please select a campus first.')
                return
            self.active_campus = self.campus_choices[index]
        else:
            self.active_campus = self.user.get_campus()

        role = self.user.get_role()
        if role == 'Lecturer':
            self.show_lecturer_dashboard()
        elif role == 'CampusAdmin':
            self.show_admin_dashboard()
        else:
            self.show_operator_dashboard()

    # ------------------------------------------------- shared dashboard header
    def build_header(self):
        header = tkinter.Frame(self.screen, bg=HEADER_COLOUR)
        header.pack(fill='x')
        text_side = tkinter.Frame(header, bg=HEADER_COLOUR)
        text_side.pack(side='left', padx=10, pady=5)

        tkinter.Label(text_side, text=self.user.get_welcome(), bg=HEADER_COLOUR, fg='white',
                      font=('Helvetica', 14, 'bold')).pack(anchor='w')

        if self.active_campus == rules.ALL_CAMPUSES:
            campus_text = 'Active Campus: ALL CAMPUSES - System Wide'
            policy = 'Policy: each campus applies its own rules (see reports)'
        elif self.user.can_choose_campus():
            campus_text = 'Active Campus: ' + self.active_campus
            policy = rules.policy_text(self.active_campus)
        else:
            campus_text = 'Active Campus: ' + self.active_campus + ' (Locked)'
            policy = rules.policy_text(self.active_campus)
        tkinter.Label(text_side, text=campus_text, bg=HEADER_COLOUR, fg='white').pack(anchor='w')
        tkinter.Label(text_side, text=policy, bg=HEADER_COLOUR, fg='#ffd966').pack(anchor='w')

        button_side = tkinter.Frame(header, bg=HEADER_COLOUR)
        button_side.pack(side='right', padx=10)
        if self.user.can_choose_campus():
            tkinter.Button(button_side, text='Change Campus', command=self.show_campus_page).pack(side='left', padx=3)
        tkinter.Button(button_side, text='Logout', command=self.logout).pack(side='left', padx=3)

    # ----------------------------------------------- Page 3a: lecturer
    def show_lecturer_dashboard(self):
        self.new_screen()
        self.build_header()

        top = tkinter.Frame(self.screen)
        top.pack(fill='x', padx=10, pady=10)

        left = tkinter.Frame(top)
        left.pack(side='left', fill='both', expand=True)
        tkinter.Label(left, text='Resources and availability on the chosen date',
                      font=('Helvetica', 11, 'bold')).pack(anchor='w')
        self.resource_listbox = tkinter.Listbox(left, height=11, width=78, exportselection=0)
        self.resource_listbox.pack(anchor='w')

        right = tkinter.Frame(top)
        right.pack(side='right', padx=10)
        tkinter.Label(right, text='Book the selected resource', font=('Helvetica', 11, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 5))
        tkinter.Label(right, text='Date (YYYY-MM-DD):').grid(row=1, column=0, sticky='e', pady=3)
        self.date_entry = tkinter.Entry(right, width=14)
        self.date_entry.insert(0, rules.today_text())
        self.date_entry.grid(row=1, column=1, pady=3)
        tkinter.Label(right, text='Start time (HH:MM):').grid(row=2, column=0, sticky='e', pady=3)
        self.time_entry = tkinter.Entry(right, width=14)
        self.time_entry.insert(0, '09:00')
        self.time_entry.grid(row=2, column=1, pady=3)
        tkinter.Label(right, text='Duration (hours):').grid(row=3, column=0, sticky='e', pady=3)
        self.hours_entry = tkinter.Entry(right, width=14)
        self.hours_entry.insert(0, '1')
        self.hours_entry.grid(row=3, column=1, pady=3)
        tkinter.Button(right, text='Book Resource', width=18, command=self.lecturer_book).grid(
            row=4, column=0, columnspan=2, pady=(10, 3))
        tkinter.Button(right, text='Refresh Availability', width=18,
                       command=self.refresh_resources).grid(row=5, column=0, columnspan=2, pady=3)

        bottom = tkinter.Frame(self.screen)
        bottom.pack(fill='both', expand=True, padx=10)
        tkinter.Label(bottom, text='My bookings', font=('Helvetica', 11, 'bold')).pack(anchor='w')

        # Radio buttons share one IntVar to choose which bookings to show.
        self.filter_var = tkinter.IntVar()
        self.filter_var.set(1)
        radio_row = tkinter.Frame(bottom)
        radio_row.pack(anchor='w')
        choices = [('Active (upcoming)', 1), ('Past history', 2), ('Cancelled', 3), ('All', 4)]
        for (label, value) in choices:
            tkinter.Radiobutton(radio_row, text=label, variable=self.filter_var, value=value,
                                command=self.refresh_my_bookings).pack(side='left', padx=5)

        self.my_listbox = tkinter.Listbox(bottom, height=9, width=110, exportselection=0)
        self.my_listbox.pack(anchor='w', pady=5)
        tkinter.Button(bottom, text='Cancel Selected Booking', command=self.lecturer_cancel).pack(anchor='w')

        self.refresh_resources()
        self.refresh_my_bookings()

    def refresh_resources(self):
        """Rebuild the resource list with live availability for the date typed in."""
        date_text = self.date_entry.get().strip()
        date_ok = rules.valid_date(date_text)
        self.resource_listbox.delete(0, tkinter.END)
        self.resource_ids = []
        now = rules.now_minutes()
        for (rid, name, rtype) in database.get_resources(self.active_campus):
            if not date_ok:
                status = 'Enter a valid date to see availability'
            else:
                slots = database.get_day_bookings(rid, date_text)
                if len(slots) == 0:
                    status = 'Available all day'
                else:
                    parts = []
                    in_use = False
                    for (start_min, duration) in slots:
                        parts.append(rules.format_slot(start_min, duration))
                        if date_text == rules.today_text() and start_min <= now < start_min + duration:
                            in_use = True
                    status = 'Booked: ' + ', '.join(parts)
                    if in_use:
                        status = 'IN USE NOW | ' + status
            self.resource_listbox.insert(tkinter.END, rid + ' | ' + name + ' (' + rtype + ') | ' + status)
            self.resource_ids.append(rid)

    def lecturer_book(self):
        index = self.selected_index(self.resource_listbox)
        if index == -1:
            tkinter.messagebox.showwarning('Booking', 'Please select a resource from the list first.')
            return
        (ok, message) = booking.make_booking(self.user.get_username(), self.active_campus,
                                             self.resource_ids[index],
                                             self.date_entry.get().strip(),
                                             self.time_entry.get().strip(),
                                             self.hours_entry.get().strip())
        if ok:
            tkinter.messagebox.showinfo('Booking Confirmed', message)
        else:
            tkinter.messagebox.showerror('Booking Rejected', message)
        self.refresh_resources()
        self.refresh_my_bookings()

    def refresh_my_bookings(self):
        rows = database.get_lecturer_bookings(self.user.get_username())
        choice = self.filter_var.get()
        self.my_listbox.delete(0, tkinter.END)
        self.my_ids = []          # parallel lists: row position -> booking id / label
        self.my_labels = []
        for row in rows:
            (booking_id, resource_id, campus, date_text, start_min, duration, status) = row
            if status == 'Cancelled':
                label = 'Cancelled'
            elif rules.is_future(date_text, start_min):
                label = 'Active'
            else:
                label = 'Past'
            if choice == 1 and label != 'Active':
                continue
            if choice == 2 and label != 'Past':
                continue
            if choice == 3 and label != 'Cancelled':
                continue
            self.my_listbox.insert(tkinter.END, '#' + str(booking_id) + ' | ' + campus + ' | ' + resource_id
                                   + ' | ' + date_text + ' ' + rules.format_slot(start_min, duration)
                                   + ' | ' + label)
            self.my_ids.append(booking_id)
            self.my_labels.append(label)

    def lecturer_cancel(self):
        index = self.selected_index(self.my_listbox)
        if index == -1:
            tkinter.messagebox.showwarning('Cancel', 'Select a booking to cancel first.')
            return
        if self.my_labels[index] != 'Active':
            tkinter.messagebox.showerror('Cancel', 'Only future, active bookings can be cancelled.')
            return
        if database.cancel_booking(self.my_ids[index]):
            tkinter.messagebox.showinfo('Cancel', 'Booking cancelled.')
        else:
            tkinter.messagebox.showerror('Cancel', 'The booking could not be cancelled.')
        self.refresh_resources()
        self.refresh_my_bookings()

    # ------------------------------------------ Page 3b: campus administrator
    def show_admin_dashboard(self):
        self.new_screen()
        self.build_header()

        top = tkinter.Frame(self.screen)
        top.pack(fill='x', padx=10, pady=10)

        left = tkinter.Frame(top)
        left.pack(side='left', fill='both', expand=True)
        tkinter.Label(left, text='Campus resources', font=('Helvetica', 11, 'bold')).pack(anchor='w')
        self.admin_listbox = tkinter.Listbox(left, height=10, width=70, exportselection=0)
        self.admin_listbox.pack(anchor='w')
        self.admin_listbox.bind('<<ListboxSelect>>', self.admin_fill_form)

        right = tkinter.Frame(top)
        right.pack(side='right', padx=10)
        tkinter.Label(right, text='Add / update / remove', font=('Helvetica', 11, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=(0, 5))
        tkinter.Label(right, text='Resource ID:').grid(row=1, column=0, sticky='e', pady=2)
        self.id_entry = tkinter.Entry(right, width=22)
        self.id_entry.grid(row=1, column=1, pady=2)
        tkinter.Label(right, text='Name:').grid(row=2, column=0, sticky='e', pady=2)
        self.name_entry = tkinter.Entry(right, width=22)
        self.name_entry.grid(row=2, column=1, pady=2)
        tkinter.Label(right, text='Type:').grid(row=3, column=0, sticky='ne', pady=2)
        type_frame = tkinter.Frame(right)
        type_frame.grid(row=3, column=1, sticky='w')
        self.type_var = tkinter.StringVar()
        self.type_var.set(rules.RESOURCE_TYPES[0])
        for rtype in rules.RESOURCE_TYPES:
            tkinter.Radiobutton(type_frame, text=rtype, variable=self.type_var, value=rtype).pack(anchor='w')
        button_row = tkinter.Frame(right)
        button_row.grid(row=4, column=0, columnspan=2, pady=8)
        tkinter.Button(button_row, text='Add', width=7, command=self.admin_add).pack(side='left', padx=2)
        tkinter.Button(button_row, text='Update', width=7, command=self.admin_update).pack(side='left', padx=2)
        tkinter.Button(button_row, text='Remove', width=7, command=self.admin_remove).pack(side='left', padx=2)
        tkinter.Button(button_row, text='Clear', width=7, command=self.admin_clear).pack(side='left', padx=2)

        middle = tkinter.Frame(self.screen)
        middle.pack(fill='x', padx=10)
        tkinter.Label(middle, text='Usage and trends for this campus', font=('Helvetica', 11, 'bold')).pack(anchor='w')
        self.report_listbox = tkinter.Listbox(middle, height=8, width=110, exportselection=0)
        self.report_listbox.pack(anchor='w', pady=(0, 5))

        bottom = tkinter.Frame(self.screen)
        bottom.pack(fill='both', expand=True, padx=10)
        tkinter.Label(bottom, text='All bookings at this campus', font=('Helvetica', 11, 'bold')).pack(anchor='w')
        self.admin_bookings = tkinter.Listbox(bottom, height=8, width=110, exportselection=0)
        self.admin_bookings.pack(anchor='w')

        self.admin_refresh()

    def admin_refresh(self):
        campus = self.active_campus

        # dictionary: resource id -> number of bookings
        usage = {}
        for (rid, uses) in database.resource_usage(campus):
            usage[rid] = uses

        self.admin_listbox.delete(0, tkinter.END)
        self.admin_rows = database.get_resources(campus)       # list of tuples
        now = rules.now_minutes()
        today = rules.today_text()
        in_use_count = 0
        for (rid, name, rtype) in self.admin_rows:
            uses = usage.get(rid, 0)
            status = 'Available now'
            for (start_min, duration) in database.get_day_bookings(rid, today):
                if start_min <= now < start_min + duration:
                    status = 'IN USE NOW'
                    in_use_count += 1
            self.admin_listbox.insert(tkinter.END, rid + ' | ' + name + ' | ' + rtype + ' | '
                                      + str(uses) + ' booking(s) | ' + status)

        (total, average, top) = database.campus_report(campus)
        self.report_listbox.delete(0, tkinter.END)
        self.report_listbox.insert(tkinter.END, 'Total bookings: ' + str(total))
        self.report_listbox.insert(tkinter.END, 'Average booking duration: ' + str(round(average, 1)) + ' minutes')
        if top is None:
            self.report_listbox.insert(tkinter.END, 'Most frequently used resource: none yet')
        else:
            self.report_listbox.insert(tkinter.END, 'Most frequently used resource: ' + top[0]
                                       + ' (' + str(top[1]) + ' bookings)')
        self.report_listbox.insert(tkinter.END, 'Resources in use right now: ' + str(in_use_count)
                                   + ' of ' + str(len(self.admin_rows)))
        self.report_listbox.insert(tkinter.END, 'Bookings per date (usage trend):')
        for (c, date_text, count) in database.booking_trend(campus):
            self.report_listbox.insert(tkinter.END, '    ' + date_text + ': ' + str(count))

        self.admin_bookings.delete(0, tkinter.END)
        for row in database.get_bookings(campus):
            self.admin_bookings.insert(tkinter.END, self.booking_line(row))

    def admin_fill_form(self, event):
        index = self.selected_index(self.admin_listbox)
        if index == -1:
            return
        (rid, name, rtype) = self.admin_rows[index]
        self.id_entry.delete(0, tkinter.END)
        self.id_entry.insert(0, rid)
        self.name_entry.delete(0, tkinter.END)
        self.name_entry.insert(0, name)
        self.type_var.set(rtype)

    def admin_clear(self):
        self.id_entry.delete(0, tkinter.END)
        self.name_entry.delete(0, tkinter.END)
        self.type_var.set(rules.RESOURCE_TYPES[0])
        self.admin_listbox.selection_clear(0, tkinter.END)

    def admin_add(self):
        new_id = self.id_entry.get().strip().upper()
        name = self.name_entry.get().strip()
        if new_id == '' or name == '':
            tkinter.messagebox.showerror('Add Resource', 'Resource ID and name are both required.')
            return
        if ' ' in new_id:
            tkinter.messagebox.showerror('Add Resource', 'The resource ID cannot contain spaces.')
            return
        resource_id_set = database.get_all_resource_ids()      # a set of every existing ID
        if new_id in resource_id_set:
            tkinter.messagebox.showerror('Duplicate Resource', 'A resource with ID ' + new_id + ' already exists.')
            return
        if database.add_resource(new_id, name, self.type_var.get(), self.active_campus):
            tkinter.messagebox.showinfo('Add Resource', new_id + ' added to ' + self.active_campus + '.')
            self.admin_clear()
        else:
            tkinter.messagebox.showerror('Add Resource', 'The resource could not be saved.')
        self.admin_refresh()

    def admin_update(self):
        index = self.selected_index(self.admin_listbox)
        if index == -1:
            tkinter.messagebox.showwarning('Update Resource', 'Select a resource from the list first.')
            return
        rid = self.admin_rows[index][0]
        name = self.name_entry.get().strip()
        if name == '':
            tkinter.messagebox.showerror('Update Resource', 'The name cannot be empty.')
            return
        if self.id_entry.get().strip().upper() != rid:
            tkinter.messagebox.showerror('Update Resource', 'A resource ID cannot be changed. '
                                         'Remove it and add a new one instead.')
            return
        if database.update_resource(rid, name, self.type_var.get()):
            tkinter.messagebox.showinfo('Update Resource', rid + ' updated.')
        else:
            tkinter.messagebox.showerror('Update Resource', 'The resource could not be updated.')
        self.admin_refresh()

    def admin_remove(self):
        index = self.selected_index(self.admin_listbox)
        if index == -1:
            tkinter.messagebox.showwarning('Remove Resource', 'Select a resource from the list first.')
            return
        rid = self.admin_rows[index][0]
        if database.count_future_for_resource(rid, rules.today_text(), rules.now_minutes()) > 0:
            tkinter.messagebox.showerror('Remove Resource', rid + ' still has future bookings. '
                                         'Cancel them before removing it.')
            return
        if database.delete_resource(rid):
            tkinter.messagebox.showinfo('Remove Resource', rid + ' removed.')
            self.admin_clear()
        else:
            tkinter.messagebox.showerror('Remove Resource', 'The resource could not be removed.')
        self.admin_refresh()

    # --------------------------------------------- Page 3c: system operator
    def show_operator_dashboard(self):
        self.new_screen()
        self.build_header()

        buttons = tkinter.Frame(self.screen)
        buttons.pack(fill='x', padx=10, pady=10)
        tkinter.Button(buttons, text='View Bookings', width=20, command=self.operator_bookings).pack(side='left', padx=3)
        tkinter.Button(buttons, text='View Resources', width=20, command=self.operator_resources).pack(side='left', padx=3)
        tkinter.Button(buttons, text='Campus Comparison Report', width=24,
                       command=self.operator_comparison).pack(side='left', padx=3)
        tkinter.Button(buttons, text='Booking Trends', width=20, command=self.operator_trends).pack(side='left', padx=3)

        self.output_title = tkinter.Label(self.screen, text='', font=('Helvetica', 12, 'bold'))
        self.output_title.pack(anchor='w', padx=10)
        self.output_listbox = tkinter.Listbox(self.screen, height=27, width=130, exportselection=0)
        self.output_listbox.pack(anchor='w', padx=10, pady=5)
        self.operator_comparison()

    def operator_scope(self):
        """None means every campus; otherwise the one campus chosen."""
        if self.active_campus == rules.ALL_CAMPUSES:
            return None
        return self.active_campus

    def show_lines(self, title, lines):
        self.output_title.configure(text=title)
        self.output_listbox.delete(0, tkinter.END)
        for line in lines:
            self.output_listbox.insert(tkinter.END, line)

    def operator_bookings(self):
        lines = []
        for row in database.get_bookings(self.operator_scope()):
            lines.append(self.booking_line(row))
        if len(lines) == 0:
            lines.append('No bookings yet.')
        self.show_lines('Bookings - ' + self.active_campus, lines)

    def operator_resources(self):
        lines = []
        for (rid, name, rtype, campus) in database.get_all_resources():
            if self.operator_scope() is None or campus == self.operator_scope():
                lines.append(campus + ' | ' + rid + ' | ' + name + ' | ' + rtype)
        self.show_lines('Resources - ' + self.active_campus, lines)

    def operator_comparison(self):
        lines = []
        for campus in database.get_campus_names():
            if campus not in rules.CAMPUS_RULES:
                continue
            (total, average, top) = database.campus_report(campus)
            limit = rules.CAMPUS_RULES[campus]['max_hours'] * 60
            lines.append(campus.upper())
            lines.append('    ' + rules.policy_text(campus))
            lines.append('    Total bookings: ' + str(total) + ' | Average duration: '
                         + str(round(average, 1)) + ' min (' + str(round(average / limit * 100)) + '% of the '
                         + str(limit) + ' min limit)')
            if top is None:
                lines.append('    Most used resource: none yet')
            else:
                lines.append('    Most used resource: ' + top[0] + ' (' + str(top[1]) + ' bookings)')
            lines.append('    Resource usage:')
            usage = database.resource_usage(campus)
            if len(usage) == 0:
                lines.append('        no bookings yet')
            for (rid, uses) in usage:
                lines.append('        ' + rid + ': ' + str(uses))
            lines.append('')
        self.show_lines('Cross-campus comparison (all campuses)', lines)

    def operator_trends(self):
        lines = []
        for (campus, date_text, count) in database.booking_trend(self.operator_scope()):
            lines.append(campus + ' | ' + date_text + ' | ' + str(count) + ' booking(s)')
        if len(lines) == 0:
            lines.append('No bookings yet.')
        self.show_lines('Booking trends (bookings per campus per date) - ' + self.active_campus, lines)
